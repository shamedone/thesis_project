import mysql.connector


def get_connection(**kwargs):
    if len(kwargs) == 0:
        cnx = mysql.connector.connect(user="advisor", password="passadvise", host="localhost",
                                      database="SFSU_STUDENT_HISTORY")
    else:
        cnx = mysql.connector.connect(user=kwargs['user'], password=kwargs['password'], host=kwargs["host"],
                                      database=kwargs["database"])
    return cnx


def list_from_file(path, eol, split, skip_headers):
    output = []
    with open(path, "r") as x:
        datas = x.read()
        datas = datas.split(eol)
        i = 0
        for data in datas:
            #  print(data)
            if skip_headers and i == 0:
                i += 1
                continue
            line = data.strip()
            if split not in line:
                output.append(line)
                continue
            line = line.split(split)

            output.append(line)
    return output


def dict_from_file(path, key, value, eol, split, headers):
    output = {}
    with open(path, "r") as x:
        datas = x.read()
        datas = datas.split(eol)
        i = 0
        for data in datas:
            #  print(data)
            line = data.strip()
            line = line.split(split)
            if headers and i == 0:
                i += 1
                continue
            output[line[key]] = line[value]
    return output


def dict_to_set_list(dict_):
    output = []
    for x in dict_:
        output.append([x, dict_[x]])
    return output


def dict_to_list(dict_):
    dictlist = []
    for key in dict_:
        temp = dict_[key]
        dictlist.append(temp)
    return dictlist


def list_to_file(path, datas, **kwargs):
    if len(datas) == 0:
        print("no data passed to util")
        return
    with open(path, "w") as x:
        if "headers" in kwargs:
            x.write((kwargs["headers"])+"\n")
        for data in datas:
            x.write(",".join(str(x) for x in data) + "\n")
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


def append_to_dict(key, value, dict_):
    if key in dict_:
        temp = dict_[key]
        temp.append(value)
        dict_[key] = temp
    else:
        temp = [value]
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
    elif course_grade > 92:
        return "A"
    elif course_grade > 90:
        return "A-"
    elif course_grade > 87:
        return "B+"
    elif course_grade > 82:
        return "B"
    elif course_grade > 80:
        return "B-"
    elif course_grade > 77:
        return "C+"
    elif course_grade > 72:
        return "C"
    elif course_grade > 70:
        return "C-"
    elif course_grade > 67:
        return "D+"
    elif course_grade > 62:
        return "D"
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
        return "B+"
    elif gpa >= 3.0:
        return "B"
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


def translate_grade(grade):
    if grade == "A":
        return 4.0
    elif grade == "A-":
        return 3.7
    elif grade == "B+":
        return 3.3
    elif grade == "B":
        return 3.0
    elif grade == "B-":
        return 2.7
    elif grade == "C+":
        return 2.3
    elif grade == "C":
        return 2.0
    elif grade == "C-":
        return 1.7
    elif grade == "D+":
        return 1.3
    elif grade == "D":
        return 1.0
    else:
        return 0.0


def semester_sort(val):
    temp = val.semester.split(" ")
    if temp[0] == "Spring":
        suffix = "1"
    elif temp[0] == "Summer":
        suffix = "2"
    elif temp[0] == "Fall":
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


def str_grade_to_int(course_grade):
    if course_grade == "A":
        return 95
    if course_grade == "A-":
        return 92
    if course_grade == "B+":
        return 88
    if course_grade == "B":
        return 85
    if course_grade == "B-":
        return 82
    if course_grade == "C+":
        return 78
    if course_grade == "C":
        return 75
    if course_grade == "C-":
        return 72
    if course_grade == "D+":
        return 68
    if course_grade == "D":
        return 65
    if course_grade == "D-":
        return 62
    if course_grade == "F":
        return 50
    if course_grade == "NC":
        return 50
    if course_grade == "CR":
        return 80
    if course_grade == "I":
        return 30
    if course_grade == "IC":
        return 30
    if course_grade == "WU":
        return 30

    return 0


def str_grade_to_gpu(course_grade):
    if course_grade == "A":
        return 4.0
    if course_grade == "A-":
        return 3.7
    if course_grade == "B+":
        return 3.3
    if course_grade == "B":
        return 3.0
    if course_grade == "B-":
        return 2.7
    if course_grade == "C+":
        return 2.3
    if course_grade == "C":
        return 2.0
    if course_grade == "C-":
        return 1.7
    if course_grade == "D+":
        return 1.3
    if course_grade == "D":
        return 1.0
    if course_grade == "D-":
        return .07
    if course_grade == "F":
        return 0.0
    if course_grade == "NC":
        return 0.0
    if course_grade == "CR":
        return 4.0
    if course_grade == "I":
        return 0.0
    if course_grade == "IC":
        return 0.0
    if course_grade == "WU":
        return 0.0

    return 0.0

def remove_dupes(datas):
    complete_set = []
    for data in datas:
        if data not in complete_set:
            complete_set.append(data)
    return complete_set