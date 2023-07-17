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
# sudo apt install -y libgmp3-dev
# brew install gmp
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

# Section 1 - SHARP

#### compile
```sh
cairo-compile section-1/sharp.cairo --output build/sharp_compiled.json
```
[cairo playground](https://www.cairo-lang.org/playground)

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
python section-3/fact_retrieval.py --from_block 52144 \
--contracts_abi_file assets/starknet_verifier_abi.json
--web3_node https://goerli.infura.io/v3/ca0bc142fd6d4090838eebb88a36596f \
--fact 0x1da36bf5ea606a1c9936fc4d044bbb36607fb3b263a4a1b020ea87a3d1c46be4 
```
