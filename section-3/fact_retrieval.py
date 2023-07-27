import argparse
import json
import web3
import requests
import os
from web3.exceptions import InvalidAddress
from typing import Dict, List
from typing import Dict, List
from eth_typing.encoding import HexStr
from web3 import Web3
from web3.contract import Contract

NONCE_BASE = 2 ** 64

def main():
    contract_names = ["GpsStatementVerifier", "MemoryPageFactRegistry", "StarknetCoreContracts"]
    parser = argparse.ArgumentParser()

    parser.add_argument('--web3_node', dest='web3_node', default="must have node", help='rpc node url')
    parser.add_argument('--da_output', dest='da_output', default=None, help='location for da output')

    args = parser.parse_args()
    
    """
    Init L1 Solidity Contract Handles
    """
    l1_node = web3.Web3(web3.HTTPProvider(args.web3_node))
    assert l1_node.is_connected(), f"Cannot connect to http provider {args.web3_node}."

    contracts_path = os.path.join(os.path.dirname(__file__), "../assets/contracts.json")
    contracts_dict = load_contracts(web3=l1_node, contracts_file=contracts_path, contracts_names=contract_names)
    (gps_statement_verifier_contract, memory_pages_contract, sn_core_contracts) = [contracts_dict[contract_name] for contract_name in contract_names]

    last_block = l1_node.eth.block_number
    from_block = last_block - 400

    """
    Fetch Starknet State Updates
    and associated state update facts
    """
    state_updates = list(sn_core_contracts.events.LogStateUpdate.get_logs(fromBlock=from_block, toBlock=last_block))
    state_update_facts = list(sn_core_contracts.events.LogStateTransitionFact.get_logs(fromBlock=from_block, toBlock=last_block))

    update_index = len(state_updates) - 1
    update_fact = state_update_facts[update_index]["args"]["stateTransitionFact"].hex()

    sn_block_num = state_updates[update_index]["args"]["blockNumber"]
    print("Starknet Block #{}:".format(sn_block_num))
    print("\troot - ", state_updates[update_index]["args"]["globalRoot"])
    print("\tfact - ", update_fact)

    """
    Fetch all `LogMemoryPagesHashes` events from the GpsStatementVerifier
    returns a mapping between Cairo job's fact and the memory pages hashes for verifier contract.
    """
    statement_verifier_events = []
    statement_verifier_events.extend(list(gps_statement_verifier_contract.events.LogMemoryPagesHashes.get_logs(fromBlock=from_block, toBlock=last_block)))
    assert len(statement_verifier_events) > 0, "0 LogMemoryPagesHashes for this Statement Verifier"

    fact_memory_pages_map = {}
    for event in statement_verifier_events:
        if update_fact == event["args"]["programOutputFact"].hex():
            pages = [page.hex() for page in event["args"]["pagesHashes"]]
            print("\t{} registry pages".format(len(pages)))
            
            """
            Fetch all `LogMemoryPageFactContinuous` events from the MemoryPageFactRegistry
            """
            mem_events = list(memory_pages_contract.events.LogMemoryPageFactContinuous.get_logs(fromBlock=from_block, toBlock=last_block))
            assert len(mem_events) > 0, "0 LogMemoryPageFactContinuous for this Fact Registry"

            for event in mem_events:
                for i, page in enumerate(pages):
                    if format(event["args"]["memoryHash"], 'x') == page:
                        mem_tx = event["transactionHash"].hex()
                        print("\t\tPage {} - ".format(i + 1))
                        print("\t\tmem_hash ", event["args"]["memoryHash"])
                        print("\t\ttx_hash ", mem_tx)
                        
                        # skip first memory page
                        if i > 0:
                            memory_pages_tx = l1_node.eth.get_transaction(HexStr(mem_tx))

                            fact_input_sn_output = memory_pages_contract.decode_function_input(memory_pages_tx["input"])[1]["values"]

                            if args.da_output is not None:
                                f = open(args.da_output, "w")
                                f.write('\n'.join(str(e) for e in fact_input_sn_output))
                                f.close()

                            parse_da(fact_input_sn_output)

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

def parse_da(fact_input_sn_output):
    """
    Parse the data availability output from the Starknet OS
    print the parsed da output
    0⋯0⏟127 bits|class information flag(1 bit)|new nonce(64 bits)|# of storage updates(64 bits)
    """
    num_storage_updates = fact_input_sn_output.pop(0)
    print("\t\t\tContract Updates - ", num_storage_updates)
    for j in range(num_storage_updates):
        contract = fact_input_sn_output.pop(0)
        print("\t\t\tContract ", contract)
        da_word = fact_input_sn_output.pop(0)
        print("\t\t\tDA word ", da_word)
        if da_word > NONCE_BASE:
            word = list(bin(da_word))[2:]
            word_length = len(word)
            if word_length == 129:
                class_hash = fact_input_sn_output.pop(0)
                nonce =  int("".join(str(x) for x in word[1:65]), 2)
                storage_updates = int("".join(str(x) for x in word[65:]), 2)
                print("\t\t\t\tcontract deployed or replaced")
                print("\t\t\t\tnew nonce ", nonce)
                print("\t\t\t\tstorage updates ", storage_updates)
                for k in range(storage_updates):
                    print("\t\t\t\tKey: ", fact_input_sn_output.pop(0))
                    print("\t\t\t\tValue: ", fact_input_sn_output.pop(0))

            elif word_length > 64:
                nonce =  int("".join(str(x) for x in word[:word_length-64]), 2)
                storage_updates = int("".join(str(x) for x in word[word_length-64:]), 2)
                print("\t\t\t\tnew nonce ", nonce)
                print("\t\t\t\tstorage updates ", storage_updates)
                for k in range(storage_updates):
                    print("\t\t\t\tKey: ", fact_input_sn_output.pop(0))
                    print("\t\t\t\tValue: ", fact_input_sn_output.pop(0))

        else:
            for k in range(da_word):
                print("\t\t\t\tKey: ", fact_input_sn_output.pop(0))
                print("\t\t\t\tValue: ", fact_input_sn_output.pop(0))
        
        print()

    print("\t\t\tDeclared Classes - ", fact_input_sn_output.pop(0))

if __name__ == "__main__":
    main()
