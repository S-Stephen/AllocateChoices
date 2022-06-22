"""
Attempt to solve the allocation by LP solve
"""
import sys

from lpsolve55 import * 
from student_selections import SelectionList, StudentSelection, SelectionLPSolver

if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <filename> [lpfile]")
else:
    # #solve_file = sys.argv[1]+'_solve.lp'
    solve_file= sys.argv[2] if len(sys.argv) > 2 else 'lp_solve_file.txt'
    #selections = load_selections(sys.argv[1])

    #lp_solver = SelectionLPSolver((selections))

    lp_solver = SelectionLPSolver()
    lp_solver.load_selections(sys.argv[1])
    lp_solver.MAX_STUDENT_PROJECTS = 2
    lp_solver.MAX_PROJECTS_SUP = 4
    
    quit = False
    while True:
            


        lp_solver.generate_solve_file(solve_file)

        print(f"-{solve_file}-")
        lp = lpsolve('read_LP',solve_file)
        lpsolve('set_verbose',lp,IMPORTANT)

        answer = lpsolve('solve',lp)
        if answer != 0:
            print("A solution can NOT be found")

        else:
            names = lpsolve('get_col_name', lp)
            values = lpsolve('get_variables', lp)[0]

            # update our selection list with allocations -> find based on selection varaible
            for index, result in enumerate(values):
                if result == 1:
                    lp_solver.get_selection_by_lp_variable(names[index]).allocate()

            print(f"Projects with multiple students: ({str(len(lp_solver.projects_allocated_multiple(2)))}): "+" ".join(map(lambda proj: proj.lp_safe(), lp_solver.projects_allocated_multiple(2))))

        while True:
            single_student_project = input("Enter single student project(s) or 'C' to continue 'Q' to quit:\n")
            if single_student_project == 'C':
                break
            if single_student_project == 'Q':
                quit=True
                break
            
            for project_lp_code in single_student_project.split():
                lp_solver.add_single_student_project(project_lp_code)
        # Tidy this 
        if quit:
            break

        print(f"Single student projects: {list(map(lambda project: project.lp_safe(), lp_solver.single_student_projects()))}")

        while True:
            single_student_project = input("Enter a multiple student project or 'C' to continue 'Q' to quit:\n")
            if single_student_project == 'C':
                break
            if single_student_project == 'Q':
                quit=True
                break

            lp_solver.add_multiple_student_project(single_student_project)
        print(f"Single student projects: {list(map(lambda project: project.lp_safe(), lp_solver.single_student_projects()))}")

        lp_solver.clear_allocations()

        if quit:
            break