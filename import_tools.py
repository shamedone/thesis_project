import utils
import sf_coder
from db_classes import Course
from db_classes import Student
from dataset_stage import calc_sem_avg_grade
from copy import deepcopy

#adds course to student object
def add_to_student_obj(student_id, course, dict_, student_data, kwargs):
    if student_id in dict_:
        temp = dict_[student_id]
        temp.add_course(course)
        if len(kwargs) > 0:  # if there are keyword args then its a sfsu type with more data
            if temp.age > int(student_data[kwargs["age"]]):
                temp.age = int(student_data[kwargs["age"]])
            if temp.final_standing > int(student_data[kwargs["standing"]]):
                temp.final_standing = int(student_data[kwargs["standing"]])
            if course.grad_flag == "Y":
                if "Computer Sci" in temp.final_major:
                    temp.status = "graduated_cs"
                    temp.global_status = "cs"
                else:
                    temp.status = "graduated_non_cs"
            if course.spring_19_flag == "Y":
                temp.spring_19_flag = True
                print(temp.spring_19_major)
                if "Computer Sci" in temp.spring_19_major:
                    temp.status = "cs_in_progress"
                    temp.global_status = "cs"
                else:
                    temp.status = "maj_change_in_progress"
                    temp.spring_19_major = temp.final_major
        dict_[student_id] = temp
    else:
        if len(kwargs) == 0:  # if no kwargs then there is no data.
            student = Student(student_id, "na", "na", "na", "na", "na", "na")
        else:
            student = Student(student_id, int(student_data[kwargs["sex"]]), int(student_data[kwargs["ethnic"]]),
                              int(student_data[kwargs["age"]]), int(student_data[kwargs["resident_status"]]),
                              int(student_data[kwargs["standing"]]), int(student_data[kwargs["admin_descript"]]),
                              student_data[kwargs["entry_major"]], student_data[kwargs["final_major"]],
                              student_data[kwargs["spring_19_major"]])
        student.add_course(course)
        dict_[student_id] = student

#builds student dict from raw file
def build_student_dict(student_data, **kwargs):
    #   returns dict of student objs, complete with course work.
    student_dict = {}
    used_ids = set()
    crs_type_look_up = utils.dict_from_file(
        "/Users/thomasolson/Documents/workspace/advising_revamp/course_type_lookup.csv", 3, 4, "\n", ",", True)
    for data in student_data:
        data = sf_coder.translate_sfsu_data(data)
        student_id = data[kwargs["student_id"]]
        i = 0
        if len(kwargs) < 3: #less than 3 means no special type.
            course = Course(data[kwargs["class_int"]], int(data[kwargs["grade_int"]])*10, data[kwargs["year_int"]], 0,
                            0, 0)
        else:
            name_check = data[kwargs["crs_abbr"]]+str(data[kwargs["crs_num"]])
#            if "CSC" not in name_check:
#            if "CSC" not in name_check and "PHYS" not in name_check and "MATH" not in name_check:
#                continue
            course_id = student_id + str(i)
            while course_id in used_ids:
                i += 1
                course_id = student_id + str(i)
            used_ids.add(course_id)
            course = Course(data[kwargs["crs_abbr"]] + str(data[kwargs["crs_num"]]), data[kwargs["grade_str"]],
                            int(data[kwargs["year_int"]]),int(data[kwargs["age"]]), int(data[kwargs["standing"]]),
                            course_id, student_id, float(data[kwargs["term_gpa"]]), float(data[kwargs["sfsu_gpa"]]),
                            crs_type_look_up[data[kwargs["crs_abbr"]]+str(data[kwargs["crs_num"]])],
                            data[kwargs["grad_flag"]], float(data[kwargs["term_units"]]),
                            float(data[kwargs["sfsu_units"]]), data[kwargs["spring_19_flag"]],
                            data[kwargs["crs_college_long"]], data[kwargs["crs_dept_long"]],
                            float(data[kwargs["total_units"]]))

        add_to_student_obj(student_id, course, student_dict, data, kwargs)
    return student_dict




#saves student to database
def persist_student_data(students):
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "insert into student_data (student_id, sex, age, resident_status, entry_standing, final_standing, status, major, admin_descript," \
          "spring_19_flag, ethnicity, dropout_semester, first_semester, prior_units, type_descript, type_descript_summary," \
          "prep_assess, prep_assess_summary, final_gpa, final_cs_gpa, final_gen_gpa, entry_major, final_major, spring_19_major," \
          "global_status, missing_classes, serious_student) values " \
          "(%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    for student in students:
        key = (student.id_num, student.sex, student.age, student.resident_status, student.entry_standing, student.final_standing,
               student.status, student.major, student.admin_descript, student.spring_19_flag, student.ethnic, student.dropout_semester,
               student.first_sem, student.prior_units, student.type_descript, student.type_descript_summary, student.prep_assess,
               student.prep_assess_summary, student.final_gpa, student.final_cs_gpa, student.final_gen_gpa, student.entry_major,
               student.final_major, student.spring_19_major, student.global_status, student.missing_classes, student.serious)
        cursor.execute(sql, key)
        persist_class_data(cnx, student.course_history)
    cnx.commit()
    cursor.close()
    cnx.close()

#saves course data to database
def persist_class_data(cnx, course_data):
    cursor = cnx.cursor(buffered=True)
    sql = "insert into course_data (ref_id, course_name, grade, semester, student_age, student_standing, repeat_, " \
          "prior_id, student_id, grade_str, term_gpa, sfsu_gpa, term_units, sfsu_units, grad_flag, " \
          "spring_19_flag, seq_int, type, college, department, tech_load, ge_load, is_final_semester) values"\
          "(%s, %s, %s, %s,%s,%s,%s,%s,%s,%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for course in course_data:
        key = (course.ref_id, course.name, course.grade, course.semester, course.student_age, course.student_standing,
               course.repeat, course.prior_id, course.student_id, course.grade_str,
               course.term_gpa, course.sfsu_gpa, course.term_units, course.sfsu_units, course.grad_flag,
               course.spring_19_flag, course.seq_int, course.course_type, course.college, course.department,
               course.tech_load, course.ge_load, course.isfinal_semester)
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()


def update_student_gpa(gpa_dict):
    #  TODO part of init
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "update student_data set final_gpa = %s where student_id = %s"
    for gpa in gpa_dict:
        key = (gpa_dict[gpa], gpa)
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()
    cnx.close()


def update_student_cs_gpa(gpa_dict):
    #  TODO part of init
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "update student_data set final_cs_gpa = %s where student_id = %s"
    for gpa in gpa_dict:
        key = (gpa_dict[gpa], gpa)
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()
    cnx.close()


def update_course_loads(course_ids):
    #  TODO part of init
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "update course_data set ge_load = %s, tech_load = %s where ref_id = %s"
    for sets in course_ids:
        set_ = course_ids[sets]
        key = (set_[0], set_[1], sets)
        cursor.execute(sql, key)
    cursor.close()
    cnx.commit()
    cnx.close()


def update_type_status(labels):
    #  TODO part of init
    sql = "update student_data set type_descript = %s where student_id = %s"
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    for label in labels:
        students = labels[label]
        for student in students:
            key = (label, student.id_num)
            cursor.execute(sql, key)
            cnx.commit()
    cursor.close()
    cnx.close()

#pulls student data from database to create student objects
def pull_student_data(cnx, **kwargs):
    student_dict = {}
    student_list = []
    cursor = cnx.cursor(buffered=True)
    sql = "select * from student_data"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        temp_student = Student(result[0], result[1], result[9], result[2], result[3], result[4], result[7], result[22],
                               result[23], result[24])
        temp_student.status = result[5]
        temp_student.major = result[6]
        temp_student.spring_19_flag = result[8]
        temp_student.final_gpa = result[10]
        temp_student.type_descript = result[11]
        temp_student.final_cs_gpa = result[12]
        temp_student.prep_assess = result[13]
        temp_student.prep_assess_summary = result[14]
        temp_student.type_descript_summary = result[15]
        temp_student.serious = result[16]
        temp_student.dropout_semester = result[17]
        temp_student.first_sem = result[18]
        temp_student.prior_units = result[19]
        temp_student.final_gen_gpa = result[20]
        temp_student.final_standing = result[21]
        temp_student.global_status = result[25]
        temp_student.missing_classes = result[26]


        student_list.append(temp_student)
    cursor.close()

    for student in student_list:
        use = True
        if 'admin' in kwargs:
            if student.admin_descript != kwargs['admin']:
                use = False
        if 'status' in kwargs:
            if student.status != kwargs['status']:
                use = False
        if use:
            student_dict[student.id_num] = student

    return student_dict

#pulls course data from database for students and adds to student object
def pull_course_data(cnx, students):
    cursor = cnx.cursor(buffered=True)
    sql = "select * from course_data where student_id = %s"
    for student in students:
        key = (student,)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        # name, grade_str, semester, student_age, student_standing, ref_id, student_id, term_gpa, sfsu_gpa,
        #            type, grad_flag, term_units, sfsu_units, spring_flag, prereqs=None):
        for result in results:
            temp_course = Course(result[1], result[9], result[3], result[4], result[5], result[0], result[8],
                                 result[10], result[13], result[17], result[14], result[11], result[12], result[15],
                                 result[22], result[23], result[24])
    #        temp_course.repeat = result[6]
    #        temp_course.prior_id = result[7]
            temp_course.seq_int = result[16]
            temp_course.tech_load = result[18]
            temp_course.ge_load = result[19]
            temp_course.equiv_name = result[20]
            temp_course.isfinal_semester = result[25]

            temp_student = students[temp_course.student_id]
            temp_student.add_course(temp_course)
            students[temp_student.id_num] = temp_student

    list_output = []
    for student_id in students:
        student = students[student_id]
        for course in student.course_history:
            seq_int = course.seq_int
            if seq_int not in student.course_seq_dict:
                student.sem_seq_dict[seq_int] = course.semester
                student.course_seq_dict[seq_int] = [course]
            else:
                temp = student.course_seq_dict[seq_int]
                temp.append(course)
                student.course_seq_dict[seq_int] = temp
        list_output.append(student)


    calc_sem_avg_grade(list_output)
    calc_focus_dicts(list_output)
    cursor.close()
    return list_output

#overview function for importing student data from database, first calls student data and then course to create list of student objects
def package_student_data(**kwargs):
    print("hi")
    cnx = utils.get_connection(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY")
    students = pull_student_data(cnx, **kwargs)
    packaged_data = pull_course_data(cnx, students)
    cnx.close()
    return packaged_data


def get_course_names_by_type():
    course_cat = {
        "core": [],
        "elective": [],
        "ge": []
    }
    cnx = utils.get_connection(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY")
    cursor = cnx.cursor(buffered=True)
    sql = "select distinct(course_name),type from course_data"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        temp = course_cat[result[1]]
        temp.append(result[0])
        course_cat[result[1]] = temp

    return course_cat


def get_class_prereqs():
    prereq_cat = {}
    crs_list = utils.list_from_file("./cs_prereqs", "\n", ",", False)
    for crs in crs_list:
        name = crs[0]
        if "^" in crs[1]:
            preq = crs[1].split("^")
        else:
            preq = crs[1].split(";")
        prereq_cat[name] = preq
    return prereq_cat


def update_student_prep(change_list):
    #  TODO make part of init
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "update student_data set prep_assess = %s where student_id = %s"
    for change in change_list:
        print(change.prep_assess)
        key = (change.prep_assess, change.id_num)
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()
    cnx.close()
    return

def update_student_serious(change_list):
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "update student_data set serious_student = %s where student_id = %s"
    for change in change_list:
        key = (True, change)
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()
    cnx.close()
    return


#builds dict for each student that counts how many courses they take in each college and department.
def calc_focus_dicts(students):

    for student in students:
        global_college_dict = {}
        global_dept_dict = {}
        semester_focus_dict = {}
        crs_seqs = student.course_seq_dict
        for x in range(1, len(crs_seqs)+1):
            courses = crs_seqs[x]
            college_dict = {}
            dept_dict = {}
            for crs in courses:
                utils.sum_to_dict(crs.department, 1, dept_dict)
                utils.sum_to_dict(crs.college, 1, college_dict)
                utils.sum_to_dict(crs.department, 1, global_dept_dict)
                utils.sum_to_dict(crs.college, 1, global_college_dict)
            temp = {}
            temp['college'] = college_dict
            temp['deptartment'] = dept_dict
            for crs in courses:
                crs.course_focus_dict = temp

            temp = {}
            temp['college'] = global_college_dict.copy()
            temp['deptartment'] = global_dept_dict.copy()
            semester_focus_dict[x] = temp
        student.total_focus_dict = semester_focus_dict
    return

#code to combine PHYS220/222 and PHYS230/232
def combine_phys(students):
    for student in students:
        update = False
        phys230_grade = 0
        phys232_grade = 0
        phys222_grade = 0
        phys220_grade = 0

        if "PHYS230" in student.unique_courses:
            phys230_grade = student.unique_courses["PHYS230"].grade
        if "PHYS232" in student.unique_courses:
            phys232_grade = student.unique_courses["PHYS232"].grade
        if "PHYS220" in student.unique_courses:
            phys220_grade = student.unique_courses["PHYS220"].grade
        if "PHYS222" in student.unique_courses:
            phys222_grade = student.unique_courses["PHYS222"].grade

        if phys232_grade > 0:
            phys230_combo_grade = round((phys230_grade * 3)/4 + (phys232_grade/4))
        else:
            phys230_combo_grade = phys230_grade

        if phys222_grade > 0:
            phys220_combo_grade = round((phys220_grade * 3)/4 + (phys222_grade/4))
        else:
            phys220_combo_grade = phys220_grade

        if phys230_combo_grade > 0:
            print(phys230_combo_grade)
            try:
                phys230_combo_course = deepcopy(student.unique_courses["PHYS230"])
            except:
                continue
            phys230_combo_course.name = "PHYS230COMBO"
            phys230_combo_course.grade = phys230_combo_grade
            phys230_combo_course.grade_str = utils.get_letter_grade(phys230_combo_grade)
            student.add_course(phys230_combo_course)


        if phys220_combo_grade > 0:
            print(phys220_combo_grade)

            try:
                phys220_combo_course = deepcopy(student.unique_courses["PHYS220"])
            except:
                continue
            phys220_combo_course.name = "PHYS220COMBO"
            phys220_combo_course.grade = phys220_combo_grade
            phys220_combo_course.grade_str = utils.get_letter_grade(phys220_combo_grade)
            student.add_course(phys220_combo_course)

    return students


preq_map = {
    "MATH227": ["MATH226"],
    "MATH324": ["MATH227"],
    "MATH325": ["MATH227"],
    "PHYS220": ["MATH226"],
#    "PHYS222": ["MATH226"],
    "PHYS230": ["PHYS220", "MATH227"],
#    "PHYS232": ["MATH227"],
    "CSC220": ["CSC210"],
    "CSC230": ["CSC210","MATH227"],
    "CSC256": ["CSC230"],
    "CSC300": ["CSC210"],
    "CSC340": ["CSC220","CSC230","MATH227"],
#    "CSC413": ["CSC220"],
    "CSC413": ["CSC340"],
    "CSC415": ["MATH324","PHYS230","CSC256","CSC340"],
    "CSC510": ["CSC340","MATH324"],
#

    "CSC520": ["CSC220","CSC230", "MATH325"],
    "CSC600": ["CSC413", "CSC510"],
#    "CSC648": ["CSC317","CSC413"],
    "CSC648": ["CSC413"],
    "CSC210": [],
#    "CSC317": ["CSC220"],
#    "CSC211": [""]
    "MATH226": []
    }
