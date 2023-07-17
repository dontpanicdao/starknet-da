%builtins output

func main(output_ptr: felt*) -> (output_ptr: felt*) {
    // assign 100 to the first unused memory cell and advance ap
    [ap] = 100;
    [ap] = [output_ptr], ap++;

    // return the new value of the output_ptr
    // which was advanced by 1
    let output_ptr = output_ptr + 1;

    return(output_ptr = output_ptr);
}
