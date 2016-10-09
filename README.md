
# Overview

This is just a silly tool to make it easier to write assembly for the microprocessors in SHENZHEN I/O, an awesome programming game released recently by Zachtronics.

WARNING: This assembler handles UNDOCUMENTED INSTRUCTIONS available in the game, and as such its source contains *mild spoilers!*

# Usage

`usage: main.py [-h] [-o OUTPUT] [-c {MC4000X,MC4000,MC6000}] input`

# Assembly Syntax

The syntax used is almost entirely identical to that in SHENZHEN.IO, any additional instructions are purely compile-time macros and are explained below:

| Mneumonic | Argument 1 | Argument 2 | Explanation
| --------- |:----------:|:----------:| -----------
| alias     | name       | register   | allows you to use *name* in place of *register* elsewhere in the program
| const     | name       | value      | allows you to use *name* instead of *value* elsewhere in the program

# To do

- [ ] Verify types of instruction arguments
- [ ] Verify register references exist on selected chip
- [ ] Warn about exceeding memory space limitations of selected chip
- [ ] Optimisation?
- [ ] Detect unused code?
- [ ] Detect unused aliases/constants?

