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

# Aternative

Python (3.10) 

```
pip install requirements.txt
```

# Running

A number of test files exist (see **sample_data** Dir).

to run a selected file:

```
python main.py <filename>
# EG
python main.py sample_data/anon_selections_twosets
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
