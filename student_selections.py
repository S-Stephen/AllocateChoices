"""
Library for the IIB project selection problem

(Constraint Satisfaction Problem)

Constraints:

one allocated selection per student
max 4 projects per supervisor

objective function
maximise the number of projects chosen
minimise the total priority index


X -> student (with a choice) ~ 300
Domian -> project (from choice (P1, P2, P3)) 5 apporx
Constraints -> one Project per student, max 4 project per supervisor

Possible Heuristics:

Pick the project involved in most selections
Pick  / set choice for students with least selections

AC-3 arc consitancy (reduce the domains with knowledge of constraints)

forward checking - remove selections taken or where the supervisor has max projects.
minimum conflicts algorithm to pick next node?

"""

from collections import Counter, namedtuple
import copy
from functools import reduce

import csv
import re

# unix only?
import signal

class Project:
    """Project offered"""

    def __init__(self, proj_id, supervisor_crsid, project_code) -> None:
        self.proj_id = proj_id
        self.supervisor_crsid = supervisor_crsid
        self.project_code = project_code

    def __hash__(self) -> int:
        return self.proj_id

    def __str__(self) -> str:
        return str(self.proj_id)+" "+self.project_code+" "+self.supervisor_crsid

    def __eq__(self, other):
        return self.project_code == other.project_code


class StudentSelection:
    """Student choice"""

    def __init__(self, sel_id, serial, student, project) -> None:
        self.sel_id = sel_id
        self.serial = serial
        self.student = student
        self.project = project
        self.allocated = False
        self.unavailable = 0

    def set_unavailable(self, call):
        """Mark this selection as hidden
        The value it is marked as is the callid to the allocate method (for backtracking)"""
        self.unavailable = call

    def is_available(self):
        """Is this selection still active
        TODO refactor to be available
        """
        return self.unavailable == 0

    def set_available(self):
        """
        set active
        TODO: refactor to be available
        """
        self.unavailable = 0

    def is_allocated(self):
        """Has this selection been allocated?"""
        return self.allocated

    def allocate(self):
        """Allocate the selection"""
        self.allocated = True
        # Should we also set the selection to be unavailable / removed?

    def unallocate(self):
        """Un allocate the selection"""
        self.allocated = False
        # Should we also set the selection to be unavailable / removed?

    def __str__(self):
        allocated = 'Yes' if self.allocated else 'No'
        return self.student.crsid+" -- "+str(self.project.project_code) +\
            " (project) by "+self.project.supervisor_crsid+" allocated: " +\
            allocated+" unavailable: "+str(self.unavailable)


Student = namedtuple("Student", "crsid")

class SelectionList(list):
    """
    A list of Selections

    These may form a 'valid' set
    or
    They may be the full set of selections
    """

    MAXPROJS = 4
    TIMEOUT = 10
    MAX_PROJ_STUDENTS = 1

    def __init__(self, *args):
        """Provide the constructor with a list of Selections"""
        list.__init__(self, *args)
        self.sets_found = []
        self.max_priority = 1000000000

    def _timeout_handler(self,signum,frame):
        print(f"Timeout ({self.TIMEOUT}) occured {signum} {frame}")
        raise Exception("TIMEOUT")

    def _prune_project(self, project, call=1):
        """Prune all unallocated selections containing the project

        :param project: The project that has been allocated elsewhere
        :type project: Project
        :param call: The call we are pruning the student from
        :type call: integer
        """
        # allow for two selections per project so first find number already allocated
        if ( len(list(filter(lambda sel: (sel.project.proj_id == project.proj_id and 
                                 sel.allocated is True), self )) ) >= self.MAX_PROJ_STUDENTS ):

            for sel in list(filter(lambda selection:
                                    (selection.unavailable == 0 and
                                    selection.allocated is False and
                                    selection.project.proj_id == project.proj_id), self)):
                sel.set_unavailable(call)

    def _prune_student(self, student, call=1):
        """Prune the students non-allocated choices

        :param student: The student that has been allocated elsewhere
        :type student: Student
        :param call: The call we are pruning the student from
        :type call: integer"""
        for sel in list(filter(lambda selection:
                               (selection.unavailable == 0 and
                                selection.allocated is False and
                                selection.student.crsid == student.crsid), self)):
            sel.set_unavailable(call)

    def students(self):
        """Returns all students involved in selections"""
        return set(list(map(lambda selection: selection.student, self)))

    def _available_students(self):
        """A list of available students left"""
        return set(list(map(lambda selection: selection.student, self._available_selections())))

    def _available_selections(self):
        """Selections still active/available"""
        return list(filter(lambda selection: selection.is_available() is True , self))

    def _sets_still_possible(self):
        """Are selection sets still possible for this set"""

        return len(self._allocated_selections())+len(self._available_students()) == \
            len(self.students())

    def _set_complete(self):
        """Have we complete a selection set"""

        return len(self._allocated_selections()) == len(self.students())

    def _allocated_selections(self):
        """Selections allocated"""
        return list(filter(lambda selection: selection.is_allocated(), self))

    def missing_students(self):
        """Report the missing students
        Those students not in our selection set (ie there selections are still available)
        :param students: list of students to search for
        """
        _available_selections = self._available_selections()
        students_not_allocated = list(
            map(lambda selection: selection.student, _available_selections))
        _allocated_selections = self._allocated_selections()
        students_allocated = list(
            map(lambda selections: selections.student, _allocated_selections))
        students_in_selections = [*students_allocated, *students_not_allocated]
        return set(self.students()) ^ set(students_in_selections)

    def _popular_projects(self, maxserial=100):
        """returns the most popular project ids in the selections

        :param maxserial: the max serial to consider

        Use this to identify the next project to remove?
        """
        filtered_by_serial = list(filter(lambda sel: sel.is_available(
        ) and sel.serial <= maxserial and sel.allocated is False, self))

        filtered_projects = Counter(
            list(map(lambda sel: sel.project, filtered_by_serial)))
        # dict(projectid) = num

        return sorted(filtered_projects, key=Counter(filtered_projects).get, reverse=True)
        # sorted(filtered_projects.items(), key=lambda pair: pair[1], reverse=True)
        # orderby num desc -> take first

    def _students_selected_project(self, project):
        """A list of students who have selected a project

        :param project: The project we are interested in
        :param project: Project
        """
        available_selections = self._available_selections()
        selections_with_project = filter(
            lambda sel: sel.project.proj_id == project.proj_id, available_selections)
        return list(map(lambda selection: selection.student, selections_with_project))

    def _supervisor_projects(self, crsid):
        """returns the list of projects this supersior has allocated"""
        return list(filter(lambda sel:
                           sel.project.supervisor_crsid == crsid and sel.allocated is True, self))

    def _copy_allocated_set(self):
        """return a SelectionList of selections that have been allocated"""
        return copy.deepcopy(self._allocated_selections())

    def print_allocated_set(self):
        """Displays the allocation set foun
        TODO put in an array of valid sets - to then search for BEST"""
        for sel in self._allocated_selections():
            print(sel)

    def _print__available_selections(self):
        """For debug print out the list of selections we still need to allocate"""
        for sel in self._available_selections():
            print(sel)

    def _serials(self):
        """
        the array of serials associated to the set
        """
        return list(map(lambda sel: sel.serial, \
                list(filter(lambda sel: sel.is_allocated() is True, self))))

    def total_serial(self):
        """
        Find the sum of the serials
        This could be used to find the optimum set ?
        """
        return sum(self._serials())

    def _mean_and_variance(self):
        """
        Find the mean and the variance of the serials
        This could be used to find the optimum set ?
        """

    def backtrack(self, call=0):
        """Re-instate the selections but not if it was the one we tried to allocate"""
        # unprune
        for sel in list(filter(lambda selection:
                               (selection.unavailable >= call), self)):

            if sel.unavailable == call and sel.is_allocated():
                # keep not available - tried and failed
                sel.unallocate()
            else:
                sel.set_available()

    def _allocate_selection(self,selection,call):
        """
        Allocates a selection
        :param selection: StudentSelection to allocate
        :param call: A serial ID used for backtracking
         """
        selection.allocate()
        selection.set_unavailable(call)
        self._prune_project(selection.project, call)
        self._prune_student(selection.student, call)

    def _allocate_non_conflicting_selections(self):
        """
        Allocate the selections for first choices
        where there are no other selections and the supervisor
        is not over the MAXPRROJS limit

        If complete the set will be added to the sets_found array
        """

        # find the qualifying selections

        def _count_selections(supervisor_count,sel):
            if sel.project.supervisor_crsid in supervisor_count:
                supervisor_count[sel.project.supervisor_crsid].append(sel)
            else:
                supervisor_count[sel.project.supervisor_crsid]=[sel]
            return supervisor_count

        # can we reduce the size of the set by allocating any serial 1 choices
        # where the max number of projects for the supervisor > number of selections
        selection_count = reduce(_count_selections, self, {} )


        # Find selections that can be allocated
        # The supervisor has < MAXPROJS selections
        # The selections involved are not for the same project
        can_allocate = list(
            dict(
                filter(
                    lambda elem: len(elem[1]) <= SelectionList.MAXPROJS and \
                    len(list(map(lambda sel : sel.project.proj_id,elem[1]))) == \
                    len(set(map(lambda sel : sel.project.proj_id,elem[1]))), \
                        selection_count.items())).values())


        # Allocate the selections in our list that are first choice
        flat_list = list(filter(lambda sel : sel.serial == 1, \
            [item for sublist in can_allocate for item in sublist]))
        for sel in flat_list:
            if sel.serial == 1:
                self._allocate_selection(sel,1)

        if self._set_complete():
            found_list = SelectionList(self._copy_allocated_set())
            self.sets_found.append(found_list)
            print('+', end='', flush=True)

    def students_by_popular_projects(self):
        """
        Join the list of students with the list of popular projects

        return the students in the order of selections including popular projects
        """
        students_crsids=[]
        students=[]
        for project in self._popular_projects():
            #if len(students) < 30:
            #    print(project)
            for student in self._students_selected_project(project):

                #if len(students) < 10:
                #    print(student)
                if student.crsid not in students_crsids:
                    students_crsids.append(student.crsid)
                    # pop will provide students selecting the most popular
                    #students.insert(0,student)
                    # pop  will provide students selecting the least popular
                    students.append(student)

        #print(students)
        return students

    def allocate(self):
        """Find valid allocation SelectionList sets"""

        # allocate non-controversial selections
        self._allocate_non_conflicting_selections()

        # Find the unallocated students
        # MORE - use heuristics to identify:
        #   Difficult to allocate students - these should be attempted first
        #   Whether the selection sets can be 'split'
        #       can we split the students up into groups that do not overlap?

        # MORE - Order the student list by those that have chosen the most popular projects


        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.TIMEOUT)

        students = self.students_by_popular_projects()
        try:
            self._allocate_backtrack_group_student(students,2)
        except Exception as exc:
            print(f"Exception occured (timeout?): {exc}")

        print(f"\n{len(self.sets_found)} sets found")
        
        return self.sets_found


    def _students_available_selections(self, student):
        """The available selections for this student"""
        return filter(lambda sel: sel.student == student, self._available_selections())

    def _projects_available_selections(self, project):
        """The available selections for this student"""
        return filter(lambda sel: sel.project == project, self._available_selections())

    def _allocate_backtrack_projects(self, projects, call =1):
        """
        Projects do not require a student - therefore this function is not valid
        """
        pass
        

    def _allocate_backtrack_group_student(self, students, call=1):
        """
        Backtrack worker for our search
        """
        call = call+1
        mystudents = copy.deepcopy(students)

        if len(students):
            student = mystudents.pop()
        else:
            return

        for sel in self._students_available_selections(student):
            self._allocate_selection(sel,call)
            # print(f"{call} --- Search selection {sel}")
            if self._set_complete() and self.total_serial() <= self.max_priority:
                found_list = SelectionList(self._copy_allocated_set())
                self.sets_found.append(found_list)
                self.max_priority = self.total_serial()
                print('+ '+str(self.total_serial()), end='', flush=True)

            elif self._selections_consistent(sel, self.max_priority):
                self._allocate_backtrack_group_student(mystudents, call)

            self.backtrack(call)

    def _selections_consistent(self, selection, max_priority):
        """Test whether we have hit any contraint

        Supervisor's max allocations: MAXPROJS
        Students without a project
        Sets no longer possible

        Heuristic total max priority > than already found

        :param selection: StudentSelection we have just attempted to allocate
        :param max_priority: Lowest sum of serials for a set that has already been identified
        """
        num_allocated_supervisor = self._supervisor_projects(
            selection.project.supervisor_crsid)

        return (len(num_allocated_supervisor) <= SelectionList.MAXPROJS
                and len(self.missing_students()) == 0
                and self._sets_still_possible()
                and self.total_serial() <= max_priority)

    def _allocate_backtrack(self, call=0):
        return self._allocate_backtrack_group_student(call)


# functions to read a CSV file containing the selections and generate the SelectionList
# CSV student and their choices
def project_sup(project_code):
    """Extracts a supervisor crsid from a project code"""
    match = re.search('^[A-Z]-([^-]*)-', project_code)
    return match.group(1) if match else ''


def create_get_project(project_list, project):
    """
    Adds the project to our project list if not exists
    returns the projectlist index
    """
    index = -1
    try:
        index = project_list.index(project)
    except ValueError:
        project_list.append(project)
        index = project_list.index(project)
    return index


def load_selections(filename):
    """
    Load selections from the by student list as gathered from IIBprojects app"""
    selections = SelectionList([])
    students = []
    projects = []

    # Tidy these constants up, and where this function goes
    NUM_PROJECTS = 1
    NUM_SELECTIONS = 1
    SELECTION_COLS = [5, 6, 7, 8, 9]
    rows = 0

    with open(filename, newline='', encoding='utf8') as csvfile:
        selectionreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in selectionreader:
            rows += 1
            if rows == 1:
                continue

            new_student = Student(row[0])
            students.append(new_student)
            for sel_row in SELECTION_COLS:
                if row[sel_row]:
                    # Only if the project is not in our project list!
                    # temporaray project to test whether project exists (by project_code)
                    # We will be wasting project_ids
                    tmp_project = Project(NUM_PROJECTS, project_sup(
                        row[sel_row]), row[sel_row])
                    proj_index = create_get_project(projects, tmp_project)

                    selections.append(
                        StudentSelection(
                            NUM_SELECTIONS,
                            sel_row-SELECTION_COLS[0]+1,
                            new_student,
                            projects[proj_index]))
                    NUM_SELECTIONS += 1
                    NUM_PROJECTS += 1

    return selections
