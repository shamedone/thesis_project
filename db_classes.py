import utils

class Student:
    def __init__(self, id_num, sex, ethnic, age, resident_status, standing, admin_descript, entry_major, final_major,
                 spring_19_major):
        self.sex = sex #varchar
        self.ethnic = ethnic #varchar
        self.age = age #archar
        self.resident_status = resident_status#varchar
        self.entry_standing = standing #varchar
        self.final_standing = standing #varchar
        self.passed_classes = []
        self.course_history = []
        self.id_num = id_num #varchar
        self.status = "dropout"  #TODO find all student.type, fill in all data here
        self.course_seq_dict = {}
        self.sem_avg_grades = {} #?
        self.sem_seq_dict = {} #?
        self.unique_courses = {}
        self.major = "CSC" #varchar
        self.admin_descript = admin_descript #varchar
        self.fp_dict = {}
        self.spring_19_flag = False
        self.spring_19_major = spring_19_major
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
        self.entry_major = entry_major
        self.final_major = final_major
        self.global_status = "non_cs_or_dropout"
        self.missing_classes = ""
        self.total_focus_dict = {}

    #Change some names to match course descriptions
    @staticmethod
    def check_course_name(course):
        # Chose to not include CSC 313 as syllabus appears to different
        #if course.name == "CSC313":
        #    course.name = "CSC220"

        if course.name == "CSC330":
            course.name = "CSC230"

        if course.name == "CSC640":
            course.name = "CSC648"
        return


    def add_course(self, course):
        self.check_course_name(course)
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
            self.entry_standing = course.student_standing
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

    def calc_semester_load(self):
        load_dict = {}
        for sem in self.sem_seq_dict:
            semester = self.sem_seq_dict[sem]
            load_dict[semester] = len(self.course_seq_dict[sem])
        for course in self.course_history:
            course.semester_load = load_dict[course.semester]

        return


    def update_final_semester (self):
        if self.dropout_semester == 0:
            raise Warning("Dropout semesters not calculated. Run label dropouts first")
        for course in self.course_history:
            if course.semester == self.dropout_semester:
                course.isfinal_semester = True

        return

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
        self.course_focus_dict = {}
        self.isfinal_semester = False


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