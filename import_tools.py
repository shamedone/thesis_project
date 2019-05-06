import utils
from db_classes import Course
from db_classes import Student

def add_to_student_obj(student_id, course, dict_, student_data, kwargs): #pulls in data from test data, student id refers to place                                                    # in line data that contains student id.
    if student_id in dict_:                 #to remain flexible, addiitional parameters can be set to be imported by provding
        temp = dict_[student_id]            #their indexes in dictionary object.
        temp.add_course(course)
        if len(kwargs) > 0: # if there are keyword args then its a sfsu type with more data
            if temp.age > student_data[kwargs["age"]]:
                temp.age = student_data[kwargs["age"]]
            if temp.standing > student_data[kwargs["standing"]]:
                temp.standing = student_data[kwargs["standing"]]
        dict_[student_id] = temp
    else:
        if len(kwargs) == 0: # if no kwargs then there is no data.
            student = Student(student_id, "na", "na", "na", "na")
        else:
            student = Student(student_id, kwargs["sex"], kwargs["ethnic"], kwargs["age"],
                              kwargs["resident_status"], kwargs["standing"])
        student.add_course(course)
        dict_[student_id] = student

def build_student_dict(student_data, **kwargs): #returns dict of student objs, complete with course work.
    student_dict = {}
    for data in student_data:
        student_id = data[kwargs["studnet_id"]]

        if len(kwargs) > 3: #less than 3 means no special type.
            course = Course(data[kwargs["class_int"]], (data[kwargs["grade_int"]])*10, data[kwargs["year_int"]],0, 0)
        else:
            course = Course(data[kwargs["class_int"]], data[kwargs["grade_int"]], int(data[kwargs["year_int"]]),data[kwargs["age"]], data[kwargs["standing"]])

        add_to_student_obj(student_id, course, student_dict, data, kwargs)
    return student_dict

def build_student_class_seq(students):  # adds a map to class sequence, which is a dicitionary object with each key a the order of the semesters
                                        # linking to a list of classes taken that semester.
    for student in students:  # no matter what format the input, the output is always 1,2,3,4 so we can compare students 1 semester vs others
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
            avg_grade = float(sum(grades)) / len(grades)
            student.sem_avg_grades[key] = avg_grade

def build_student_class_seq(students):  # adds a map to class sequence, which is a dicitionary object with each key a the order of the semesters
    # linking to a list of classes taken that semester.
    for student in students:  # no matter what format the input, the output is always 1,2,3,4 so we can compare students 1 semester vs others
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
            avg_grade = float(sum(grades)) / len(grades)
            student.sem_avg_grades[key] = avg_grade

def import_sfsu_core_classes():
    data = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv", "\n", ",",False)
    course_list = []
    for course in data:
        new_course = Course(course[0], 0, "REF_COURSE",0,0,prereqs=course[course[4].split(";")])
        course_list.append(new_course)
    return course_list
