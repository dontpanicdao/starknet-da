<div align="center">
    <h1>Starknet Data Availability</h1>
    <img src="assets/DAtoshi.jpg" height="256">
    <br>
</div>

[![Pres](https://img.shields.io/badge/pres-starknet--cc-blue)](https://docs.google.com/presentation/d/1Jv_URt6uLy_kTS0GCjXnG7I3kdkfFDFB3k-Hc1j-Z_g/edit?usp=sharing)
[![Docs](https://img.shields.io/badge/docs-da-blue)](https://docs.starknet.io/documentation/architecture_and_concepts/Data_Availability/on-chain-data)
[![CCs](https://img.shields.io/badge/core--contracts-goerli-blue)](https://goerli.etherscan.io/address/0xde29d060D45901Fb19ED6C6e959EB22d8626708e)
[![Verifiers](https://img.shields.io/badge/verifier-goerli-blue)](https://goerli.etherscan.io/address/0x8f97970aC5a9aa8D130d35146F5b59c4aef57963)

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
python -m venv ~/cairo_venv
source ~/cairo_venv/bin/activate
pip install cairo-lang
```

# Section 1 - SHARP

#### compile
```sh
cairo-compile section-1/sharp.cairo --output build/sharp_compiled.json
```

#### run w/ debug info
```sh
cairo-run --program build/sharp_compiled.json --print_memory --print_info --relocate_prints --layout=small
```

#### submit to SHARP
```sh
cairo-sharp submit --program build/sharp_compiled.json
```

# Section 2 - Fact Registries

#### compile
```sh
cairo-compile section-2/da.cairo --output build/da_compiled.json
```

#### run w/ PIE info
```sh
cairo-run --program section-2/da_compiled.json --layout=small --cairo_pie_output=build/da.pie.zip
unzip build/da.pie.zip -d build
```

#### compute fact
```sh
cairo-hash-program --program da_compiled.json
```

# Section 3 - Starknet

