# AllocateChoices

From a set of  project choices distribute the selections to acheive the best outcome (those with the highest total selection order)

The constraints of the system are that:

* Each student can choose upto MAXCHOICES projects
* A supervisor is only allowed to supervise upto MAXPROJECTS 
* Each student is to be allocated ONE project

There is also an optimisation of the final allocation set required: 

Maximise the number of lower serial (high preference) that are allocated

Typically:

* MAXCHOICES = 5
* MAXPROJECTS = 4

# Setup VSC

Run in **Remote Container** This should provide ALL the enviroment required

# Alternative (local environment)

Python (3.10) is required
lp_solve and Python libraries are also required

```
pip install requirements.txt
```

# Running - LP Solve method

The LP solve solution provides an CLI interface allowing the user to configure a list of projects that are able to take multiple students the maximum multiple set by **SelectionLPSolver.MAX_STUDENT_PROJECTS**

The Maximum number of projects which can be alloacted to a supervisor is set by **SelectionLPSolver.MAX_PROJECTS_SUP** TODO provide the ability to set supervisors who are able to take upto a particular number of projects (eg 5, rather than 4). 

Running the LP Solve method will produce an lp file (default: __'lp_solve_file.txt'__) which can be run indepentantly by lp_solve

To run the script on a datafile extarcted from IIBProjects (where lp_filename is optional): 

```
python lp_solve.py <filename> [lp_filename]
# for sample_data/anon_selections.csv
python lp_solve.py sample_data/anon_selections.csv [lp_filename]
# save the lp_file as 'my_lp_file.txt'
python lp_solve.py sample_data/anon_selections.csv my_lp_file.txt
```

# Running - Backtrack method

A number of test files exist (see **sample_data** Dir).

to run a selected file:

```
python bt_solve.py <filename>
# EG
python bt_solve.py sample_data/anon_selections_twosets.csv
```

The script will timeout after 10 seconds to extend this modify the Class variable **SelectionList.TIMEOUT** eg;

```
    selections = load_selections(sys.argv[1])
    selections.TIMEOUT=100
```

# Configuration

The search can be configured to allow multiple students to be allocated to a project.  To do this set **MAX_PROJ_STUDENTS** variable eg:

```
    selections = load_selections(sys.argv[1])
    selections.MAX_PROJ_STUDENTS=2
    selections.allocate()
```

# Tests

In the root directory

```
pytest --cov=.
```

# Notes

Some of the students may not have made choices in which case the student count will be lower than the number of students in the file
