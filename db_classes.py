class Student:
    def __init__(self, first_name, last_name, email, grade_adj, id_num):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.class_list = []
        self.electives_taken = 0
        self.core_classes = []
        self.age = 0 # age in semesters
        self.passed_classes = []
        self.course_history = []
        self.grade_adj = grade_adj
        self.id_num = id_num
        self.status = "in progress"


    def add_course(self, course):
        self.class_list.append(course)
        if course.grade >= 60:
            self.passed_classes.append(course.name)
        self.course_history.append(course)

    def check_prereqs(self, prereqs):
        if prereqs == ['']:
            return True
        for req in prereqs:

            if req in self.passed_classes:
                continue
            elif "^" in req:
                or_reqs = req.split("^")
                fail = True
                for or_req in or_reqs:
                    if or_req in self.passed_classes:
                        fail = False
                if fail:
                    return False
                else:
                    continue
            else:
                return False
        return True

    def check_bonus(self, prereqs):
        if prereqs == ['']:
            return False
        for req in prereqs:

            if req in self.passed_classes:
                continue
            elif "^" in req:
                or_reqs = req.split("^")
                fail = True
                for or_req in or_reqs:
                    if or_req in self.passed_classes:
                        fail = False
                if fail:
                    return False
                else:
                    continue
            else:
                return False
        return True


    def adjust_grade(self, course, course_count):
        grade_adjust = float(course[1])
        if (course[3] == 1 and course_count >= 5) or course_count > 5:
            grade_adjust -= .1

        if self.check_bonus(course[5].split(";")): #check fo bonus classes
            grade_adjust += .1
            #print("Bonus :" + course[0])
        return grade_adjust


class Course:
    def __init__(self, name, grade, semester, type, prereqs=None):
        self.name = name
        self.grade = grade
        self.semester = semester
        self.type = type

        if prereqs is None:
            self.prereqs = []
        else:
            self.prereqs = prereqs

    def load_pre_reqs(self, prereqs):
        for course in prereqs:
            self.prereqs.append(course)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self.name == other.name

    def __ne__(self, other):
        """Override the default Unequal behavior"""
        return self.name != other.name