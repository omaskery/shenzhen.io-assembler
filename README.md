
# Overview

This is just a silly tool to make it easier to write assembly for the microprocessors in SHENZHEN I/O,
an awesome programming game released recently by Zachtronics.

WARNING: This assembler handles UNDOCUMENTED INSTRUCTIONS available in the game, and as such its
source contains *mild spoilers!*

# Usage

`usage: main.py [-h] [-o OUTPUT] [-c {MC4000X,MC4000,MC6000}] input`

## Example: Pulse Generator

```asm
# the pin we'll pulse the outputs on
alias output_pin p1

# the width of the pulses on period and off period
const on_duration 2
const off_duration 4

# the value we'll emit to the output pin during the on and off phases
const on_value 100
const off_value 0

# the actual code:
  mov on_value output_pin   # write the on value to the output pin
  slp on_duration           # sleep for the on duration
  mov off_value output_pin  # write the off value to the output pin
  slp off_duration          # sleep for the off duration
  # the microprocessors in the game automatically loop to the beginning
  # so this will run forever now
```

Which compiles to:

```asm
  mov 100 p1
  slp 2
  mov 0 p1
  slp 4
```

# Assembly Syntax

The assembly used is almost entirely identical to that in SHENZHEN.IO, the only differences are:

## Preprocessor Directives

There is currently only one supported directive:

- `!include "some/filepath/here.asm"` - textually includes the specified file in-place

## 'Macro' Instructions

| Mneumonic | Argument 1 | Argument 2 | Explanation
| --------- |:----------:|:----------:| -----------
| alias     | name       | register   | allows you to use *name* in place of *register* elsewhere in the program
| const     | name       | value      | allows you to use *name* instead of *value* elsewhere in the program

# To do

- [ ] Verify types of instruction arguments
- [ ] Verify register references exist on selected chip
- [x] Warn about exceeding memory space limitations of selected chip
- [ ] Basic optimisation (probably not?)
- [ ] Detect unused code (possibly not?)
- [ ] Detect unused aliases/constants?
- [ ] Compress label names
- [ ] Detect and remove redundant labels?
- [x] Error on redefinitions of alias/const names
- [x] Add support for including other files textually (preprocessor style)
- [x] Improve error reporting to use source file and source line
- [ ] Make errors accumulate and prevent output, rather than immediate abort?
- [ ] Make constants evaluate simple expressions?

