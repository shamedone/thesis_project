import utils
import import_tools
import dataset_stage as ds
from db_classes import SmallCourse
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import linear_model
#need GE testing.


def find_trip_classes(students, **kwargs):
    trip_dict = {}
    semester_dict = {}
    trip_output = [["course", "times in final semester"]]
    semester_output = [["semester", "times final semester"]]
    do_count = 0
    for student in students:
        if student.status != "dropout":
            continue
        do_count+=1
        max_semester = student.sem_seq_dict[len(student.sem_seq_dict)]
        print(student.sem_seq_dict)
        print(len(student.sem_seq_dict))
        print(max_semester)
        max_semester_courses = student.course_seq_dict[len(student.sem_seq_dict)]
        utils.sum_to_dict(len(student.sem_seq_dict), 1, semester_dict)
        for crs in max_semester_courses:
            utils.sum_to_dict(crs.name, 1, trip_dict)
            #print(crs.name)
    for crs in trip_dict:
        #print(crs+","+str(trip_dict[crs]))
        trip_output.append([crs,str(trip_dict[crs]),str(float(trip_dict[crs]/do_count))])

    for sems in semester_dict:
        semester_output.append([str(sems), str(semester_dict[sems])])

    print(do_count)
    return trip_output, semester_output

def generic_impact_rf_feature_extract(df, target_name):
    output = [[target_name+"_feature_impacts_decision_tree"]]
    localDF = df.copy(deep=True)
    target = pd.DataFrame(localDF[target_name], columns=[target_name])
    localDF = localDF.drop(columns=target_name)
    classifier = RandomForestClassifier(n_estimators=400)
    classifier.fit(localDF, target[target_name])
    for x in range(0, len(localDF.columns)):
        #print(localDF.columns[x] + "," + str(classifier.feature_importances_[x]))
        output.append([localDF.columns[x], str(classifier.feature_importances_[x])])
    return output


def create_custom_dataframe(students, student_fields, course_fields, course_list): #cor_fields names
    columns = []  #TODO replace summary with fields.
    all_data = []

    if "status" in student_fields:
        columns.append("status")
    if "sex" in student_fields:
        columns.append("sex")
    if "ethnicity" in student_fields:
        columns.append("ethnicity")
    if "resident_status" in student_fields:
        columns.append("resident_status")
    if "admin_decript" in student_fields:
        columns.append("admin_decript")
    if "prep_summary" in student_fields:
        columns.append("prepardness")

    for course in course_list:
        columns.append(course + "_grade")
        for field in course_fields:
            columns.append(course+"_"+field)
            #columns.append(field+"_sfu")
            #columns.append(field+"_seq")
            #columns.append(field+"_prior_ges")
            #columns.append(field+"_conc_ge")
    for student in students:
        student_data = []
        use = True
        if "status" in student_fields:
            student_data.append(student.status)
        if "sex" in student_fields:
            student_data.append(student.sex)
        if "ethnicity" in student_fields:
            student_data.append(student.ethnic)
        if "resident_status" in student_fields:
            student_data.append(student.resident_status)
        if "admin_descript" in student_fields:
            student_data.append(student.admin_descript)
        if "prep_summary" in student_fields:
            student_data.append(student.prep_assess_summary)
        for course in course_list:
            try:
                crs = student.unique_courses[course]
                student_data.append(crs.grade)
                if "tu" in course_fields:
                    student_data.append(crs.term_units)
                if "sfsu_u" in course_fields:
                    student_data.append(crs.sfsu_units)
                if "tech_u" in course_fields:
                    student_data.append(crs.tech_load)
                if "ge_u" in course_fields:
                    student_data.append(crs.ge_load)
                if "seq_int" in course_fields:
                    student_data.append(crs.seq_int)
                if "age" in course_fields:
                    student_data.append(crs.student_age)
                if "repeat" in course_fields:
                    student_data.append(crs.repeat)
                if "ge_count" in course_fields:
                    ge_count = 0
                    for course in student.course_history:
                        if course.course_type == "ge" and course.seq_int < crs.seq_int:
                            ge_count += 1
                    student_data.append(ge_count)
                if "core_count" in course_fields:
                    core_count = 0
                    course_list = student.course_seq_dict[crs.seq_int]
                    for course in student.course_history:
                        if course.course_type == "ge" and course.seq_int < crs.seq_int and course.repeat == 0:
                            core_count += 1
                    student_data.append(core_count)

            except KeyError:
                #use = False
                for x in range(0, len(course_fields)+1):
                    student_data.append(-999)
        if use:
            all_data.append(student_data)
    print("****")
    print(len(all_data))
    print("****")

    df = pd.DataFrame(np.asarray(all_data), columns=columns)

    return df

def LinearRegression(df,target_name):
    output = [[target_name+"_feature_impacts"]]
    localDF = df.copy(deep=True)
    target = pd.DataFrame(localDF[target_name], columns=[target_name])
    localDF = localDF.drop(columns=target_name)
    lm = linear_model.LinearRegression()
    model = lm.fit(localDF,target[target_name])
    for x in range(0, len(localDF.columns)):
        #print (localDF.columns[x]+","+str(model.coef_[x]))
        output.append([localDF.columns[x], str(model.coef_[x])])
    return output

def correlation_analysis(df, filename):
    df = pd.DataFrame(df, dtype=np.float)
    corrmat = df.corr(method='pearson')
    corrmat.to_excel(filename+".xlsx")
    return

def prereq_correlation_analysis(students, course, prereqs, filename): #cor_fields names
    columns = []
    all_data = []
    for field in prereqs:
        columns.append(field+"_grade")
        columns.append(field+"_tu")
        columns.append(field+"_tech_u")
        columns.append(field+"_ge_u")
        columns.append(field+"_sfsu_units")
        columns.append(field+"_seq")
    for student in students:
        student_data = []
        use = True
        for field in prereqs:
            try:
                crs = student.unique_courses[field]
                student_data.append(crs.grade)
                student_data.append(crs.term_units)
                student_data.append(crs.tech_load)
                student_data.append(crs.ge_load)
                student_data.append(crs.sfsu_units)
                student_data.append(crs.seq_int)
            except KeyError:
                use = False
        if use:
            all_data.append(student_data)

    df = pd.DataFrame(np.asarray(all_data), columns=columns)
    corrmat = df.corr()

    f, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(corrmat, ax=ax, cmap="YlGnBu", linewidths=0.1)

    plt.show()
    plt.savefig(filename+".png", quality=95)
    corrmat.to_excel(filename+".xlsx")


def custom_corr_analysis(students):

    return


def grade_compare_by_course_load(query_course, load_v, load_type, cnx):
    positive_results = []
    negative_results = []
    cursor = cnx.cursor(buffered=True)
    key = (query_course, load_v)
    sql = "select distinct(ref_id), student_id, course_name, grade from course_data where course_name = %s and  "+load_type+" >= %s"
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        positive_results.append(temp)
    sql = "select distinct(ref_id), student_id, course_name, grade from course_data where course_name = %s and "+load_type+" < %s"
    key = (query_course, load_v)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        negative_results.append(temp)
    cursor.close()
    return positive_results, negative_results

def class_type_grade_compare(course_a, type, compare_op, cnx):
    positive_results = []
    negative_results = []
    cursor = cnx.cursor(buffered=True)
    sql = "select distinct(a.ref_id), a.student_id, a.course_name, a.grade, b.course_name, b.grade from course_data a join course_data b on" \
          " a.student_id = b.student_id where a.course_name = %s and b.type = %s and a.semester " + compare_op +" b.semester "\
          "and a.repeat_ = 0  order by a.student_id"
#          " a.student_id = b.student_id where a.type = %s and b.course_name = %s and a.semester " + compare_op +" b.semester order by a.student_id"
    key = (course_a, type)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        positive_results.append(temp)

    sql = "select distinct(a.ref_id), a.student_id, a.course_name, a.grade, a.semester from course_data a join course_data " \
          "b on a.student_id = b.student_id where (a.course_name = %s and b.type = %s and" \
          " b.semester "+compare_op+" a.semester) OR (%s not in (select type from course_data where student_id = a.student_id) " \
          "and a.course_name = %s) and a.repeat_ = 0 order by a.student_id;"
    key = (course_a, type, type, course_a)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        negative_results.append(temp)
    cursor.close()
    return positive_results, negative_results


def grade_compare_positive_query(course_a, course_b, cnx):  # TODO make equiv function
    positive_results = []
    negative_results = []
    cursor = cnx.cursor(buffered=True)
    #sql = "select distinct(a.ref_id), a.student_id, a.course_name, a.grade, b.course_name, b.grade from course_data a join course_data b on" \
    #      " a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and a.semester = b.semester " \
    #      "and a.repeat_ = 0 order by a.student_id"
    sql = "select distinct(b.ref_id), b.student_id, b.course_name, b.grade, a.course_name, a.grade from course_data a join course_data b on" \
          " a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and a.semester <  b.semester " \
          "and a.repeat_ = 0 and b.repeat_ = 0 order by a.student_id"
#          " a.student_id = b.student_id where a.type = %s and b.course_name = %s and a.semester " + compare_op +" b.semester order by a.student_id"
    key = (course_a, course_b)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results: # Results are a list of students who took a before b. Grades are of course B when taken class a prior
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        positive_results.append(temp)

    #old combined sql query
    #sql = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join course_data " \
    #      "y on x.student_id = y.student_id where x.repeat_ = 0 and y.repeat_= 0 and ((x.course_name b = %s and y.course_name = %s a and" \
    #      " x.semester < y.semester) OR (%s a not in (select course_name from course_data where student_id = x.student_id) " \
    #      "and x.course_name = %s b)) order by x.student_id"

    sql_never_take = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join " \
                     "course_data y on x.student_id = y.student_id where x.repeat_= 0 and %s not in " \
                     "(select course_name from course_data where student_id = x.student_id) and " \
                     "x.course_name = %s order by x.student_id"

    sql_out_of_order = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join "\
                        "course_data y on x.student_id = y.student_id where x.repeat_ = 0 and y.repeat_= 0 and " \
                        "(x.course_name = %s and y.course_name = %s and x.semester < y.semester)"

    #old_key and execute
    #key = (course_b, course_a, course_a, course_b)
    #cursor.execute(sql, key)

    key_out_of_order = (course_b, course_a)
    cursor.execute(sql_out_of_order, key_out_of_order)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()   #grades are of class b and of students who did not take class a before b.
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        temp.flag = "OOO"
        negative_results.append(temp)

    key_never_take = (course_a, course_b)
    cursor.execute(sql_never_take, key_never_take)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()  # grades are of class b and of students who did not take class a before b.
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        temp.flag = "NT"
        negative_results.append(temp)


    cursor.close()
    cnx.close()
    return positive_results, negative_results


def grade_compare_equiv(course_a, course_b, cnx):
    positive_results_a = []
    negative_results_b = []
    positive_results_b = []
    negative_results_a = []
    cursor = cnx.cursor(buffered=True)
    sql = "select distinct(b.ref_id), b.student_id, b.course_name, b.grade, a.course_name, a.grade from course_data a" \
          " join course_data b on a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and " \
          "a.semester = b.semester and a.repeat_ = 0 and b.repeat_= 0 order by a.student_id"
    key = (course_a, course_b)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        positive_results_a.append(temp)
        temp_b = SmallCourse()
        temp_b.student_id = result[1]
        temp_b.course_name = result[4]
        temp_b.grade = result[5]
        positive_results_b.append(temp_b)


    #TODO alter this so that the sql occurs in two steps, one for no taken and then one for out of order
    #TODO add flag in small course to capture flag for this
    sql = "select distinct(b.ref_id), b.student_id, b.course_name, b.grade, a.course_name, a.grade from course_data a" \
          " join course_data b on a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and " \
          "a.semester != b.semester and a.repeat_ = 0 and b.repeat_= 0 order by a.student_id"
    key = (course_a, course_b)
    cursor.execute(sql, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        negative_results_a.append(temp)
        temp_b = SmallCourse()
        temp_b.student_id = result[1]
        temp_b.course_name = result[4]
        temp_b.grade = result[5]
        negative_results_b.append(temp_b)
    cursor.close()
    return positive_results_a, negative_results_a, positive_results_b, negative_results_b


def build_grade_comp(compare_type): #  TO DO update to reflect this is
    comp_dict = {}
    course_cat = import_tools.get_course_names_by_type()
    core_courses = course_cat['core']
    compare_courses = course_cat['core']
    compare_courses.extend(course_cat['elective'])
    #compare_courses.extend(course_cat['ge'])

    for x in range(0, len(core_courses)):
        print("build " + str(x+1) + " of " + str(len(core_courses)))
        course_b = core_courses[x]
        for course_a in compare_courses:
            #print("A : " + course_a + " B :" + course_b)
            if course_a == course_b or course_a+"_"+course_b in comp_dict:
                continue
            if compare_type == 'equiv':
                compare_data = grade_compare_equiv(course_a, course_b, cnx=utils.get_connection())
                comp_dict[course_a+"_"+course_b] = [[compare_data[0], compare_data[1], course_a, course_b],
                              [compare_data[2], compare_data[3], course_b, course_a]]
            else:
                compare_data = grade_compare_positive_query(course_a, course_b, cnx=utils.get_connection()) # testing effect of taking course a before b and not.
                comp_dict[course_a + "_" + course_b] = [[compare_data[0], compare_data[1], course_a, course_b]]
    #        print(results)
    return comp_dict



def iterative_impact_comp(test_course, students, run_type, comp_dict): #  TO DO update to reflect this is
    course_cat = import_tools.get_course_names_by_type()
    prereq_cat = []
    core_courses = course_cat['core']

    if test_course == 'prereqs':
        prereq_cat = import_tools.get_class_prereqs()
        core_courses = list(prereq_cat.keys())

    elif type(test_course) is list:
        compare_courses = test_course

    elif test_course == "allall_cs":
        compare_courses = course_cat['core']
        compare_courses.extend(course_cat['elective'])
    elif test_course == "allall":
        compare_courses = course_cat['core']
        compare_courses.extend(course_cat['elective'])
        compare_courses.extend(course_cat['ge'])
    else:
        compare_courses = (course_cat['elective'])



    result_set = [["course_a", "op", "course_b", "t", "p", "pos_n", "pos_min_max", "pos_mean", "pos_vari", "neg_n", "neg_min_max",
                  "neg_mean", "neg_vari"]]

    op = " before "
    for course_b in core_courses:
        if test_course == 'prereqs':
            compare_courses = prereq_cat[course_b]
        for course_a in compare_courses:
            print(course_a)
            if course_a == course_b or course_a == "":
                continue
            if run_type == 'equiv':
                op = " concurrent "
                #compare_data = grade_compare_equiv(course_a, course_b, cnx=utils.get_connection())
                #comp_results = comp_dict[course_a+"_"+course_b]
                #comp_results = [[compare_data[0], compare_data[1], course_a, course_b],
                #              [compare_data[2], compare_data[3], course_b, course_a]]
                #compare_data = grade_compare_positive_query(course_a, course_b, cnx=utils.get_connection()) # testing effect of taking course a before b and not.
            comp_results = comp_dict[course_a+"_"+course_b]
            for result in comp_results:
                try:
                    output = calc_pval_tval(result[0], result[1], filter=students, starter=[result[2], op, result[3]])
                    result_set.append(output)

                except ValueError:
                    print(result)
                    continue

#        print(results)
    return utils.remove_dupes(result_set)



def iterative_impact_prereq(students):  #need to double chack courses are labled correctly.
    course_cat = import_tools.get_class_prereqs()  # TODO Fix thhese two outputs to be nmore readable. make the header go first, then sort results, then print.
    result_set = [["course a", "op", "course_b", "t", "p", "pos_n", "pos_min_max", "pos_mean", "pos_vari", "neg_n",
                   "neg_min_max", "neg_mean", "neg_vari"]]
    for crs in course_cat:  #course cat has crs -> prereq, prereq, preeq
        test_courses = course_cat[crs]
        results = []
        for test in test_courses: #prereqs
            compare_data = grade_compare_positive_query(crs, test, ">", cnx=utils.get_connection())
            try:
                result = calc_pval_tval(compare_data[0], compare_data[1], filter=students,
                                        starter=[crs], test=test)
            except ValueError:
                result = [test, crs, "NO RESULTS", 999]
            results.append(result)
        #print("********")
        #print(results)
        results.sort(key=lambda x: x[0]+str(x[3]))
        result_set.extend(results)
    return result_set

def calc_pval_tval(positive_data, negative_data, **kwargs):
    positive_scores = []
    negative_scores = []
    student_ids = set()
    output = []
    op = kwargs['starter'][1]
    if 'filter' in kwargs:
        for student in kwargs['filter']:
            student_ids.add(student.id_num)
    for data in positive_data:
        if 'filter' in kwargs and data.student_id not in student_ids:
            continue
        positive_scores.append(int(data.grade))
    for data in negative_data:
        if 'filter' in kwargs and data.student_id not in student_ids:
            continue
        if 'score_type' in kwargs:
            score_type = kwargs['score_type']
            if score_type == data.flag or 'concurrent' in op:
                negative_scores.append(int(data.grade))
            else:
                continue
        else:
            negative_scores.append(int(data.grade))

    #print("postives:")

    if len(positive_scores) <= 0:
        #print("no positive")
        raise ValueError

    #print("negatives:")
    if len(negative_scores) <= 0:
        #print("no negative")
        raise ValueError

    t2, p2 = stats.ttest_ind(positive_scores, negative_scores, equal_var=False)
    #print("t = " + str(t2))
    #print("p = " + str(p2))

    if 'starter' in kwargs:
        output.extend(kwargs['starter'])
    pos_data = stats.describe(positive_scores)
    neg_data = stats.describe(negative_scores)
    output.append(t2)
    output.append(p2)
    output.append(pos_data.nobs)
    output.append(str(pos_data.minmax).replace(",",";"))
    output.append(pos_data.mean)
    output.append(pos_data.variance)
    output.append(neg_data.nobs)
    output.append(str(neg_data.minmax).replace(",",";"))
    output.append(neg_data.mean)
    output.append(neg_data.variance)
    #print(output)
    return output




#parses through list of students, filtering out those that dont have the binning courses or the test courese
#Calculates binned grade. Binned classes are those we are binning based off of, req sre those needed for analysis
def bin_students_by_course(students, bin_course_list, req_classes):
    bin_dict = {}

    for student in students:
        go = True
        bin_grade = 0
        for course in bin_course_list:
            if course not in student.unique_courses:
                go = False
                continue
            if student.unique_courses[course].repeat == True: #no repeates allowed in binned classes.
                go = False
                continue
            bin_grade+= student.unique_courses[course].grade

        for course in req_classes:
            if course not in student.unique_courses:
                go = False
                continue

        if go:
            bin_grade = bin_grade/float(len(bin_course_list))
            if bin_grade > 89:
                utils.add_to_dict_list("A", student, bin_dict)
            elif bin_grade > 79:
                utils.add_to_dict_list("B", student, bin_dict)
            elif bin_grade > 69:
                utils.add_to_dict_list("C", student, bin_dict)
            elif bin_grade > 59:
                utils.add_to_dict_list("D", student, bin_dict)
            elif bin_grade > 49:
                utils.add_to_dict_list("F", student, bin_dict)
    return bin_dict

#testing impact of query course(s) on test course(s)
#semester param limits where the query courses are taken
def test_list_by_course(test_list, query_course_list, test_course_list, **kwargs): #right now we are going to include summer school

    positive_list = [] #students who meet req
    positive_score_set = []
    negative_list = [] #students who do not meet req
    negative_score_set = []

    for student in test_list:
        positive = False
        course_list = student.unique_courses
        if 'semester_limits' in kwargs:
            semester_list = {}
            for sem in kwargs['semester_parm']: #if semester limit set, only pull classes from specific semesters.
                temp = student.sem_seq_dict[sem]
                for crs in temp:
                    semester_list[crs.name] = crs
            course_list = semester_list
        inc = True
        for course in query_course_list: #first check for query course
            if course not in course_list:
                inc = False
                continue
            if "query_load_lim" in kwargs:
                temp = course_list[course]
                if temp.semester_load not in kwargs['query_load_lim']:
                    inc = False

        score_set = []
        for course in test_course_list:
            student_course = student.unique_courses[course]
            if student_course.repeat == True:
                student_course = student_course.past_attempts[0] #this may be issue, i am taking the first time that student took that class.
            score_set.append(student_course.grade)
        if inc:
            positive_list.append(student)
            positive_score_set.append(score_set)
        else:
            negative_list.append(student)
            negative_score_set.append(score_set)

    return [positive_list, positive_score_set, negative_list, negative_score_set]

def perform_count():
    count_dict = {}
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    sql = "select course_name from course_data"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        class_name = result[0]
        utils.sum_to_dict(class_name, 1, count_dict)
    for course in count_dict:
        print(course + ","+str(count_dict[course]))


def compare_course_pairing(students, course_set, **kwargs):
    #TODO comment on 9/28, idk what this
    positive_grades = []
    negative_grades = []

    for student in students:
        compare_set = {}
        for course in student.course_history:
                if course.name in course_set:
                    utils.add_to_dict_list(course.seq_int, course, compare_set)
        for comps in compare_set:
            pairs = compare_set[comps]
            temp = set()
            datas = []
            semester_check = True
            if 'sem_check' in kwargs:
                if comps != kwargs['sem_check']:
                    semester_check = False
            for pair in pairs:
                temp.add(pair.name)
                temp_course = SmallCourse()
                temp_course.grade = pair.grade
                temp_course.student_id = pair.student_id
                temp_course.name = pair.name
                datas.append(temp_course)
            if len(temp) > 1 and semester_check:
                positive_grades.extend(datas)
            else:
                negative_grades.extend(datas)

    return positive_grades, negative_grades


