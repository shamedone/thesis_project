import mysql.connector
import random

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

def add_to_dict_set(key, value, dict_):
    if key in dict_:
        temp = dict_[key]
        temp.add(value.strip())
        dict_[key] = temp
    else:
        temp = set()
        temp.add(value.strip())
        dict_[key] = temp
    return dict_

def sum_to_dict(key, value, dict_obj):
    if key in dict_obj:
        temp = dict_obj[key]
        temp += value
        dict_obj[key] = temp
    else:
        dict_obj[key] = value

    return dict_obj

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