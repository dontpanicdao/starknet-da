%builtins output

// Compile:
// cairo-compile da.cairo --output da_compiled.json

// Run w/ Debug Info:
// cairo-run --program da_compiled.json --print_memory --print_info --relocate_prints --layout=small

// Submit to SHARP:
// cairo-sharp submit --program da_compiled.json

// Compute Fact:
// cairo-hash-program --program da_compiled.json
func main(output_ptr: felt*) -> (output_ptr: felt*) {
    // assign 100 to the first unused memory cell and advance ap
    [ap] = 100;
    [ap] = [output_ptr], ap++;

    [ap] = 200;
    [ap] = [output_ptr + 1], ap++;

    [ap] = 300;
    [ap] = [output_ptr + 2], ap++;

    // return the new value of the output_ptr
    // which was advanced by 3
    let output_ptr = output_ptr + 3;

    return(output_ptr = output_ptr);
}
