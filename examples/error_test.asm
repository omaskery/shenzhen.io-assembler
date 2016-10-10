# test various preprocessor directive edge cases
!include "fake"
!include fake
!include fake"
!include "fake
!include
!fake
!

# constant redefinition
const redef 4
const redef 4

# constants must be integers
const non_integer_const non_integer_value

# argument counts
  mov too many args
  gen test # too few args

# conditions without associated instructions
+
-
@
