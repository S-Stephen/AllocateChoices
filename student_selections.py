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
        self.allow_multiple = True

    def __hash__(self) -> int:
        return self.proj_id

    def __str__(self) -> str:
        return str(self.proj_id)+" "+self.project_code+" "+self.supervisor_crsid

    def __eq__(self, other):
        return self.project_code == other.project_code

    # TODO LP specific
    def lp_safe(self):
        """
        Returns a label safe for use in lp-solve
        """
        return self.project_code.replace("-", "_")

    def restrict_multiple(self):
        """
        Prevent the project being allocated multiple times
        """
        self.allow_multiple = False

    def set_allow_multiple(self):
        """
        Allow this project to be allocated multiple times
        """
        self.allow_multiple = True

class StudentSelection:
    """Student choice"""

    def __init__(self, sel_id, serial, student, project) -> None:
        self.sel_id = sel_id
        self.serial = serial
        self.student = student
        self.project = project
        self.allocated = False
        # TODO This relates to the backtack search method only - should not be here
        self.unavailable = 0

    def set_unavailable(self, call):
        """Mark this selection as hidden
        The value it is marked as is the callid to the allocate method (for backtracking)"""
        self.unavailable = call

    # TODO relates to backtrack - should not be here
    def is_available(self):
        """Is this selection still active
        TODO refactor to be available
        """
        return self.unavailable == 0

    # TODO relates to backtrack - should not be here
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

    # TODO This relates to lp_solve only - should not be here
    def lp_variable(self):
        """A variable string that can be used in lp_solver files"""
        return self.student.crsid+"_"+self.project.lp_safe()

Student = namedtuple("Student", "crsid")

class SelectionList(list):
    """
    A list of Selections

    These may form a 'valid' set
    or
    They may be the full set of selections
    """

    def __init__(self, *args):
        """Provide the constructor with a list of Selections"""
        list.__init__(self, *args)

    def students(self):
        """Returns all students involved in selections"""
        return set(list(map(lambda selection: selection.student, self)))

    def allocated_selections(self):
        """Selections allocated"""
        return list(filter(lambda selection: selection.is_allocated(), self))

    def unallocated_selections(self):
        """Selections allocated"""
        return list(filter(lambda selection: selection.is_allocated() is False, self))

    def print_allocated_set(self):
        """Displays the allocation set found
        TODO put in an array of valid sets - to then search for BEST"""
        for sel in self.allocated_selections():
            print(sel)

    def projects_allocated_multiple(self,n):
        """
        Report of the projects that have been allocated n time

        :param n: number of times the project has been allocated
        """
        project_count={}
        for sel in self.allocated_selections():
            if sel.project in project_count:
                project_count[sel.project]+=1
            else:
                project_count[sel.project]=1

        return dict(filter(lambda elem: elem[1] >= n, project_count.items()))

    def single_student_projects(self):
        """
        Return the projects which have been marked as single student
        """
        return set(
            list(
                filter(lambda selection: selection.allow_multiple is False, \
                    map(lambda sel: sel.project, self))))

    def add_single_student_project(self,project_lp_safe):
        """
        Adds a project to the single student list

        :param project_lp_safe: The lp safe label for this project
        """
        # find the project
        selections = self.project_selections(project_lp_safe)
        # hopefully we have one!
        try:
            selections[0].project.restrict_multiple()
        except:
            pass

    def add_multiple_student_project(self,project_lp_safe):
        """
        Removes a project from the single student list

        :param project_lp_safe: The lp safe label for this project
        """
        # find the project
        selections = self.project_selections(project_lp_safe)
        # hopefully we have one!
        try:
            selections[0].project.set_allow_multiple()
        except:
            pass


    def supervisor_selections(self,crsid):
        """
        The selections associated to this supervisor

        :param crsid: supervisor crsid
        """
        return list(filter(lambda sel:
                           sel.project.supervisor_crsid == crsid, self))

    def student_selections(self,crsid):
        """
        The selections associated to this student

        :param crsid: student crsid
        """
        return list(filter(lambda sel:
                           sel.student.crsid == crsid, self))


    def project_selections(self,project_lp_safe):
        """
        The selections associated to this student

        :param project_safe: safe lp label for project
        """
        return list(filter(lambda sel:
                           sel.project.lp_safe() == project_lp_safe, self))

    def supervisor_projects(self, crsid):
        """returns the list of projects this supersior has allocated"""
        return list(filter(lambda sel:
                           sel.project.supervisor_crsid == crsid and sel.allocated is True, self))



    def _serials(self):
        """
        the array of serials associated to the set
        """
        return list(map(lambda sel: sel.serial,
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

    def clear_allocations(self):
        """Remove all the allocations made for this set"""
        for sel in self:
            sel.unallocate()


    def load_selections(self,filename):
        """
        Load selections from the by student list as gathered from IIBprojects app"""
        # self.selections = SelectionList([])
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

                        self.append(
                            StudentSelection(
                                NUM_SELECTIONS,
                                sel_row-SELECTION_COLS[0]+1,
                                new_student,
                                projects[proj_index]))
                        NUM_SELECTIONS += 1
                        NUM_PROJECTS += 1

class SelectionBacktrackSolver():
    """
    Solve the allocation uisng backtrack algorithm
    """

    TIMEOUT = 10
    MAX_PROJ_STUDENTS = 1
    MAXPROJS = 4

    def __init__(self) -> None:
        self.selection_list = SelectionList([])
        self.sets_found = []
        self.max_priority = 1000000000

    def load_selections(self,filename):
        """
        Load selections from the by student list as gathered from IIBprojects app
        """
        self.selection_list.load_selections(filename)

    def _timeout_handler(self, signum, frame):
        print(f"Timeout ({self.TIMEOUT}) occured {signum} {frame}")
        raise Exception("TIMEOUT")

    def students(self):
        """Returns the students in the selection list"""
        return self.selection_list.students()

    def _sets_still_possible(self):
        """Are selection sets still possible for this set"""
        return len(self.selection_list.allocated_selections())+len(self._available_students()) == \
            len(self.students())

    def _selections_consistent(self, selection, max_priority):
        """Test whether we have hit any contraint

        Supervisor's max allocations: MAXPROJS
        Students without a project
        Sets no longer possible

        Heuristic total max priority > than already found

        :param selection: StudentSelection we have just attempted to allocate
        :param max_priority: Lowest sum of serials for a set that has already been identified
        """
        num_allocated_supervisor = self.selection_list.supervisor_projects(
            selection.project.supervisor_crsid)

        return (len(num_allocated_supervisor) <= self.MAXPROJS
                and len(self.missing_students()) == 0
                and self._sets_still_possible()
                and self.selection_list.total_serial() <= max_priority)

    def _prune_project(self, project, call=1):
        """Prune all unallocated selections containing the project

        :param project: The project that has been allocated elsewhere
        :type project: Project
        :param call: The call we are pruning the student from
        :type call: integer
        """
        # allow for two selections per project so first find number already allocated
        if (len(list(filter(lambda sel: (sel.project.proj_id == project.proj_id and
                                         sel.allocated is True), self.selection_list))) >= \
                                             self.MAX_PROJ_STUDENTS):

            for sel in list(filter(lambda selection:
                                   (selection.unavailable == 0 and
                                    selection.allocated is False and
                                    selection.project.proj_id == project.proj_id), \
                                        self.selection_list)):
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
                                selection.student.crsid == student.crsid), self.selection_list)):
            sel.set_unavailable(call)

    def _set_complete(self):
        """Have we completed a selection set"""
        return len(self.selection_list.allocated_selections()) == len(self.students())

    def _available_selections(self):
        """Selections still active/available"""
        return list(filter(lambda selection: selection.is_available() is True, self.selection_list))

    def _print_available_selections(self):
        """For debug print out the list of selections we still need to allocate"""
        for sel in self._available_selections():
            print(sel)

    def _available_students(self):
        """A list of available students left"""
        return set(list(map(lambda selection: selection.student, self._available_selections())))

    def missing_students(self):
        """Report the missing students
        Those students not in our selection set (ie their selections are still available)
        :param students: list of students to search for
        """
        available_selections = self._available_selections()
        students_not_allocated = list(
            map(lambda selection: selection.student, available_selections))
        allocated_selections = self.selection_list.allocated_selections()
        students_allocated = list(
            map(lambda selections: selections.student, allocated_selections))
        students_in_selections = [*students_allocated, *students_not_allocated]
        return set(self.students()) ^ set(students_in_selections)

    def _allocate_selection(self, selection, call):
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

        def _count_selections(supervisor_count, sel):
            if sel.project.supervisor_crsid in supervisor_count:
                supervisor_count[sel.project.supervisor_crsid].append(sel)
            else:
                supervisor_count[sel.project.supervisor_crsid] = [sel]
            return supervisor_count

        # can we reduce the size of the set by allocating any serial 1 choices
        # where the max number of projects for the supervisor > number of selections
        selection_count = reduce(_count_selections, self.selection_list, {})

        # Find selections that can be allocated
        # The supervisor has < MAXPROJS selections
        # The selections involved are not for the same project
        can_allocate = list(
            dict(
                filter(
                    lambda elem: len(elem[1]) <= self.MAXPROJS and
                    len(list(map(lambda sel: sel.project.proj_id, elem[1]))) ==
                    len(set(map(lambda sel: sel.project.proj_id, elem[1]))),
                    selection_count.items())).values())

        # Allocate the selections in our list that are first choice
        flat_list = list(filter(lambda sel: sel.serial == 1,
                                [item for sublist in can_allocate for item in sublist]))
        for sel in flat_list:
            if sel.serial == 1:
                self._allocate_selection(sel, 1)

        if self._set_complete():
            found_list = SelectionList(self._copy_allocated_set())
            self.sets_found.append(found_list)
            print('+', end='', flush=True)

    def _copy_allocated_set(self):
        """return a SelectionList of selections that have been allocated"""
        return copy.deepcopy(self.selection_list.allocated_selections())


    def _popular_projects(self, maxserial=100):
        """returns the most popular project ids in the selections

        :param maxserial: the max serial to consider

        Use this to identify the next project to remove?
        """
        filtered_by_serial = list(filter(lambda sel: sel.is_available(
        ) and sel.serial <= maxserial and sel.allocated is False, self.selection_list))

        filtered_projects = Counter(
            list(map(lambda sel: sel.project, filtered_by_serial)))
        # dict(projectid) = num

        return sorted(filtered_projects, key=Counter(filtered_projects).get, reverse=True)
        # sorted(filtered_projects.items(), key=lambda pair: pair[1], reverse=True)
        # orderby num desc -> take first



    def _students_available_selected_project(self, project):
        """A list of students who have selected a project

        :param project: The project we are interested in
        :param project: Project
        """
        available_selections = self._available_selections()
        selections_with_project = filter(
            lambda sel: sel.project.proj_id == project.proj_id, available_selections)
        return list(map(lambda selection: selection.student, selections_with_project))

    def students_by_popular_projects(self):
        """
        Join the list of students with the list of popular projects

        return the students in the order of selections including popular projects
        """
        students_crsids = []
        students = []
        for project in self._popular_projects():
            # if len(students) < 30:
            #    print(project)
            for student in self._students_available_selected_project(project):

                # if len(students) < 10:
                #    print(student)
                if student.crsid not in students_crsids:
                    students_crsids.append(student.crsid)
                    # pop will provide students selecting the most popular
                    # students.insert(0,student)
                    # pop  will provide students selecting the least popular
                    students.append(student)

        # print(students)
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
            self._allocate_backtrack_group_student(students, 2)
        except Exception as exc:
            print(f"Exception occured (timeout?): {exc}")

        print(f"\n{len(self.sets_found)} sets found")

        return self.sets_found

    def backtrack(self, call=0):
        """Re-instate the selections but not if it was the one we tried to allocate"""
        # unprune
        for sel in list(filter(lambda selection:
                               (selection.unavailable >= call), self.selection_list)):

            if sel.unavailable == call and sel.is_allocated():
                # keep not available - tried and failed
                sel.unallocate()
            else:
                sel.set_available()


    def _students_available_selections(self, student):
        """The available selections for this student"""
        return filter(lambda sel: sel.student == student, self._available_selections())

    #def _projects_available_selections(self, project):
    #    """The available selections for this student"""
    #    return filter(lambda sel: sel.project == project, self._available_selections())

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
            self._allocate_selection(sel, call)
            # print(f"{call} --- Search selection {sel}")
            if self._set_complete() and self.selection_list.total_serial() <= self.max_priority:
                found_list = SelectionList(self._copy_allocated_set())
                self.sets_found.append(found_list)
                self.max_priority = self.selection_list.total_serial()
                print('+ '+str(self.selection_list.total_serial()), end='', flush=True)

            elif self._selections_consistent(sel, self.max_priority):
                self._allocate_backtrack_group_student(mystudents, call)

            self.backtrack(call)

    def _allocate_backtrack(self, call=0):
        return self._allocate_backtrack_group_student(call)

class SelectionLPSolver():
    """
    Solve the allocation of choices using an LP solver
    """
    MAX_STUDENT_PROJECTS = 2
    MAX_PROJECTS_SUP = 4

    def __init__(self) -> None:
        self.selection_list = SelectionList([])

    def load_selections(self,filename):
        """
        Load selections from the by student list as gathered from IIBprojects app
        """
        self.selection_list.load_selections(filename)

    def projects_allocated_multiple(self,n):
        """
        Report of the projects that have been allocated n time

        :param n: number of times the project has been allocated
        """
        return self.selection_list.projects_allocated_multiple(n)

    def single_student_projects(self):
        """
        Return the projects which have been marked as single student
        """
        return self.selection_list.single_student_projects()

    def add_single_student_project(self,project_lp_safe):
        """
        Adds a project to the single student list

        :param project_lp_safe: The lp safe label for this project
        """
        self.selection_list.add_single_student_project(project_lp_safe)

    def add_multiple_student_project(self,single_student_project):
        """
        Removes a project from the single student list

        :param project_lp_safe: The lp safe label for this project
        """
        self.selection_list.add_multiple_student_project(single_student_project)

    def clear_allocations(self):
        """Remove all the allocations made for this set"""
        self.selection_list.clear_allocations()

    # TODO move to LP Solver
    def get_selection_by_lp_variable(self,lp_variable):
        """
        Retrieves the selection by the safe_lp label
        """
        res = list(filter(lambda sel:
                           sel.lp_variable() == lp_variable, self.selection_list))
        # handle empty array
        return res[0]

    def generate_solve_file(self, filename='lp_solve.lp'):
        """
        Creates an LP file
        This can be run externally or using the commands in this class
        """
        #MAX_PROJECTS_SUP = 4
        #self.MAX_STUDENT_PROJECTS = 2

        objective_function = "min: "

        # The selections
        declarations = []

        # miniise me
        priorities = []
        # total per project
        # total per supervisor
        # total per student
        student_constraints = {}
        project_constraints = {}
        project_single_constraints = {}
        supervisor_constraints = {}

        with open(filename, 'w', encoding='utf-8') as lpfile:
            selection_list = self.selection_list
            for selection in selection_list.unallocated_selections():
                priorities.append(str(selection.serial) +
                                " "+selection.lp_variable())
                declarations.append(f"int {selection.lp_variable()}")

                if selection.project.supervisor_crsid not in supervisor_constraints:
                    crsid=selection.project.supervisor_crsid
                    selections = list(
                        map( lambda sel: sel.lp_variable(), \
                                selection_list.supervisor_selections(crsid) ))
                    supervisor_constraints[crsid] = selections

                if selection.student.crsid not in student_constraints:
                    crsid = selection.student.crsid
                    selections = map(
                        lambda sel: sel.lp_variable(), \
                            selection_list.student_selections(crsid))
                    student_constraints[crsid] = selections

                if selection.project.allow_multiple is True and \
                    selection.project.lp_safe() not in project_constraints:
                    project = selection.project.lp_safe()
                    selections = list(
                        map( lambda sel: sel.lp_variable(), \
                            selection_list.project_selections(project)))
                    project_constraints[project] = selections

                if selection.project.allow_multiple is False and \
                    selection.project.lp_safe() not in project_single_constraints:
                    project = selection.project.lp_safe()
                    selections = map( lambda sel: sel.lp_variable(), \
                        selection_list.project_selections(project))
                    project_single_constraints[project] = selections


            objective_function += ' + '.join(priorities)

            lpfile.write("\n/*Minimise this*/\n")
            lpfile.write(objective_function+";\n")

            lpfile.write("\n/*ONE allocation per student*/\n")
            lpfile.write('\n'.join(list(map( \
                lambda arr: (' + '.join(arr))+' = 1;', \
                    list(student_constraints.values()))))+'\n')

            lpfile.write(f"\n/*MAX projects per supervisor: {self.MAX_PROJECTS_SUP}*/\n")
            supervisor_constraints=dict(
                filter(lambda elem: len(elem[1]) > self.MAX_PROJECTS_SUP,\
                    list(supervisor_constraints.items())))
            lpfile.write('\n'.join(
                list(map(
                    lambda arr: (' + '.join(arr))+f" <= {self.MAX_PROJECTS_SUP};", \
                        supervisor_constraints.values())))+'\n')

            lpfile.write(f"\n/*MAX students per project: {self.MAX_STUDENT_PROJECTS}*/\n")
            project_constraints=dict(filter(
                lambda elem: len(elem[1]) > self.MAX_STUDENT_PROJECTS,\
                    list(project_constraints.items())))
            lpfile.write('\n'.join(list(map(
                lambda arr: (' + '.join(arr))+f" <= {self.MAX_STUDENT_PROJECTS};", \
                    list(project_constraints.values()))))+'\n')

            lpfile.write("\n/*Restricted to single project per student: */\n")
            lpfile.write('\n'.join(list(map(
                lambda arr: (' + '.join(arr))+" <= 1;", \
                    list(project_single_constraints.values()))))+'\n')

            lpfile.write("\n/*selection declarations*/\n")
            lpfile.write((';\n'.join(declarations))+';\n')

            lpfile.close()

# functions to read a CSV file containing the selections and generate the selection_list
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
