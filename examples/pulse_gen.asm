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
