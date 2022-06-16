
import os
path = os.path.dirname(__file__)

from student_selections import load_selections

def test_set_generated_with_first_allocation():
    """All selections can be allocated immediately"""
    selections = load_selections(path+"/fixtures/anon_selections_nonsharing.csv")

    assert len(selections.allocate()) == 1
