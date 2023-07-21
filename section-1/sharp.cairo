%builtins output

// Rough Trace Cell Calculation(no builtin ratios):
// 4 Cairo Steps x 50 trace cells + 5 trace cells
// ----------------
// 205 trace cells  
func main(output_ptr: felt*) -> (output_ptr: felt*) {
    // assign 100 to the first unused memory cell and advance ap
    [ap] = 100;
    [ap] = [output_ptr], ap++;

    // return the new value of the output_ptr
    // which was advanced by 1
    let output_ptr = output_ptr + 1;

    return(output_ptr = output_ptr);
}
