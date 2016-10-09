# aliases for keys
alias key_input x1
alias ram_data x2
alias ram_addr x3

# constants for storing in RAM chip
const default_cheese_duration 1
const default_mustard_duration 1

# addresses of constants in RAM chip
const cheese_duration_addr 0
const mustard_duration_addr 1

# values to send to RAM chip on certain key presses
const no_cheese 0
const extra_mustard 2

# keypad values we expect
const key_cancel -1
const key_hold_the_cheese 1
const key_extra_mustard 2
const key_sandwich_time 3
