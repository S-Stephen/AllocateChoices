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


# Tests

In the root directory

```
pytest --cov=.
```
