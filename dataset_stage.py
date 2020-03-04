import utils

core_set = {"MATH226", "MATH227","MATH324","MATH325","PHYS220","PHYS222","PHYS230","PHYS232"}


def variable_check(students, query_course_name, prep_courses):
    kept_students = []
    for student in students:
        accept = True
        # if query_course_name not in student.unique_courses and query_course_name != "":
        #    accept = False
        #    continue
        # if student.unique_courses[query_course_name].seq_int == 1: #check if we need to do compare
        #     accept = False
        #     continue
        for course in prep_courses:
            if course not in student.unique_courses:
                accept = False
        if accept:
            kept_students.append(student)
    return kept_students


def build_named_fp(students, prep_courses):
    prep_courses.sort()
    filtered_students = variable_check(students, "", prep_courses)  # need to check this.
    x = []
    y = []
    variable_names = []
    for prep_course in prep_courses:
        variable_names.append(prep_course + "_grade")
        variable_names.append(prep_course + "_term_units")
        variable_names.append(prep_course + "_sfsu_units")
        variable_names.append(prep_course + "_seq")
        variable_names.append(prep_course + "_repeat")
        variable_names.append(prep_course + "_ge_load")
        variable_names.append(prep_course + "_tech_load")
    for student in filtered_students:

        y.append(student)

        x_data = []

        for prep_course in prep_courses:

            x_data.append(student.unique_courses[prep_course].grade)
            x_data.append(student.unique_courses[prep_course].term_units)
            x_data.append(student.unique_courses[prep_course].sfsu_units)
            x_data.append(student.unique_courses[prep_course].seq_int)
            x_data.append(student.unique_courses[prep_course].repeat)
            x_data.append(student.unique_courses[prep_course].ge_load)
            x_data.append(student.unique_courses[prep_course].tech_load)

        x.append(x_data)

    return x, y


def year_count(students):
    for student in students:
        skip = False
#        print(student.id_num)
#        for key in student.sem_avg_grades:
#           if student.sem_avg_grades[key] < 2:
#                print(student.sem_avg_grades[key])
#                skip = True
#                continue
#            sem_classes = student.sequence_dict[key]
#            if len(sem_classes) > 10:
#                skip = True
#                continue
        for key in student.sequence_dict:
            sem_classes = student.sequence_dict[key]
        if skip:
            continue
        student_set = set()
#        print(student.id_num)
        for course in student.course_history:
            student_set.add(course.semester)
        print(str(student.id_num)+","+str(len(student_set)))


def label_drop_outs_sfsu(students):  # student drop out conditions
    labels = {}

    for student in students:
        label = []
        if student.status in ["in progress", "graduated"]:
            continue
        final_sems_gpa = student.course_seq_dict[len(student.course_seq_dict)][0].term_gpa
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

def summerize_failure(label):
    summary = "No Summary"
    if "poor_cs_grades" in label and "poor_ge_grades" in label:
        summary = "overall_poor_performance"
    elif "poor_cs_grades" in label and "lack_of_cs_progress" in label and "poor_ge_grades" not in label and "outside_study" not in label:
        summary = "poor_cs_student"
    elif "poor_cs_grades" in label and "lack_of_cs_progress" in label and "poor_ge_grades" not in label and "outside_study" in label:
        summary = "likely_transfer"
    elif "high_grades" in label and "lack_of_cs_progress" in label:
        summary = "good_student_transfer"
    elif "high_grades" in label:
        summary = "good_cs_student_transfer"

    return summary

def label_student_prepardness(students):
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
            student.prep_assess_summary = "unprepared"
        else:
            student.prep_assess = label.pop() + ";" + label.pop()
            student.prep_assess_summary = "unprepared"

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

def update_final_cs_gpa(students):
    # include in final init
    cs_dict = {}
    gen_dict = {}
    for student in students:
        course_hist = student.course_history
        cs_grades = []
        gen_grades = []
        for course in course_hist:
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
    return cs_dict, gen_dict


def analyze_drop_outs(students, **kwargs):
    # TODO - create analogs based off of course names. skip 210 and 220 from reqs.
    drop_outs = []
    for student in students:
        if student.status is "drop_out":
            for course in student.course_history:
                print(course)
            drop_out_semester = max(student.sequence_dict.keys(), key=(lambda k: student.sequence_dict[k]))
            drop_outs.append(student.id_num + "," + drop_out_semester)
    if "outpath" in kwargs:
        utils.list_to_file(kwargs["outpath"], drop_outs, headers="student_id,sem_dropout")


def student_series_analysis(students):
    class_dict = {}
    for student in students:
        for keys in student.course_seq_dict:
            course_list = student.course_seq_dict[keys]
            for course in course_list:
                if course.name in class_dict:
                    temp = class_dict[course.name]
                    count = temp[keys-1]
                    count += 1
                    temp[keys-1] = count
                    class_dict[course.name] = temp
                else:
                    temp = [0] * 7
                    temp[keys - 1] = 1
                    class_dict[course.name] = temp
    for data in class_dict:
        print((str(data) + ",") + (",".join(str(count) for count in class_dict[data])))

    return class_dict


def analyze_series(infile):
    datas = utils.list_from_file(infile, "\n", ",", True)
    degree_dicts = {"G1042": {}, "G1077": {}}
    current_student = 0
    student_data = []
    for data in datas:
        degree = data[3]
        active_dict = degree_dicts[degree]
        if data[2] + data[3] != current_student:
            for x in range(0, len(student_data)):
                if student_data[x] not in active_dict:
                    active_dict[student_data[x]] = [0] * 60
                temp_data = active_dict[student_data[x]]
                print(current_student)
                temp_data[x] += 1

                active_dict[student_data[x]] = temp_data
            student_data = []
            current_student = data[2] + data[3]
        student_data.append(data[4])
    for dict_ in degree_dicts:
        data_dict = degree_dicts[dict_]
        for data in data_dict:
            print((dict_ + " " + str(data) + ",") + (",".join(str(count) for count in data_dict[data])))


# new student vector,
# modify to allow 8 classes per semester
# build so first 8 relate to integer of class, next 8 relate to grades

def create_named_fps(students, query_course_name, prep_courses, **kwargs):
    prep_courses.sort()
    filtered_students = variable_check(students, query_course_name, prep_courses)
    x = []
    y = []
    variable_names = ["coures_seq", "course_term_units", "prior_semester_sfsu_units", "prior_semester_sfsu_gpa"]
    for prep_course in prep_courses:
        variable_names.append(prep_course + "_grade")
        variable_names.append(prep_course + "_term_units")
    for student in filtered_students:
        course = student.unique_courses[query_course_name]
        while course.repeat > 0:
            course = course.past_attempts[0]

        course_int = course.seq_int

        if course_int - 1 == 0:
            continue
        y.append(course.grade)

        any_prior_course = student.course_seq_dict[course_int - 1][0]
        x_data = [course_int, course.term_units, any_prior_course.sfsu_units, any_prior_course.sfsu_gpa]

        for prep_course in prep_courses:
            x_data.append(student.unique_courses[prep_course].grade)
            x_data.append(student.unique_courses[prep_course].term_units)

        if "prior_ge" in kwargs:
            ge_count = 0
            for course in student.course_history:
                if course.type == "ge" and course.seq_int < course_int:
                    ge_count += 1
            x_data.append(ge_count)
            variable_names.append("prior ges")
        if "concurrent_ge" in kwargs:
            cge_count = 0
            course_list = student.course_seq_dict[course_int]
            for course in course_list:
                if course.type == "ge":
                    cge_count += 1
            x_data.append(cge_count)
            variable_names.append("concurrent ges")

        x.append(x_data)
    return x, y


def build_variable_student_vector(students, class_dict, lim):  # what we need this new system to do is

    for student in students:
        master_vect = []
        for x in range(1, lim+1):
            sequence_vect = [0] * 10
            grade_vect = [0] * 10
            try:
                course_history = student.course_seq_dict[x]  # should we sort this?
            except KeyError:
                addition = sequence_vect + grade_vect
                master_vect += addition
                continue
            #                course_history.sort(key=lambda x: x.name)

            i = 0
            for course in course_history:
                if course.name not in class_dict:  # skip if not in requested classes available for training.
                    continue
                grade = course.grade
                name = course.name
                grade_vect[i] = grade
                sequence_vect[i] = class_dict[name]
                i += 1
            addition = sequence_vect + grade_vect
            master_vect += addition
        student.fp_dict["master"] = master_vect


def build_student_vector_cs_only(students, class_dict, lim):  # what we need this new system to do is

    for student in students:
        master_vect = [0] * len(class_dict)
        for x in range(1, lim+1):
            try:
                course_history = student.course_seq_dict[x]  # should we sort this?
            except KeyError:
                continue
            for course in course_history:
                if course.name not in class_dict or course.repeat > 0:
                    #  skip if not in requested classes available for training.
                    continue
                grade = course.grade
                name = course.name

                master_vect[class_dict[name]] = grade
        student.fp_dict["master"] = master_vect


def build_demographic_vector(students):  # TODO look up inline modifcation for method.
    for student in students:
        demo_fp = [int(student.sex), int(student.ethnic), int(student.admin_descript), int(student.resident_status)]
        if student.prep_assess == "OK":
            demo_fp.append("1")
        elif student.prep_assess == "UN_MATH":
            demo_fp.append("2")
        elif student.prep_assess == "UN_PHYS":
            demo_fp.append("3")
        elif student.prep_assess == "UN_MATH;UN_PHYS":
            demo_fp.append("4")
        student.fp_dict["demo"] = demo_fp
    return students


def build_block_fp(students):
    course_set = set()
    course_dict = {}
    for student in students:
        crs_hist = student.course_history
        for crs in crs_hist:
            course_set.add(crs.name)
    course_list = list(course_set)
    course_list.sort()
    i = 0
    for course in course_list:
        course_dict[course] = i
        i += 3
    for student in students:
        crs_hist = student.course_history
        block_fps = {}
        for crs in crs_hist:
            if crs.name not in block_fps:
                block_fps[crs.name] = [crs.grade, crs.seq_int, 0]
            else:
                temp = block_fps[crs.name]
                grade = float((temp[0] + crs.grade)) / 2
                repeat = temp[2] + 1
                block_fps[crs.name] = [grade, crs.seq_int, repeat]
        final_block_fp = [0]*len(course_list) * 3
        for crs in block_fps:
            block_fp = block_fps[crs]
            i = course_dict[crs]
            final_block_fp[i] = block_fp[0]
            final_block_fp[i+1] = block_fp[1]
            final_block_fp[i+2] = block_fp[2]
        student.fp_dict["block_fp"] = final_block_fp

    return


def build_student_vector(students, class_dict, lim):
    for student in students:
        sequence_vect = [0] * len(class_dict)
        grade_vect = [0] * len(class_dict)
        repeat_vect = [0] * len(class_dict)
        for seq in student.course_seq_dict:
            if seq <= lim:
                course_history = student.course_seq_dict[seq]
            else:
                continue
            for course in course_history:
                if course.name not in class_dict:  # skip if not in requested classes available for training.
                    continue
                grade = course.grade
                if grade == 0:  # does it need to check between spain and sfsu data.
                    grade = 10  # seperate non attempts from failed attempts.
                name = course.name
                if sequence_vect[class_dict[name]] != 0:
                    repeat_vect[class_dict[name]] = 1
                sequence_vect[class_dict[name]] = seq
                grade_vect[class_dict[name]] = grade
        student.fp_dict["grades"] = grade_vect
        student.fp_dict["seq"] = sequence_vect
        student.fp_dict["repeat"] = repeat_vect

        """
                if grade_vect[class_dict[name]] != 0:
                    temp = repeat_vect[class_dict[name]]
                    temp+=1
                    repeat_vect[class_dict[name]] = temp
                    temp_grade = grade_vect[class_dict[name]]
                    temp_grade.append(grade)
                    grade_vect[class_dict[name]] = temp_grade
                else:
                    grade_vect[class_dict[name]] = [grade]
                grades.append(grade)
            for x in range(0, len(grade_vect)):
                if grade_vect[x] == 0:
                    continue
                grade_vect[x] = sum(grade_vect[x])/float(len(grade_vect[x]))
                
        if vect_type == "simple":
            return grade_vect
        else:
            return sequence_vect + grade_vect + repeat_vect + [sum(grades)/float(len(grades))]
        """


def get_course_pred_vect_key_dict(training_set, testing_set, class_pred_seq, pred_class):
    #  PROBLEM: need to recreate each FP to eliminate class in questions.
    pred_train_classes = set()
    for student in testing_set:
        for x in range(1, class_pred_seq):
            course_list = student.course_seq_dict[x]
            for course in course_list:
                if course.name == pred_class:
                    continue
                pred_train_classes.add(course.name)
    for student in training_set:
        for x in range(1, class_pred_seq):
            course_list = student.course_seq_dict[x]
            for course in course_list:
                if course.name == pred_class:
                    continue
                pred_train_classes.add(course.name)
    key_dict = {}
    i = 0
    for classes in pred_train_classes:
        key_dict[classes] = i
        i += 1
    return key_dict


def build_class_key_vector(datas, **kwargs):
    #  runs through list of classes, and gives each a unique identifier.
    key_dict = {}
    i = 0
    class_list = set()
    for student in datas:
        for data in student.course_history:
            if 'core_only' in kwargs and "CSC" not in data.name and data.name not in core_set:
                continue
            if 'generic_ge' in kwargs and "CSC" not in data.name and data.name not in core_set:
                class_list.add("GE")
            else:
                class_list.add(data.name)
    for classes in class_list:
        key_dict[classes] = i
        i += 1
    return key_dict


def match_student_classes(datas, student_list, **kwargs):
    student_dict = {}
    output = []
    for student in student_list:
        student_dict[student.id_num] = student

    for data in datas:
        line = data
        try:
            student = student_dict[line[0]]
        except KeyError:
            continue
        if 'preds' in kwargs:
            try:
                predict = kwargs['preds'][student.id_num]
                line.append(predict)
            except KeyError:
                line.append("no_pred")
        line.append(student.status)
        output.append(line)
    return output

def flag_serious(students):
    false_set = []
    for student in students:
        if student.status != "dropout":
            continue
        if "CSC220" not in student.unique_courses:
            false_set.append(student.id_num)

    return false_set

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

#TODO which of these to keep
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

def calc_sem_avg_grade(students):
    for student in students:
        for key in student.course_seq_dict:
            grades = []
            sem_list = student.course_seq_dict[key]
            for cor in sem_list:
                grades.append(cor.grade)
            avg_grade = float(sum(grades)) / len(grades)
            student.sem_avg_grades[key] = avg_grade