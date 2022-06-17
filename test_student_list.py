
import os
path = os.path.dirname(__file__)

from student_selections import load_selections

def test_students_by_popular_projects():
    """The students will be ordered as associated to popular projects"""
    selections = load_selections(path+"/fixtures/anon_selections_popular_projects.csv")

    assert False
    # assert len(selections.allocate()) == 1


def test_popular_projects():
    """Test that our pojects can be identified and ordered by how many selections they have"""

    assert False