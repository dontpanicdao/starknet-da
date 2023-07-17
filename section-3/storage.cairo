%lang starknet

// starknet-compile storage.cairo --output storage_compiled.json
// starknet declare --account devnet --gateway_url http://localhost:5050 --feeder_gateway_url http://localhost:5050 --contract storage_compiled.json
// starknet invoke --address 0x041a78e741e5af2fec34b695679bc6891742439f7afb8484ecd7766661ad02bf --account devnet --gateway_url http://localhost:5050 --feeder_gateway_url http://localhost:5050  --abi udc.json  --function deployContract  --inputs 0x3cbb006ebfac465fc64939c2ba2ddfb1db0aa2a8324a29206e3ad72ee6e8e6a 0 0 0
from starkware.cairo.common.cairo_builtins import HashBuiltin, SignatureBuiltin
from starkware.starknet.common.syscalls import storage_read
from starkware.cairo.common.hash import hash2

struct Custom {
    left: felt,
    center: felt,
    right: felt,
}

//
// '@storage_var' decorator declares a variable that will be kept as part of the contract storage
//   - can consist of a single felt, or map to custom types(tuple, structs)
//   - '.read' and '.write' utility functions are created automatically for storage variables
//
@storage_var
func single_store() -> (res: felt) {
}

@storage_var
func mapping_store(idx: felt) -> (res: felt) {
}

@storage_var
func multi_store() -> (res: (left: felt, right: felt)) {
}

@storage_var
func struct_store() -> (res: Custom) {
}

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    single_store.write(1);
    mapping_store.write(100, 123);
    mapping_store.write(200, 567);
    multi_store.write((left=456, right=789));
    struct_store.write(Custom(left=101112, center=131415, right=161718));

    return ();
}

//
// '@external' functions can be used to write to contract storage
//
@external
func update_single_store{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    value: felt
) {
    single_store.write(value);

    return ();
}

@external
func update_multi_store{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    value: (left: felt, right: felt)
) {
    multi_store.write(value);

    return ();
}

@external
func update_struct_store{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    value: Custom
) {
    struct_store.write(value);

    return ();
}
