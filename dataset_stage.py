import utils

core_set = {"MATH226", "MATH227","MATH324","MATH325","PHYS220","PHYS222","PHYS230","PHYS232"}
all_core_classes = {"MATH227","MATH324","MATH325","PHYS220","PHYS222","PHYS230","PHYS232","CSC220","CSC230","CSC256",
                    "CSC300","CSC340","CSC413","CSC415","CSC510","CSC520","CSC600","CSC648","CSC210","MATH226"}


#checks if students have taken a course provided in a list of couress
def variable_check(students, prep_courses):
    kept_students = []
    for student in students:
        accept = True
        for course in prep_courses:
            if course not in student.unique_courses:
                accept = False
        if accept:
            kept_students.append(student)
    return kept_students



def label_drop_outs_sfsu(students):  # student drop out conditions
    labels = {}

    for student in students:
        label = []
        build_missing_classes(student)
#        if "in_progress" in student.status or "graduated" in student.status:
#            continue
        if float(student.final_gpa) < 2:
            label.append("poor_overall_grades")
        if float(student.final_cs_gpa) < 2:
            label.append("poor_cs_grades")
        if float(student.final_gen_gpa) < 2:
            label.append("poor_ge_grades")
        if float(student.final_gpa) >= 2.7:
            label.append("high_grades")
        ge = 0
        cs = 0
        for course in student.course_history:
            if course.course_type in ["core", "elective"]:
                cs += 1
            else:
                ge += 1
        if ge >= cs:
            label.append("lack_of_cs_progress")
        if ge > (2 * len(student.sem_seq_dict.keys())):
            label.append("outside_study")
        if len(label) == 0:
            label.append("special_case")
            student.type_descript_summary = "special_case"
        student.type_descript = ";".join(label)
        student.dropout_semester = max(student.sem_seq_dict.keys())
        student.type_descript_summary = summerize_failure(label)
        utils.append_to_dict(";".join(label), student, labels)
    for label in labels:
        print(label)
        print(len(labels[label]))

    return labels

def summerize_failure(label): #students may be tagged with more than one failure type, this function summerizes them.
    summary = "No Summary"
    if "poor_overall_grades" in label:
        summary = "overall_poor_performance"
    elif "high_grades" in label and "outside_study" in label and "poor_cs_grades" not in label and "poor_ge_grades" not in label:
        summary = "high_grades_likely_transfer"
    elif "outside_study" in label and ("lack_of_cs_progress" in label or "poor_cs_grades" in label):
        summary = "poor_cs_student_likely_transfer"
    elif "lack_of_cs_progress" in label or "poor_cs_grades"  in label and "outside_study" not in label:
        summary = "poor_cs_student"
    elif "poor_ge_grades" in label and "poor_cs_grades" not in label:
        summary = "poor_ge_student_only"
    elif len(label) == 1:
        summary = label[0]

    return summary

def label_student_prepardness(students): #checks for student preparedness based on unprepared file list
    # Run as part of init.
    unprepard_list = utils.list_from_file("./unprepared_courses", "\n", ",", False)
    change_list = []
    for student in students:
        course_history = student.course_history
        label = set()
        for crs in course_history:
            if crs.name in unprepard_list:
                if "MATH" in crs.name:
                    label.add("UN_MATH")
                if "PHYS" in crs.name:
                    label.add("UN_PHYS")
        if len(label) == 0:
            continue
        if len(label) == 1:
            student.prep_assess = label.pop()
            student.prep_assess_summary = "1"
        else:
            student.prep_assess = label.pop() + ";" + label.pop()
            student.prep_assess_summary = "1"

        change_list.append(student)
    return change_list

def update_final_gpa(students):
    gpa_dict = {}
    for student in students:
        course_history = student.course_history
        course_history.sort(key=lambda x: x.semester, reverse=True)
        gpa_dict[student.id_num] = course_history[0].sfsu_gpa
        student.final_gpa = course_history[0].sfsu_gpa
    return gpa_dict

def update_gpas(students):
    # include in final init
    cs_dict = {}
    gen_dict = {}
    all_dict = {}
    for student in students:
        course_hist = student.course_history
        cs_grades = []
        gen_grades = []
        all_grades = []
        for course in course_hist:
            all_grades.append(utils.translate_grade(course.grade_str))
            if course.course_type in ["core", "elective", "bonus"]:
                cs_grades.append(utils.translate_grade(course.grade_str))
            else:
                gen_grades.append(utils.translate_grade(course.grade_str))
        if len(cs_grades) == 0:
            cs_dict[student.id_num] = 0.0
            student.final_cs_gpa = 0.0
        else:
            final_cs_gpa = round(sum(cs_grades) / len(cs_grades), 2)
            cs_dict[student.id_num] = final_cs_gpa
            student.final_cs_gpa = final_cs_gpa
        if len(gen_grades) == 0:
            gen_dict[student.id_num] = 0.0
            student.final_gen_gpa = 0.0
        else:
            final_gen_gpa = round(sum(gen_grades) / len(gen_grades), 2)
            gen_dict[student.id_num] = final_gen_gpa
            student.final_gen_gpa = final_gen_gpa

        final_gpa = round(sum(all_grades) / len(all_grades), 2)
        all_dict[student.id_num] = final_gpa
        student.final_gpa = final_gpa

    return cs_dict, gen_dict, all_dict


def build_missing_classes(student):
    missing = []
    for crs in all_core_classes:
        if crs not in student.passed_classes:
            missing.append(crs)
    student.missing_classes = ",".join(missing)

    return student


def flag_serious(students): #flags students as serious if taken more than 2 CSC courses

    for student in students:
        csc_count = 0
        student.serious = True
        if "progress" in student.status:
            continue
        for crs in student.course_history:
            if "CSC" in crs.name:
                csc_count += 1
            if "MATH" in crs.name:
                missing_math = False
        if csc_count < 2:
            student.serious = False
            print(student.id_num)
    return


def update_load_list(students):
    course_ids = {}
    for student in students:
        for seq in student.course_seq_dict:
            course_set = student.course_seq_dict[seq]
            ge_count = 0
            tech_count = 0
            for course in course_set:
                if "MATH" in course.name or "PHSY" in course.name or "CSC" in course.name:
                    tech_count += 1
                else:
                    ge_count += 1
            for course in course_set:
                course_ids[course.ref_id] = [ge_count, tech_count]
                course.ge_load = ge_count
                course.tech_load = tech_count
    return course_ids


def build_student_class_seq(students):
    #  adds a map to class sequence, which is a dicitionary object with each key a
    # the order of the semesters linking to a list of classes taken that semester.
    for student in students:  #  no matter what format the input, the output is always 1,2,3,4 so we can compare students 1 semester vs others
        seqs = []             #   not sure this is critical for SFSU students, tho we use it to build the sequence FPs.
        for course in student.course_history:
            if course.semester not in seqs:
                seqs.append(course.semester)
        seqs.sort()
        for course in student.course_history:
            seq = course.semester
            seq_index = seqs.index(seq) + 1
            course.seq_int = seq_index
            if seq_index not in student.course_seq_dict:
                student.sem_seq_dict[seq_index] = seq
                student.course_seq_dict[seq_index] = [course]
            else:
                temp = student.course_seq_dict[seq_index]
                temp.append(course)
                student.course_seq_dict[seq_index] = temp
        student.final_standing = student.course_seq_dict[max(student.course_seq_dict.keys())][0].student_standing


def calc_sem_avg_grade(students):
    for student in students:
        for key in student.course_seq_dict:
            grades = []
            sem_list = student.course_seq_dict[key]
            for cor in sem_list:
                grades.append(cor.grade)
            avg_grade = float(sum(grades)) / len(grades)
            student.sem_avg_grades[key] = avg_grade


def calc_semester_load(students):
    for student in students:
        student.calc_semester_load()


def update_final_sem(students):
    for student in students:
        student.update_final_semester()

