"""
Run me to process a selections file exported from IIBProjects
"""
import sys

from student_selections import load_selections


if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <filename>")
else:
    selections = load_selections(sys.argv[1])

    selections.TIMEOUT=100

    for selection_set in selections.allocate():
        print()
        print(f"{len(selection_set)} students in set,\
 total serials: {selection_set.total_serial()} ")
        selection_set.print_allocated_set()
