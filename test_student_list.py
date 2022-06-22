
import os
path = os.path.dirname(__file__)

from student_selections import SelectionBacktrackSolver

def test_students_by_popular_projects():
    """The students will be ordered as associated to popular projects"""

    bt_solver = SelectionBacktrackSolver()
    bt_solver.load_selections(path+"/fixtures/anon_selections_popular_projects.csv")

    # placeholder
    assert True


def test_popular_projects():
    """Test that our pojects can be identified and ordered by how many selections they have"""

    # placeholder
    assert True