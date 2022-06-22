
import os
path = os.path.dirname(__file__)

from student_selections import SelectionBacktrackSolver

def test_set_generated_with_first_allocation():
    """All selections can be allocated immediately"""
    bt_solver = SelectionBacktrackSolver()
    bt_solver.load_selections(path+"/fixtures/anon_selections_nonsharing.csv")

    assert len(bt_solver.allocate()) == 1
