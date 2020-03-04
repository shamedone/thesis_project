from random import randint
import utils

class Student:
    def __init__(self, id_num, sex, ethnic, age, resident_status, standing, admin_descript):
        self.sex = sex #varchar
        self.ethnic = ethnic #varchar
        self.age = age #archar
        self.resident_status = resident_status#varchar
        self.standing = standing #varchar
        self.passed_classes = [] # do we need both of these? skip
        self.course_history = [] # do we need we both? we have course history? skip
        self.id_num = id_num #varchar
        self.status = "dropout"  #TODO find all student.type, fill in all data here
        self.course_seq_dict = {}
        self.sem_avg_grades = {} #?
        self.sem_seq_dict = {} #?
        self.unique_courses = {}
        self.major = "" #varchar
        self.admin_descript = admin_descript #varchar
        self.fp_dict = {}
        self.spring_19_flag = False
        self.pred = "NA"
        self.pred_class = "NA"
        self.final_gpa = 0
        self.type_descript = "NA"
        self.final_cs_gpa = 0
        self.serious = True
        self.prep_assess = "OK"
        self.type_descript_summary = "0"
        self.prep_assess_summary = "0"
        self.seq_sim_score = 0
        self.units_by_college_totals = {}
        self.units_by_dept_totals = {}
        self.dropout_semester = 0
        self.first_sem = 90000
        self.prior_units = 0
        self.final_gen_gpa = 0

    @staticmethod
    def check_course_name(course):
        if course.name == "CSC313":
            course.name = "CSC220"

        if course.name == "CSC330":
            course.name = "CSC230"

        if course.name == "CSC640":
            course.name = "CSC648"
        return

    def add_course(self, course):
        #self.check_course_name(course)
        if course.name in self.unique_courses:
            old_course = self.unique_courses[course.name]
            course.repeat += 1
            course.prior_id = old_course.ref_id
            course.past_attempts.append(old_course)
        self.unique_courses[course.name] = course

        if course.grade_gpu >= .07:
            self.passed_classes.append(course.name)
        utils.sum_to_dict(course.college, 1, self.units_by_college_totals)
        utils.sum_to_dict(course.department, 1, self.units_by_dept_totals)

        if course.semester < self.first_sem:
            self.first_sem = course.semester
            check = course.total_units - course.sfsu_units
            if check > 0:
                self.prior_units = int(check)

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
        grade_adjust += (randint(-20,20) / 1000) #vary course grade results slightly
        if (course[3] == 1 and course_count >= 5) or course_count > 5:
            grade_adjust -= .1

        if self.check_bonus(course[5].split(";")): #check fo bonus classes
            grade_adjust += .1
            #print("Bonus :" + course[0])
        return grade_adjust

    def calc_semester_load(self):
        load_dict = {}
        for sem in self.sem_seq_dict:
            semester = self.sem_seq_dict[sem]
            load_dict[semester] = len(self.course_seq_dict[sem])
        for course in self.course_history:
            course.semester_load = load_dict[course.semester]


class Course:
    def __init__(self, name, grade_str, semester, student_age, student_standing, ref_id, student_id, term_gpa, sfsu_gpa, \
                 type, grad_flag, term_units, sfsu_units, spring_flag, college, department, total_units, prereqs=None):
        self.name = name #varchar
        self.grade_str = grade_str
        self.grade = utils.str_grade_to_int(self.grade_str) #int
        self.grade_gpu = utils.str_grade_to_gpu(self.grade_str)
        #self.grade = utils.str_grade_to_int(self.grade_str) #int
        self.semester = semester #varchar
        self.student_age = student_age
        self.student_standing = student_standing
        self.repeat = 0 #int indicating number of times the course has been repeated.
        self.past_attempts = []
        self.prior_id = 0 #varchar
        self.ref_id = ref_id #varchar
        self.student_id = student_id
        self.term_gpa = term_gpa
        self.sfsu_gpa = sfsu_gpa
        self.term_units = term_units
        self.sfsu_units = sfsu_units
        self.course_type = type
        self.grad_flag = grad_flag
        self.spring_19_flag = spring_flag
        self.seq_int = 0
        self.pred = 0
        self.pred_class = "NA"
        self.tech_load = 0
        self.ge_load = 0
        self.orig_name = name
        self.college = college
        self.department = department
        self.total_units = total_units


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


class SmallCourse:
    def __init__(self):
        return