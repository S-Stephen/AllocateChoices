
import os
path = os.path.dirname(__file__)

from student_selections import SelectionBacktrackSolver

def test_twosets_found():
    """All selections can be allocated immediately"""
    bt_solver = SelectionBacktrackSolver()
    bt_solver.load_selections(path+"/fixtures/anon_selections_twosets.csv")


    assert len(bt_solver.allocate()) == 2
