# Creates sets of expectations, saves them,
# but also runs the expirements as an option
# everything else is in sub directories.
from Planner.run import run


selected_problem = "A_SND"
# Select your problem to run, separate with an underscore,
# then select the domain type. Your problem files should
# be labeled similarly, with the problem file adding a
# 'P' to the end of the problem name, and the operator
# file adding an 'O' to the end of the problem name.
# they should then be in a directory titled the same
# as the domain type.

run(selected_problem)


