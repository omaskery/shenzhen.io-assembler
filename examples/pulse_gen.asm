
alias output_pin p1

const on_duration 2
const off_duration 4

const on_value 100
const off_value 0

  mov on_value output_pin
  slp on_duration
  mov off_value output_pin
  slp off_duration