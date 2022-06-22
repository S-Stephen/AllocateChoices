"""
Run me to process a selections file exported from IIBProjects
"""
import sys

from student_selections import SelectionBacktrackSolver

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <filename>")
else:
    bt_solver = SelectionBacktrackSolver()
    bt_solver.load_selections(sys.argv[1])

    bt_solver.TIMEOUT=100
    bt_solver.MAX_PROJ_STUDENTS=1

    for selection_set in bt_solver.allocate():
        print()
        print(f"{len(selection_set)} students in set,\
 total serials: {selection_set.total_serial()} ")
        selection_set.print_allocated_set()
