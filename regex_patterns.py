import re

# Matches, if the line starts with any dot-separated numbers, 
# and has two consecutive dots after the bullet point
# i.e. 12.1.2
# Group 1: dot-separated numbers
# Group 2: subject line
dot_separated_pattern = re.compile(r"^([\d+\.]*\d+) (.*?) ?(\d+) ?$")

# Matches if the end of a line features a page number
# Used for filtering
line_end_pattern = re.compile(r"\d+ ?$")

# Matches, when the line contains a current page indicator
# Used for filtering
page_no_pattern = re.compile(r"(\d+) \| P a g e")