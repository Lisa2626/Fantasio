#Code for normalizing SPIRou observations, choose between the interactive or the automatic mode to normalise SPIRou data

import argparse
from . import interactive
from . import auto

# ------------------------------------------------------------------------------#

parser = argparse.ArgumentParser(description='Choose mode.')
parser.add_argument('mode', nargs='?', choices=['interactive', 'automatic'], help='Choose mode: interactive or automatic')
args = parser.parse_args()

if args.mode is None:
    mode = input("Choose normalisation mode ('interactive' or 'automatic'): ")
    while mode not in ['interactive', 'automatic']:
        print("Invalid mode. Please choose 'interactive' or 'automatic'.")
        mode = input("Choose normalisation mode ('interactive' or 'automatic'): ")
else:
    mode = args.mode

if mode == 'interactive':
    interactive.main()
elif mode == 'automatic':
    auto.main()

# ------------------------------------------------------------------------------#




