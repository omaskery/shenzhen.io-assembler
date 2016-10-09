!include "constants.asm"

# code itself:

# reset state to default values
init:
  mov cheese_duration_addr ram_addr
  mov default_cheese_duration ram_data
  mov default_mustard_duration ram_data

# await and act on keypad input
await:
  # wait for key press
  slx key_input
  # move key into accumulator so we can start testing it...
  mov key_input acc
  # is the value KEY_CANCEL or KEY_SANDWHICH_TIME?
  tlt acc key_hold_the_cheese
- tgt acc key_extra_mustard
  # if so, reset state!
+ jmp init
  # otherwise was the extra mustard button pressed?
  teq acc key_extra_mustard
  # if not, they asked for no cheese, so update that value in RAM
- mov cheese_duration_addr ram_addr
- mov no_cheese ram_data
  # if so, they asked for extra mustard, so update that value in RAM
+ mov mustard_duration_addr ram_addr
+ mov extra_mustard ram_data
  # wait for more key presses!
  jmp await
