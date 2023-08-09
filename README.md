<div align="center">
    <h1>Starknet Data Availability</h1>
    <img src="assets/DAtoshi.jpg" height="256">
    <br>
    <br>
    <a href="https://docs.google.com/presentation/d/1Jv_URt6uLy_kTS0GCjXnG7I3kdkfFDFB3k-Hc1j-Z_g/edit?usp=sharing"><img src="https://img.shields.io/badge/pres-starknet--cc-blue)"/></a>
    <a href="https://docs.starknet.io/documentation/architecture_and_concepts/Data_Availability/on-chain-data"><img src="https://img.shields.io/badge/docs-da-blue)"/></a>
    <a href="https://goerli.etherscan.io/address/0xde29d060D45901Fb19ED6C6e959EB22d8626708e"><img src="https://img.shields.io/badge/core--contracts-goerli-blue)"/></a>
    <a href="https://goerli.etherscan.io/address/0x8f97970aC5a9aa8D130d35146F5b59c4aef57963"><img src="https://img.shields.io/badge/verifier-goerli-blue)"/></a>
</div>


## Setup

#### Automatic installer

```sh
# sudo apt install -y libgmp3-dev jq
# brew install gmp jq
curl https://pyenv.run | bash
source <(profile)>
pyenv install 3.9 && pyenv local 3.9
```

#### Init Cairo Env

```sh
python3.9 -m venv ~/cairo_venv
source ~/cairo_venv/bin/activate
pip install -r requirements.txt
mkdir build
```

# Section 1 - [SHARP](https://www.cairo-lang.org/playground)

#### compile
```sh
cairo-compile section-1/sharp.cairo --output build/sharp_compiled.json
```


#### run w/ debug info
```sh
cairo-run --program build/sharp_compiled.json --print_memory --print_info --relocate_prints --layout=small --trace_file build/sharp_trace
```

# Section 2 - Fact Registries

#### compile
```sh
cairo-compile section-2/fact.cairo --output build/fact_compiled.json
```

#### submit to SHARP
```sh
cairo-sharp submit --program build/sharp_compiled.json
cairo-sharp status <JOB_ID>
```

#### run w/ PIE info
```sh
cairo-run --program section-2/fact_compiled.json --layout=small --cairo_pie_output=build/da.pie.zip
unzip build/fact.pie.zip -d build
```

#### compute fact
```sh
cairo-hash-program --program build/fact_compiled.json
python section-2/fact_check.py
```

# Section 3 - Starknet

```sh
curl --location 'https://alpha4.starknet.io/feeder_gateway/get_state_update?blockNumber=latest' | jq
```

#### set env vars

NOTE: don't copy accounts json if you already have an existing one
```sh
export STARKNET_WALLET=starkware.starknet.wallets.open_zeppelin.OpenZeppelinAccount
export STARKNET_NETWORK=alpha-goerli
export STARKNET_FEEDER_GATEWAY_URL=http://localhost:5050
export STARKNET_GATEWAY_URL=http://localhost:5050
cp assets/starknet_open_zeppelin_accounts.json ~/.starknet_accounts
```

#### deploy storage contract
```sh
starknet-devnet --seed 0
starknet-compile-deprecated section-3/storage.cairo --output build/storage_compiled.json
starknet declare --account devnet --contract build/storage_compiled.json --deprecated --gateway_url http://localhost:5050 --feeder_gateway_url http://localhost:5050
starknet invoke --address 0x041a78e741e5af2fec34b695679bc6891742439f7afb8484ecd7766661ad02bf --account devnet --gateway_url http://localhost:5050 --feeder_gateway_url http://localhost:5050  --abi assets/udc.json  --function deployContract  --inputs 0x6fa450e1381e13f22d1bc5a6ef56edfe9fafd7f4b3a7d483b8c14de83a5be6f 0 0 0
```

#### query storage keys

```sh
python section-3/storage.py
curl --location 'http://localhost:5050/feeder_gateway/get_storage_at?contractAddress=<ADDRESS>&key=<INT KEY FROM SCRIPT>'
```

```sh
python section-3/fact_retrieval.py --web3_node https://goerli.infura.io/v3/<API KEY> --da_output build/out.txt
```

#### run starknet os

```sh
cairo-run --program=assets/os_compiled.json --layout=starknet_with_keccak --program_input=assets/sn_input.json  --cairo_pie_output=build/sn.pie.zip --print_output
```