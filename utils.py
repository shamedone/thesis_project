import mysql.connector
import random
from db_classes import Student, Course

def get_connetion(user, pass_, host, dbase):
    cnx = mysql.connector.connect(user=user, password=pass_,host=host, database=dbase)
    return cnx

def list_from_file(path, eol, split, headers):
    output = []
    with open(path, "r") as x:
        datas = x.read()
        datas = datas.split(eol)
        i = 0
        for data in datas:
          #  print(data)
            line = data.strip()
            line = line.split(split)
            if headers and i == 0:
                i+=1
                continue
            output.append(line)
    return output

def list_to_file(path, datas, **kwargs):
    with open(path, "w") as x:
        if "headers" in kwargs:
            x.write((kwargs["headers"])+"\n")
        for data in datas:
            x.write(str(data)+"\n")
    return

def add_to_dict_set(key, value, dict_):
    if key in dict_:
        temp = dict_[key]
        temp.add(value)
        dict_[key] = temp
    else:
        temp = set()
        temp.add(value)
        dict_[key] = temp

def add_to_dict_list(key, value, dict_):
    if key in dict_:
        temp = dict_[key]
        temp.append(value)
        dict_[key] = temp
    else:
        dict_[key] = [value]

def add_to_dict(key, value, dict_):
    if key in dict_:
        temp = dict_[key]
        temp.append(value)
        dict_[key] = temp
    else:
        temp = []
        temp.append(value)
        dict_[key] = temp

def sum_to_dict(key, value, dict_obj):
    if key in dict_obj:
        temp = dict_obj[key]
        temp += value
        dict_obj[key] = temp
    else:
        dict_obj[key] = value


def get_letter_grade(course_grade):
    if course_grade > 100:
        return "A+"
    elif course_grade > 95:
        return "A"
    elif course_grade > 90:
        return "A-"
    elif course_grade > 85:
        return "B"
    elif course_grade > 80:
        return "B-"
    elif course_grade > 75:
        return "C"
    elif course_grade > 70:
        return "C-"
    elif course_grade > 65:
        return "D+"
    elif course_grade > 60:
        return "D-"
    else:
        return "F"


def get_grade_points(course_grade):
    if course_grade > 100:
        return 4
    elif course_grade > 95:
        return 4
    elif course_grade > 90:
        return 3.7
    elif course_grade > 85:
        return 3
    elif course_grade > 80:
        return 2.7
    elif course_grade > 75:
        return 2
    elif course_grade > 70:
        return 1.7
    elif course_grade > 65:
        return 1.3
    elif course_grade > 60:
        return 1
    else:
        return 0

def group_gpa(gpa):
    if gpa >= 4.0:
        return 4.0
    elif gpa >= 3.7:
        return 3.7
    elif gpa >= 3.5:
        return 3.5
    elif gpa >= 3.3:
        return 3.3
    elif gpa >= 3:
        return 3
    elif gpa >= 2.7:
        return 2.7
    elif gpa >= 2.5:
        return 2.5
    elif gpa >= 2.3:
        return 2.3
    elif gpa >= 2:
        return 2
    elif gpa >= 1.7:
        return 1.7
    elif gpa >= 1.5:
        return 1.5
    elif gpa >= 1.3:
        return 1.3
    else:
        return 1

def group_gpa_class(gpa):
    if gpa >= 4.0:
        return "A"
    elif gpa >= 3.7:
        return "A-"
    elif gpa >= 3.3:
        return "A-"
    elif gpa >= 3.0:
        return "B+"
    elif gpa >= 2.7:
        return "B-"
    elif gpa >= 2.3:
        return "C+"
    elif gpa >= 2.0:
        return "C"
    elif gpa >= 1.7:
        return "C-"
    elif gpa >= 1.3:
        return "D+"
    elif gpa >= 1.0:
        return "D"
    else:
        return "F"

def get_students_history():
    cnx = get_connetion("advisor","passadvise","localhost","ADVISING")
    cursor = cnx.cursor(buffered=True)
    student_list = []

    for x in range(1,5500):
        sql = "select class_list_tester.CLASS_NAME, class_list_tester.SEMESTER_TAKEN, class_list_tester.GRADE, " \
              "class_list_tester.TYPE, student_list_tester.STUDENT_GRADE_ADJ, student_list_tester.STUDENT_SEMESTER_AGE" \
              " from class_list_tester inner join student_list_tester on " \
              "class_list_tester.STUDENT_ID = student_list_tester.STUDENT_ID where class_list_tester.STUDENT_ID = %s"

        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        temp_student = Student("NA", "NA", "NA", "NA", x)
        student_grade = 0
        student_age = 0
        for result in results:
            class_name = result[0]
            semester_taken = result[1]
            grade = result[2]
            course_type = result[3]
            temp_class = Course(class_name, grade, semester_taken, course_type)
            temp_student.add_course(temp_class)
            student_grade = result[4]
            student_age = result[5]
        temp_student.grade_adj = student_grade
        temp_student.age = student_age
        temp_student.course_history.sort(key=semester_sort)
        student_list.append(temp_student)
    return student_list

def semester_sort(val):
    temp = val.semester.split(" ")
    if temp[0] == "Spring":
        suffix = "1"
    if temp[0] == "Summer":
        suffix = "2"
    if temp[0] == "Fall":
        suffix = "3"
    else:
        suffix = "4"

    return temp[1]+suffix

def grade_vect_to_bit(vect):
    bit_vect = []
    for y in vect:
        if y != 0:
            bit_vect.append(1)
        else:
            bit_vect.append(0)
    return bit_vect

def dict_to_list(dict):
    dictlist = []
    for key in dict:
        temp = dict[key]
        dictlist.append(temp)
    return dictlist