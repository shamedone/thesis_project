import utils
import random
import db_classes
import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np

#TODO need to alter classes lists to add prereqs to end, seperated by semicolon.
#TODO add grade modifier class ie: if taking course x and have not taken course y, *.5 else *1.05
#TODO build vector of classes as part of student class, so that they can be passed to learner

def main_generate_student_data(name_path, core_path, elective_path):
    cnx = utils.get_connection("advisor", "passadvise", "localhost", "ADVISING")
    name_data = utils.list_from_file(name_path, "\n", "," ,False)
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", "," ,False)
    students = generate_student(name_data, elective_data[:], core_data[:])
    persist_students(students, cnx)
    cnx.close()


def generate_student(name_data, elective_list, core_list):
    students = []

    id = 1
    corlen= 0
    for student_name in name_data:
        first_name = student_name[0].split(" ")[0]
        last_name = student_name[0].split(" ")[1]
        email = first_name+last_name+"@mail.sfsu.edu"
        start_year = 2012
        semester = "Fall"
        course_taken = 0
        print(student_name)
        student_grade_adustment = int(float(student_name[1]))
        student = db_classes.Student(first_name, last_name, email, student_grade_adustment, id)
        id+=1
        elective_data  = []
        elective_data.extend(elective_list)
        core_data = []
        core_data.extend(core_list)
        max_course = 40
        #TODO : alter code so that it can escape if no more classes with prereqs are found.
        force = "none"

        while course_taken < max_course and student.type != "Failed":
            num_to_take = random.randint(4,7) #allow students to take 4 to 7 classes
            core_eligible_count = 0
            for core_class in core_data:
                if (student.check_prereqs(core_class[4].split(";"))):
                    core_eligible_count += 1
            elective_eligible_count = 0
            for elective_class in elective_data:
                if (student.check_prereqs(elective_class[4].split(";"))):
                    elective_eligible_count += 1
            class_set = set()
            class_block = []

            for x in range(0, num_to_take):
                skip_iter = False

                if course_taken > 40 and len(core_data) == 0: #check to see if we are in added time to compelete core courses, if so and all cores are taken break
                    break
                type = "elective"
                if (force == "core" or random.randint(1,100) > 16) and len(core_data) > 0 and force != "elective": #65% chance to take cores course, unless all are taken
                    force = "none"
                    go = True
                    seen = []
                    while go:
                        if len(core_data) == 0:
                            skip_iter = True
                            core_data.extend(seen)
                            break
                        course = core_data.pop(random.randint(0, len(core_data) - 1))

                        check = student.check_prereqs(course[4].split(";"))  # randomly pick a elective class, check prereqs, and if satisfied continue, else pick again
                        if check and course[0] not in class_set:
                            go = False
                            class_set.add(course[0])
                            core_data.extend(seen)
                            class_block.append(course)

                        else:
                            seen.append(course)

                    type = "core"
                else:
                    force = "none"
                    go = True
                    seen = []
                    while go:
                        if len(elective_data) == 0:
                            skip_iter = True
                            go = False
                            elective_data.extend(seen)
                            break

                        course = elective_data.pop(random.randint(0, len(elective_data)-1))
                        check = student.check_prereqs(course[4].split(";"))  # randomly pick a elective class, check prereqs, and if satisfied continue, else pick again
                        if check and course[0] not in class_block:
                            go = False
                            class_set.add(course[0])
                            elective_data.extend(seen)
                            class_block.append(course)

                        else:
                            seen.append(course)

                if skip_iter:
                    force = "elective"
                    if type == "elective":
                        force = "core"
                    continue



            for course in class_block: #in roder to better simulate semesters, grade students in blocks of classes.
                course_name = course[0]
                course_grade = float(random.normalvariate( student.grade_adj, 5)) # randomly generate grade
                grade_adjustment = float(student.adjust_grade(course, num_to_take))
                course_grade *= grade_adjustment
                type = course[6]
                new_course = db_classes.Course(course_name, course_grade, semester + " " + str(start_year), type)  # add to student history
                student.add_course(new_course)
                course_taken += 1

                if course_grade < 60 and type == "core":  # if failed place back in queue
                    core_data.append(course)
                elif course_grade < 60:
                    elective_data.append(course)

            if course_taken >= 40 and len(core_data) != 0:  # if 40 classes hit and core classes not met, than electives have been taken, force cores and keep loop going
                force = "core"
                max_course += 7

            if len(core_data) == 0:
                student.type = "Success"

            if len(core_data) == 0 and course_taken > 40:
                max_course -= 10

            student.age+= 1
            if student.age > 16 and len(core_data) > 0:
                student.type = "Failed"


            if semester == "Fall":
                start_year += 1
                semester = "Spring"
            else:
                semester = "Fall"
        corlen += len(core_data)
        print(corlen)
        students.append(student)
    return students

def persist_students(student_data, cnx):
    cursor = cnx.cursor(buffered=True)

    for student in student_data:
        sql = "insert into student_list_tester (STUDENT_ID, STUDENT_FIRST_NAME, STUDENT_LAST_NAME, STUDENT_EMAIL, \
        STUDENT_SEMESTER_AGE, STUDENT_GRADE_ADJ, status) values (%s, %s, %s, %s, %s, %s, %s)"
        values = (student.id_num, student.first_name, student.last_name, student.email, student.age, student.grade_adj, student.status)
        cursor.execute(sql, values)

        for course in student.course_history:
            sql = "insert into class_list_tester (STUDENT_ID, CLASS_NAME, SEMESTER_TAKEN, GRADE, TYPE) values (%s, %s, %s, %s, %s)"
            values = (student.id_num, course.name, course.semester, course.grade, course.class_type)
            cursor.execute(sql, values)
    cnx.commit()
    cursor.close()




#main_generate_student_data("/Users/thomasolson/Documents/workspace/advising_revamp/students.csv",
#                           "/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
#                           "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv")

def student_scores():


    y = []
    for x in range(0,5000):

        score = random.normalvariate(80,8)
        y.append(score)

    data = [go.Histogram(x=y)]

    py.plot(data, filename='basic histogram')
    for score in y:
        print(score)

def test_2():


    y = []
    for x in range(0,33):
        y.append(random.normalvariate(75, 5))

    data = [go.Histogram(x=y)]

    py.plot(data, filename='basic histogram')
    for score in y:
        print(score)
    print (float(sum(y))/len(y))

def test_3():
    for x in range(0,35):
        print(random.normalvariate(.95, .05))

def populate_tester_db():
    starting_id = "1"
    insert_db = [];
    cnx = utils.get_connection("advisor", "passadvise", "localhost", "ADVISING")
    cursor = cnx.cursor(buffered=True)

    for x in range(1,145):
        sql = "select STUDENT_FIRST_NAME, STUDENT_LAST_NAME, STUDENT_EMAIL from student_list_tester where STUDENT_ID = %s"

        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchone()
        first_name = results[0]
        last_name =results[1]
        email = results[2]
        entry = [first_name, last_name, email, x]
        insert_db.append(entry)

    for db_entry in insert_db:
        sql = "insert into checkpoints (STUDENT_ID, STUDENT_FIRST_NAME, STUDENT_LAST_NAME, STUDENT_EMAIL) values (%s, %s, %s, %s)"
        key = (db_entry[3], db_entry[0], db_entry[1], db_entry[2])
        cursor.execute(sql, key)
    cnx.commit()
    cursor.close()
    cnx.close()

populate_tester_db()





