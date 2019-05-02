import utils
from db_classes import Course
from db_classes import Student


def add_to_student_obj(student_id, course, dict_): #pulls in data from test data, student id refers to place                                                    # in line data that contains student id.
    if student_id in dict_:
        temp = dict_[student_id]
        temp.add_course(course)
        dict_[student_id] = temp
    else:
        student = Student("na", "na", "na", "na", student_id)
        student.add_course(course)
        dict_[student_id] = student

def build_student_dict(student_data, id_int, class_int, grade_int, year_int): #returns dict of student objs, complete with course work.
    student_dict = {}
    for data in student_data:
        student_id = data[id_int]
        course = Course(data[class_int], float(data[grade_int]), data[year_int],"None")
        add_to_student_obj(student_id, course, student_dict)
    return student_dict

def build_class_key_vector(datas, class_int): #runs through list of classes, and gives each a unique identifier.
    key_dict = {}
    i = 0
    class_list = set()
    for data in datas:
        class_list.add(data[class_int])
    for classes in class_list:
        key_dict[classes] = i
        i+=1
    return key_dict

def build_student_class_seq(students): #adds a map to class sequence, which is a dicitionary object with each key a the order of the semesters
                                        # linking to a list of classes taken that semester.
    for student in students:
        seqs = []
        for course in student.course_history:
            if course.semester not in seqs:
                seqs.append(course.semester)
        seqs.sort()
        for course in student.course_history:
            seq = course.semester
            seq_index = seqs.index(seq) + 1
            if seq_index not in student.course_seq_dict:
                student.sem_seq_dict[seq_index] = seq
                student.course_seq_dict[seq_index] = [course]
            else:
                temp = student.course_seq_dict[seq_index]
                temp.append(course)
                student.course_seq_dict[seq_index] = temp

    for student in students:
        for key in student.course_seq_dict:
            grades = []
            sem_list = student.course_seq_dict[key]
            for cor in sem_list:
                grades.append(cor.grade)
            avg_grade = float(sum(grades))/len(grades)
            student.sem_avg_grades[key] = avg_grade




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

def label_drop_outs(students): #student drop out conditions
    do_count = 0
    one_years = 0
    for student in students:
        if len(student.course_seq_dict) == 1 and student.sem_seq_dict[1] == "2014": #enroll in one year and dont return
            one_years+=1
            continue
        if len(student.course_seq_dict) == 1 and student.sem_seq_dict[1] != "2014": #enroll in one year and dont return
            do_count += 1
            student.status = "drop_out_one_done"
            #print(student.status)
            #print(student.id_num)
            continue
        max_count = max(list(student.course_seq_dict.keys()))
        max_yr = student.sem_seq_dict[max_count]
        max_yr_avg_grade = student.sem_avg_grades[max_count]
        if max_yr_avg_grade < 2 and max_yr != "2014":  #enroll in fail out a year and dont return
            do_count += 1
            student.status = "drop_out_fail_out"
            #print(student.status)
            #print(student.id_num)
            continue

    print(str(len(students)-one_years)+" total students")
    print(str(one_years)+" one years")
    print(str(do_count)+" droppouts")

def analyze_drop_outs(students, **kwargs):
    drop_outs = []
    for student in students:
        if student.status is "drop_out":
            for course in student.course_history:
                print(course)
            drop_out_semester = max(student.sequence_dict.keys(), key=(lambda k: student.sequence_dict[k]))
            drop_outs.append(student.id_num +","+drop_out_semester)
    if "outpath" in kwargs:
        utils.list_to_file(kwargs["outpath"], drop_outs, headers="student_id,sem_dropout")

def print_class_dict(path, **kwargs): #G1042 - math
                            #G1077 - cs
    student_data = utils.list_from_file(path, "\n", ",", True)
    class_dict = build_class_key_vector(student_data, 4)
    output = []
    for key in class_dict:
        output.append(key+","+str(class_dict[key]))
    if "outpath" in kwargs:
        utils.list_to_file(kwargs["outpath"], output, headers="class_id,vect_int")

def student_series_analysis(students):
    class_dict = {}
    for student in students:
        for keys in student.course_seq_dict:
            course_list = student.course_seq_dict[keys]
            for course in course_list:
                if course.name in class_dict:
                    temp = class_dict[course.name]
                    count = temp[keys-1]
                    count+=1
                    temp[keys-1] = count
                    class_dict[course.name] = temp
                else:
                    temp = [0] * 7
                    temp[keys - 1] = 1
                    class_dict[course.name] = temp
    for data in class_dict:
        print((str(data) + ",") + (",".join(str(count) for count in class_dict[data])))

    return class_dict

def find_successful(students):
    successes = []
    for student in students:
        good_student = False
        #course_set = student.unique_coures
        #for classes in req_classes:
        #    if classes not in course_set:
        #        good_student = False


        if len(student.sem_seq_dict) >= 4 and len(student.unique_coures) >= 30: #enroll in one year and dont return
            good_student = True
            for key in student.sem_avg_grades:
                 if student.sem_avg_grades[key] < 7:
                        good_student = False

        if good_student:
            print(student.id_num)
            print(len(student.unique_coures))
            for key in student.sem_avg_grades:
                print(student.sem_avg_grades[key])
            print("-----")
            successes.append(student)
            print(len(successes))
    student_series_analysis(successes)

def lable_successfull(students):
    req_classes = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/req_classes.csv", "\n", ",",True)
    g1077_req = set()
    g1402_req = set()
    for req in req_classes:
        check1 = req[0]
        check2 = req[1]
        if check1 != "":
            g1402_req.add(check1)
        if check2 != "":
            g1077_req.add(check2)

    g_count = 0
    for student in students:
        courses = student.course_history
        course_dict = {}
        good_student = True
        for course in courses:
            course_dict[course.name] = course

        if student.major == "G1077":
            active_set = g1077_req
        else:
            active_set = g1402_req
        for req in active_set:
            if req not in course_dict:
                good_student = False
                continue
            if course_dict[req].grade < 5:
                good_student = False
        if good_student:
            g_count +=1
            student.status = "graduated"
    print(g_count)




def analyze_series(infile):
    datas = utils.list_from_file(infile, "\n", ",", True)
    degree_dicts = {}
    degree_dicts["G1042"] = {}
    degree_dicts["G1077"] = {}
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
    for dict in degree_dicts:
        data_dict = degree_dicts[dict]
        for data in data_dict:
            print((dict + " " + str(data) + ",") + (",".join(str(count) for count in data_dict[data])))


def build_student_vector(students, class_dict):
    for student in students:
        sequence_vect = [0] * len(class_dict)
        grade_vect = [0] * len(class_dict)
        repeat_vect = [0] * len(class_dict)
        grades = []
        for seq in student.course_seq_dict:
            course_history = student.course_seq_dict[seq]
            for course in course_history:
                if course.name not in class_dict:#skip if not in requested classes available for training.
                    continue
                grade = course.grade
                if grade == 0:
                    grade = .1 # seperate non attempts from failed attempts.
                name = course.name
                if sequence_vect[class_dict[name]] != 0:
                    repeat_vect[class_dict[name]] = 1
                sequence_vect[class_dict[name]] = seq
                grade_vect[class_dict[name]] = grade
        student.fp_dict["grades"] = grade_vect
        student.fp_dict["seq"] = sequence_vect
        student.fp_dict["repeate"] = repeat_vect

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

def get_course_pred_vect_key_dict(training_set, testing_set, class_pred_seq, pred_class): #PROBLEM: need to recreate each FP to eliminate class in questions.
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

