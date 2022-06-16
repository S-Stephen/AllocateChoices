
import os
path = os.path.dirname(__file__)

from student_selections import load_selections

def test_twosets_found():
    """All selections can be allocated immediately"""
    selections = load_selections(path+"/fixtures/anon_selections_twosets.csv")

    assert len(selections.allocate()) == 2
