import os
from pathlib import Path

from starkware.cairo.lang.vm.crypto import pedersen_hash
from starkware.python.utils import to_bytes
from starkware.starknet.public.abi import starknet_keccak
from requests import get

CONTRACT_NAME = "storage"
SLOTS = 2**251

print("\nTotal Storage Slots: ", SLOTS)

#
# Raw Keys
#
single_key = starknet_keccak(b"single_store")
print("\n\tSingle Store's Key: 0x{:x}".format(single_key))
print("\tSingle Store's Key(dec): ", single_key)

# mapping variable first hash element(pedersen(this, index))
mapping_key = starknet_keccak(b"mapping_store")
print(
    "\n\tMapping Store's 1st Hash Element: 0x{:x}".format(
        pedersen_hash(mapping_key, 100)
    )
)
print(
    "\tMapping Store's 1st Hash Element(dec): ", pedersen_hash(mapping_key, 100)
)

# multiple value continuous storage
multi_key = starknet_keccak(b"multi_store")
print("\n\tMulti Store's Key Left: 0x{:x}".format(multi_key))
print("\tMulti Store's Key Right: 0x{:x}".format(multi_key + 1))

# struct value continuous storage
struct_key = starknet_keccak(b"struct_store")
print("\n\tStruct Store's Key Left: 0x{:x}".format(struct_key))
print("\tStruct Store's Key Center: 0x{:x}".format(struct_key + 1))
print("\tStruct Store's Key right: 0x{:x}\n".format(struct_key + 2))
