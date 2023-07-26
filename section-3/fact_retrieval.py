import argparse
import json
import web3
from web3.exceptions import InvalidAddress
from typing import Dict, List
import os
import logging
from typing import Dict, List
from eth_typing.encoding import HexStr
from web3 import Web3
from web3.contract import Contract

class MemoryPagesFetcher:
    """
    Given a fact hash and using onchain data, retrieves the memory pages that the GPS statement
    verifier outputted for the relevant Cairo job.
    """

    def __init__(
        self,
        web3: Web3,
        memory_page_transactions_map: Dict[int, str],
        fact_memory_pages_map: Dict[bytes, bytes],
        memory_page_fact_registry_contract: Contract,
    ):
        self.web3 = web3
        # Mapping from memory page hash to memory page Ethereum transaction.
        self.memory_page_transactions_map = memory_page_transactions_map
        # Mapping from Cairo job's fact to the Cairo job memory pages list.
        self.fact_memory_pages_map = fact_memory_pages_map
        self.memory_page_fact_registry_contract = memory_page_fact_registry_contract

    @classmethod
    def create(
        cls,
        web3: Web3,
        gps_statement_verifier_contract: Contract,
        memory_page_fact_registry_contract: Contract
    ) -> "MemoryPagesFetcher":
        """
        Creates an initialized instance by reading contract logs from the given web3 provider.
        If is_verifier_proxied is true, then gps_statement_verifier_contract is the proxy contract
        rather than the statement verifier implemantation.
        """
        last_block = web3.eth.block_number
        from_block = last_block - 500

        """
        Fetch all `LogMemoryPageFactContinuous` events from the MemoryPageFactRegistry
        """
        mem_events = []
        mem_events.extend(list(memory_page_fact_registry_contract.events.LogMemoryPageFactContinuous.get_logs(fromBlock=from_block, toBlock=last_block)))
        assert len(mem_events) > 0, "0 LogMemoryPageFactContinuous for this Fact Registry"
        
        memory_page_transactions_map = {hex(event["args"]["memoryHash"]): event["transactionHash"].hex() for event in mem_events}

        """
        Fetch all `LogMemoryPagesHashes` events from the GpsStatementVerifier
        returns a mapping between Cairo job's fact and the memory pages hashes for verifier contract.
        """
        statement_verifier_events = []
        statement_verifier_events.extend(list(gps_statement_verifier_contract.events.LogMemoryPagesHashes.get_logs(fromBlock=from_block, toBlock=last_block)))
        assert len(statement_verifier_events) > 0, "0 LogMemoryPagesHashes for this Statement Verifier"

        fact_memory_pages_map = {}
        for event in statement_verifier_events:
            pages = ["0x" + page.hex() for page in event["args"]["pagesHashes"]]
            fact_memory_pages_map[event["args"]["programOutputFact"].hex()] = pages

    
        return cls(
            web3=web3,
            memory_page_transactions_map=memory_page_transactions_map,
            fact_memory_pages_map=fact_memory_pages_map,
            memory_page_fact_registry_contract=memory_page_fact_registry_contract,
        )

    def get_memory_pages_from_fact(self, fact_hash: bytes) -> List[List[int]]:
        """
        Given a fact hash, retrieves the memory pages which are relevant for that fact.
        """
        if fact_hash not in self.fact_memory_pages_map:
            raise Exception(f"Fact hash {fact_hash} was not registered in the verifier contracts.")
        
        memory_pages = []
        memory_pages_hashes = self.fact_memory_pages_map[fact_hash]

        for memory_page_hash in memory_pages_hashes:
            transaction_str = self.memory_page_transactions_map[memory_page_hash]

            memory_pages_tx = self.web3.eth.get_transaction(HexStr(transaction_str))

            inp = memory_pages_tx["input"]
            tx_decoded_values = self.memory_page_fact_registry_contract.decode_function_input(memory_pages_tx["input"])[1]["values"]
            memory_pages.append(tx_decoded_values)

        return memory_pages


def load_contracts(
    web3: web3.Web3, contracts_file: str, contracts_names: List[str]
) -> Dict[str, web3.contract.Contract]:
    """
    Given a list of contract names, returns a dict of contract names and contracts.
    """
    res = {}
    with open(contracts_file) as infile:
        source_json = json.load(infile)
    for contract_name in contracts_names:
        try:
            res[contract_name] = web3.eth.contract(
                address=source_json[contract_name]["address"], abi=source_json[contract_name]["abi"]
            )
        except (KeyError, InvalidAddress) as ex:
            raise ex
    return res


def parse_storage_updates(diffs):
    diffs.pop(0)  # num of contracts updates
    parsed_diff = {}
    while len(diffs) > 0:
        contract_address = hex(int(diffs.pop(0)))
        num_updates = diffs.pop(0)
        parsed_diff[contract_address] = {}
        for _ in range(num_updates):
            storage_var_address = hex(int(diffs.pop(0)))
            parsed_diff[contract_address][storage_var_address] = diffs.pop(0)
    return parsed_diff


def main():
    contract_names = ["GpsStatementVerifier", "MemoryPageFactRegistry"]
    parser = argparse.ArgumentParser()

    # Note that Registration of memory pages happens before the state update transaction, hence
    # make sure to use from_block which preceeds (~500 blocks) the block of the state transition fact
    parser.add_argument('--web3_node', dest='web3_node', default="must have node", help='rpc node url')
    parser.add_argument('--fact', dest='fact', default="983e4a7350a46070642a1ba0e6df4b097d527633c1ef256a2140c9ad0f264587", type=str.lower)

    args = parser.parse_args()
    
    w3 = web3.Web3(web3.HTTPProvider(args.web3_node))
    assert w3.is_connected(), f"Cannot connect to http provider {args.web3_node}."

    verifier_contracts_path = os.path.join(os.path.dirname(__file__), "../assets/contracts.json")
    verifier_contracts_dict = load_contracts(web3=w3, contracts_file=verifier_contracts_path, contracts_names=contract_names)
    (gps_statement_verifier_contract, memory_pages_contract) = [verifier_contracts_dict[contract_name] for contract_name in contract_names]

    memory_pages_fetcher = MemoryPagesFetcher.create(
        web3=w3,
        gps_statement_verifier_contract=gps_statement_verifier_contract,
        memory_page_fact_registry_contract=memory_pages_contract
    )

    pages = memory_pages_fetcher.get_memory_pages_from_fact(args.fact)

    state_diff = pages[1:]  # ignore first page
    diffs = [item for page in state_diff for item in page]  # flatten
    # len_deployments = diffs.pop(0)
    # deployments_data = list(map(lambda arg: hex(int(arg)) if int(
    #     arg) > 10**10 else int(arg), diffs[0:len_deployments]))
    # storage_updates = parse_storage_updates(diffs[len_deployments:])
    # deployed_contracts = {}
    # while len(deployments_data) > 0:
    #     contract_address = deployments_data.pop(0)
    #     deployed_contracts[contract_address] = {}
    #     deployed_contracts[contract_address]['contract_hash'] = deployments_data.pop(
    #         0)
    #     num_constructor_args = deployments_data.pop(0)
    #     deployed_contracts[contract_address]['constructor arguments'] = deployments_data[0:num_constructor_args]
    #     deployments_data = deployments_data[num_constructor_args:]

    # print(storage_updates)
    # print(deployed_contracts)


if __name__ == "__main__":
    main()
