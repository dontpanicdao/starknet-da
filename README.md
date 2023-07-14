<div align="center">
    <h1>Starknet Data Availability</h1>
    <img src="assets/DAtoshi.jpg" height="256">
    <br>
</div>
[![presentation](https://docs.rs/anthropic/badge.svg)](https://docs.google.com/presentation/d/1Jv_URt6uLy_kTS0GCjXnG7I3kdkfFDFB3k-Hc1j-Z_g/edit?usp=sharing)

## Setup

#### Homebrew in macOS

```sh
brew update
brew install pyenv
```

#### Automatic installer

`curl https://pyenv.run | bash`


# Section 1 - SHARP

// Compile:
// cairo-compile section-1/sharp.cairo --output build/sharp_compiled.json

// Run w/ Debug Info:
// cairo-run --program build/sharp_compiled.json --print_memory --print_info --relocate_prints --layout=small

// Submit to SHARP:
// cairo-sharp submit --program build/sharp_compiled.json


# Section 2 - Fact Registries

// Compile:
// cairo-compile section-2/da.cairo --output build/da_compiled.json

// Run w/ PIE Info:
// cairo-run --program section-2/da_compiled.json --layout=small --cairo_pie_output=build/da.pie.zip
// unzip build/da.pie.zip -d build

// Compute Fact:
// cairo-hash-program --program da_compiled.json


# Section 3 - Starknet

[Contract Addresses](https://github.com/starknet-io/starknet-addresses)
