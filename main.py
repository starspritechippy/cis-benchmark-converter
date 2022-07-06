import argparse
import pathlib
import sys
from typing import Iterator, Optional
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer
from regex_patterns import dot_separated_pattern, line_end_pattern, page_no_pattern
from filetype import guess
import csv


def yes_no_prompt(prompt: str, default: Optional[bool] = None) -> bool:
    stuff = ""
    while stuff not in ["y", "n"]:
        stuff = input(prompt)
        if not stuff and default is not None:
            return True if default else False
        stuff = stuff.lower()[0]
    return True if stuff == "y" else False

def get_page_content(page: LTPage) -> str:
    content = []
    final_content = ""

    # go through all groups in a Page and if they contain text, 
    for group in page.groups:
        if isinstance(group, LTTextContainer):
            content.append(group.get_text())

    final_content = "".join(content)
    # even if the page contains no text, an empty string is still returned
    # this serves to keep the page indeces in order
    return final_content


def extract_table_of_contents(filename: str | pathlib.Path) -> str:
    # variable initialization

    # start and end are used to track the page index of the table of contents
    index: int = 0
    start: int = 0
    # the variable "first bullet point" holds the first line stored in the table of contents
    # we can compare the page content against this to see if we've reached the end of the ToC
    first_bullet_point: str = ""
    # page_contents contains the content of the pages, one String for each page
    # using start and end, it's possible to get just the right text
    pages_content: list[str] = []

    pages: Iterator[LTPage] = extract_pages(filename)

    try:
        while page := next(pages):
            page: LTPage
            content = get_page_content(page).replace("\t", " ")
            if "contents" in content.lower():
                start = index
                lines = content.splitlines()
                for line in lines[1:]:
                    if not ("contents" in line.lower() or "use" in line.lower()):
                        first_point_line = line
                        first_bullet_point = first_point_line[0:first_point_line.find("..")].strip()
                        break
                if not first_bullet_point:
                    print("Could not find table of contents. Please report.", file=sys.stderr)
                    exit(1)
            elif start != 0 and first_bullet_point in content:
                break
            pages_content.append(content)
            index += 1
    except StopIteration:
        print("Could not find table of contents. Please report.", file=sys.stderr)
        exit(1)

    # remove the first few pages that don't have table of contents stuff
    pages_content = pages_content[start:]

    contents = "\n".join(pages_content)
    lines = contents.splitlines()

    # remove empty lines
    for line in lines:
        if line.strip() == "":
            lines.remove(line)

    # remove lines that contain a page indicator
    for line in lines:
        if page_no_pattern.search(line):
            lines.remove(line)

    # add a newline character to multiline bullet points
    # this concatenates multiline points into a single line in the next block
    for index, line in enumerate(lines):
        if line_end_pattern.search(line):
            lines[index] += "\n"

    ntext = "".join(lines)
    lines = ntext.splitlines()
    nlines = []

    for line in lines:
        if dot_separated_pattern.match(line):
            nlines.append(line)

    ntext = "\n".join(nlines)
    return ntext


def num_point(line: str):
    groups = dot_separated_pattern.match(line).groups()
    return groups[0].strip(), groups[1].strip(". "), groups[2].strip()


def num_point_no_page(line: str):
    groups = dot_separated_pattern.match(line).groups()
    return groups[0].strip(), groups[1].strip(". ")


def get_points(text: str, include_page_numbers: bool = True):
    lines = text.splitlines()
    if include_page_numbers:
        points = map(num_point, lines)
    else:
        points = map(num_point_no_page, lines)
    return points


def create_csv(content: str, output_file: Optional[str | pathlib.Path]):
    global skip_yn
    global include_headers
    global include_page_numbers
    global csv_delimiter
    global is_full

    if output_file.exists() and not skip_yn:
        if not yes_no_prompt("{} already exists. Overwrite it? [y/N] ".format(output_file), default=False):
            exit(1)

    if not output_file:
        # this really is only a fallback, this should always be a given
        output_file = pathlib.Path("out.pdf")
    try:
        file = open(output_file, "w")
    except PermissionError:
        print("Couldn't open", str(output_file), file=sys.stderr)
        exit(1)
    except FileNotFoundError:
        print("Couldn't create the file {}. Does the folder exist?".format(output_file))
        exit(1)
    lines = get_points(content, include_page_numbers)

    # Smart pass
    # lines is an iterable of iterables
    if not is_full:
        lines = list(lines)
        lines_smart = []
        for idx, item in enumerate(lines):
            depth = len(item[0].split("."))
            try:
                next_depth = len(lines[idx+1][0].split("."))

                if next_depth > depth:
                    continue
                else:
                    depth = next_depth
                    lines_smart.append(item)
                
            except IndexError:
                lines_smart.append(item)
                pass

        lines = lines_smart
    
    writer = csv.writer(file, delimiter=csv_delimiter)
    if include_headers:
        if include_page_numbers:
            writer.writerow(["Point", "Description", "Page Number"])
        else:
            writer.writerow(["Point", "Description"])
    writer.writerows(lines)
    file.close()
    return

def main():
    # python main.py [OPTIONS] [FILE]
    # Options:
    #   --full, -f      Convert the entire table of contents to a CSV file, rather than just a bit of it
    #   --output, -o    Specify an output path. By default, the original file name is used, with the .csv extension

    parser = argparse.ArgumentParser(description="Convert A CIS Benchmark PDF file to CSV")
    parser.add_argument("filename", metavar="FILE", type=pathlib.Path)
    parser.add_argument("--full", "-f", dest="is_full", action="store_true", help="Convert the entire table of contents to a CSV file, rather than just a bit of it")
    parser.add_argument("-y", dest="skip_yn", action="store_true", help="Automatically reply \"y\" for yes/no prompts.")
    parser.add_argument("--include-headers", dest="include_headers", action="store_true", help="In the generated CSV file, include a row explaining the fields")
    parser.add_argument("--include-page-numbers", dest="include_page_numbers", action="store_true", help="In the generated CSV file, include the page numbers.")
    parser.add_argument("--output", "-o", dest="output_path", type=pathlib.Path, action="store", help="Specify an output path. By default, the original file name is used, with the .csv extension")
    parser.add_argument("--delimiter", "-d", dest="csv_delimiter", type=str, action="store", default="\t", help="Specify a delimiter to be used in the resulting CSV file. Tab is used by default")

    args = parser.parse_args()
    global filename
    global is_full
    is_full = args.is_full
    global skip_yn
    skip_yn = args.skip_yn
    global include_headers
    include_headers = args.include_headers
    global include_page_numbers
    include_page_numbers = args.include_page_numbers
    global csv_delimiter
    csv_delimiter = args.csv_delimiter
    global output_path
    # use as args.filename, args.is_full, args.output_path
    # args.filename is required; it's a pathlib.Path object
    # args.is_full is a boolean indicating whether to output the entire ToC or only the "necessary" stuff
    # args.output_path signifies the optional desired output path

    filename = args.filename
    if not filename.exists:
        print(str(filename), "does not exist.", file=sys.stderr)
        exit(1)
    elif not (filename.is_file() and guess(str(filename.absolute())) and guess(str(filename.absolute())).extension == "pdf"):
        print(str(filename), "is not a PDF file", file=sys.stderr)
        exit(1)

    # This now holds the entire table of contents
    contents = extract_table_of_contents(filename)
    # with open("debug.txt", "w") as File:
    #     File.write(contents)
    output_path = args.output_path
    if not output_path:
        output_path = filename
        output_path = pathlib.Path(str(filename)[:-3] + "csv")
    create_csv(contents, output_path)
    return 0


if __name__ == "__main__":
    main()