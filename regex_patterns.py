import re

# Matches, if the line starts with any dot-separated numbers, 
# and has two consecutive dots after the bullet point
# i.e. 12.1.2
# Group 1: dot-separated numbers
# Group 2: subject line
old_dot_separated_pattern = re.compile(r"^([\d+\.]*\d+) (.*) ?\.\.")
dot_separated_pattern = re.compile(r"^([\d+\.]*\d+) ([^.]*) ?\.* (\d+) ?$")

# Matches, if the line ends with a dot, then a number
# in other words, when a line has a referenced page number at the end
# Used for filtering
line_end_pattern = re.compile(r"\. \d+ $")

# Matches, when the line contains a current page indicator
# Used for filtering
page_no_pattern = re.compile(r"(\d+) \| P a g e")