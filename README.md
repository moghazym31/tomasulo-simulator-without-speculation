# Tomasulo's Simulator without Speculation

## Overview

This project implements a simulator for Tomasulo's algorithm without speculation. The simulator evaluates the effectiveness of a simplified out-of-order RISC processor. It utilizes a 16-bit word size ISA with 8 registers (R0-R7) and a word addressable memory with a capacity of 128KB. The supported instructions include `LOAD`, `STORE`, `BEQ`, `JAL`, `RET`, `ADD/I`, `NEG`, `NAND`, and `MUL`.

## Implementation

The simulator includes a parser that extracts necessary values from the provided instructions. For example, the parser identifies labels, registers, and immediate values based on the instruction type. The parsed data is stored in an output dictionary.

**Note**: Before executing a Load instruction, ensure that the corresponding address has been loaded into memory. If using the console version of the application, you will have the opportunity to enter the address and value. To indicate no further addresses or values, enter 'x'. After entering the values, the program will simulate Tomasulo's algorithm without speculation.

If a branch (BEQ), jump and link (JAL), or return (RET) instruction is encountered, the instructions that follow will not be issued, executed, or written back. These instructions are printed for reference. Instructions should be provided in the `instructions.txt` file. The program will automatically generate an `instructions_without_labels` file, which is used for parsing and can be ignored.

## Usage

To use the simulator, follow these steps:

1. Open the `instructions.txt` file.
2. Edit the file to include the desired instructions, with each instruction on a new line.
3. Save the changes to the `instructions.txt` file.
4. Open the command-line interface or terminal.
5. Navigate to the directory where the `main.py` script is located.
6. Run the following command to execute the simulator:

   ```
   python main.py
   ```

   **Note**: Ensure Python is installed and the necessary dependencies are satisfied.

7. The simulator will read the instructions from `instructions.txt`, simulate Tomasulo's algorithm, and display the output.

Please review the code and run the simulator using the provided files.

**Note:** Ensure the necessary Python environment is set up to run the program.

## Sample Run

Here is an example of a sample run using the provided `instructions.txt` file and the corresponding output:

### Instructions.txt Content

```
ADDI R1, R0, 4
BEQ R0, R0, Exit
ADDI R3, R3, 5
Exit:LOAD R3, 0(R0)
```

### Sample Output

<p align="center">
  <img src="https://s12.gifyu.com/images/SQtzp.png" alt="Sample Output" style="height:800px;">
</p>
