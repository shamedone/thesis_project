import utils
import db_classes
import plotly.plotly as py
import plotly.graph_objs as go
import numpy


def generate_class_histogram_data(core_path, elective_path, repeat):
    cnx = utils.get_connetion("advisor","passadvise","localhost","ADVISING")
    histo_gram_dict = {}
    all_class_list = read_classes(core_path=core_path, elective_path=elective_path)
    cursor = cnx.cursor(buffered=True)
    for course in all_class_list:
            histo_gram_dict[course] = 0


    sql = "select CLASS_NAME from class_list_tester where STUDENT_ID = %s"

    if repeat:
        sql += " group by CLASS_NAME having count(*) > 1"

    for x in range(1,5001):
        #print(x)
        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        #print(results)
        for result in results:
            #print(result)
            utils.sum_to_dict(result[0].decode("utf-8"), 1, histo_gram_dict)
    cursor.close()
    cnx.close()

    course_list = []
    course_freq = []
    for course in histo_gram_dict.keys():
        course_list.append(course)
        course_freq.append(str(histo_gram_dict[course]))
    print (course_list)
    print (course_freq)
    hist_data = [
        go.Histogram(
            histfunc="sum",
            y=course_freq,
            x=course_list,
            name="sum"
        )
    ]
    py.plot(hist_data, filename='binned classes')

    return course_list, course_freq

def check_core_check(core_path):
    cnx = utils.get_connetion("advisor", "passadvise", "localhost", "ADVISING")
    core_list = read_classes(core_path=core_path)
    core_set = set()
    for course in core_list:
        core_set.add(course)

    students_missing_core = {}

    sql = "select CLASS_NAME from class_list_tester where STUDENT_ID = %s and TYPE = 'core'"
    cursor = cnx.cursor(buffered=True)



    for x in range(1,5001):
        student_gaps = []
        #print(x)
        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        #print(results)
        taken_classes = set()
        for result in results:
            taken_classes.add(result[0].decode("utf-8"))
        for course in core_set:
            if course not in taken_classes:
                student_gaps.append(course)
        if len(student_gaps) > 0:
            students_missing_core[x] = student_gaps

    for student in students_missing_core.keys():

        print (student)
        print (students_missing_core[student])


    cursor.close()
    cnx.close()

def read_classes(**kwargs):
    course_list = []
    if 'core_path' in kwargs:
        core_data = utils.list_from_file(kwargs['core_path'], "\n", ",", False)
        for course in core_data:
            course_list.append(course[0].strip())

    if 'elective_path' in kwargs:

        elective_data = utils.list_from_file(kwargs['elective_path'], "\n", ",", False)
        for course in elective_data:
            course_list.append(course[0].strip())

    return course_list


def calc_gpa_histogram(testers):
    cnx = utils.get_connetion("advisor","passadvise","localhost","ADVISING")

    cursor = cnx.cursor(buffered=True)
    gpas = []
    sql = "select GRADE from class_list_tester where STUDENT_ID = %s"

    min = 1
    max = 5001
    if testers:
        min = 5001
        max = 5501

    for x in range(min, max):
        # print(x)
        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        # print(results)
        grade_points = 0
        class_points = 0
        for result in results:
            # print(result)
            score = result[0]
            gps = utils.get_grade_points(score)
            grade_points +=(gps * 3)
            class_points += 3
        gpa = float(grade_points)/ class_points
        gpas.append(gpa)

    print(gpas)
    hist_data = [go.Histogram(x=gpas)]

    prefix = "student"
    if testers:
        prefix = "tester"
    py.plot(hist_data, filename=prefix+' histogram')

    cnx.close()
    cursor.close()

    print ("mean : %.4f " % numpy.mean(gpas))
    print ("median : %.4f" % numpy.median(gpas))
    print ("std : %.4f" % numpy.std(gpas))

    return gpas


def gather_student_history(testers):
    cnx = utils.get_connetion("advisor", "passadvise", "localhost", "ADVISING")

    cursor = cnx.cursor(buffered=True)
    hists = []
    sql = "select GRADE,CLASS_NAME,SEMESTER_TAKEN from class_list_tester where STUDENT_ID = %s"
    min = 1
    max = 5001
    if testers:
        min = 5001
        max = 5501

    for x in range(min,max):
        student_hist = []
        key = (str(x),)
        cursor.execute(sql, key)
        results = cursor.fetchall()
        for result in results:
            class_pair = [result[1], result[0], result[2]]
            student_hist.append(class_pair)
        hists.append(student_hist)

    cursor.close()
    cnx.close()
    return hists

def check_bonus_effect(core_path, elective_path, testers):
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", ",", False)
    bonus_class_ref = {}

    for course in core_data:
        if course[5] != "":
            bonus_class_ref[course[0]] = course[5]
    for course in elective_data:
        if course[5] != "":
            bonus_class_ref[course[0]] = course[5]

    grade_sets_no_bonus = []
    grade_sets_bonus = []

    student_histories = gather_student_history(testers)

    for hist in student_histories:
        taken_classes = []
        for datas in hist:
            if datas[0] in bonus_class_ref:
                bonus_classes = bonus_class_ref[datas[0]].split(";")
                found = False
                for b_class in bonus_classes:
                    if b_class in taken_classes:
                        found = True
                if found:
                    grade_sets_bonus.append(float(datas[1]))
                else:
                    grade_sets_no_bonus.append(float(datas[1]))
            taken_classes.append(datas[0])

    prefix = "student"
    if testers:
        prefix = "cohort"

    print(prefix + " bonus course")
    print ("mean : %.4f " % numpy.mean(grade_sets_bonus))
    print ("median : %.4f" % numpy.median(grade_sets_bonus))
    print ("std : %.4f" % numpy.std(grade_sets_bonus))

    print(prefix + " normal course")
    print ("mean : %.4f " % numpy.mean(grade_sets_no_bonus))
    print ("median : %.4f" % numpy.median(grade_sets_no_bonus))
    print ("std : %.4f" % numpy.std(grade_sets_no_bonus))



    trace0 = go.Box(
        y=grade_sets_bonus,
        name=prefix + ' grade_sets_bonus',
        marker=dict(
            color='rgb(214, 12, 140)',
        )
    )
    trace1 = go.Box(
        y=grade_sets_no_bonus,
        name=prefix+' grade_sets_no_bonus',
        marker=dict(
            color='rgb(0, 128, 128)',
        )
    )
    data = [trace0, trace1]
    py.plot(data)

def semester_dissolve(hist):
    semester_dict = {}
    for course in hist:
        semester = course[2]
        if semester in semester_dict:
            temp = semester_dict[semester]
            temp.append(course)
            semester_dict[semester] = temp
        else:
            temp = [course]
            semester_dict[semester] = temp
    return semester_dict


def check_class_load_effect(core_path, elective_path, testers):
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", ",", False)
    exceptional_classes = []

    for course in core_data:
        if course[3] != "1": #BE SURE TO CHECK THIS CORRECT CHECK
            exceptional_classes.append(course[0])
    for course in elective_data:
        if course[3] != "1":
            exceptional_classes.append(course[0])

    grade_sets_no_penalty = []
    grade_sets_penalty = []

    student_histories = gather_student_history(testers)

    for hist in student_histories:
        semesters = semester_dissolve(hist)
        for semester in semesters:
            course_count = len(semesters[semester])
            semester_courses = semesters[semester]
            penalty_class = False
            grade_set = []
            for course in semester_courses:
                if course[0] in exceptional_classes:
                    penalty_class = True
                grade_set.append(float(course[1]))
            if (penalty_class and course_count >= 5) or course_count > 5:
                #grade_sets_penalty.append(float(course[1]))
                grade_sets_penalty.append(numpy.mean(grade_set))

            else:
                #grade_sets_no_penalty.append(float(course[1]))
                grade_sets_no_penalty.append(numpy.mean(grade_set))
    prefix = "student"
    if testers:
        prefix = "cohort"

    print(prefix+" penalty course")
    print ("mean : %.4f " % numpy.mean(grade_sets_penalty))
    print ("median : %.4f" % numpy.median(grade_sets_penalty))
    print ("std : %.4f" % numpy.std(grade_sets_penalty))

    print(prefix+" normal course")
    print ("mean : %.4f " % numpy.mean(grade_sets_no_penalty))
    print ("median : %.4f" % numpy.median(grade_sets_no_penalty))
    print ("std : %.4f" % numpy.std(grade_sets_no_penalty))


    trace0 = go.Box(
        y=grade_sets_penalty,
        name=prefix + ' penalty course grades',
        marker=dict(
            color='rgb(214, 12, 140)',
        )
    )
    trace1 = go.Box(
        y=grade_sets_no_penalty,
        name=prefix +' normal course grades',
        marker=dict(
            color='rgb(0, 128, 128)',
        )
    )
    data = [trace0, trace1]
    py.plot(data)




#gpa_result = calc_gpa_histogram(False)

#gpa_result = calc_gpa_histogram(True)

#generate_class_histogram_data( "/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
   #                        "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", False)

#generate_class_histogram_data( "/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
  #                         "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", True)

#check_class_load_effect("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
 #                          "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", False)

#check_bonus_effect("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
#                           "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", False)


#check_class_load_effect("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
#                          "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", True)

#check_bonus_effect("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
 #                         "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv", True)