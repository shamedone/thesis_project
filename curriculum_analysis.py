import utils
import import_tools
from db_classes import SmallCourse
import numpy as np
from scipy import stats
from scipy.stats import pearsonr
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn import linear_model


#tester class for random forest
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

#creates new dataframe for correlation analysis
def create_corr_dataframe(students, course_fields, course_list, time_isolation, target): #cor_fields names
    columns = []
    all_data = []

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
        if time_isolation:
            try:
                target_course = student.unique_courses[target]
            except KeyError:
                continue

        for course in course_list:
            try:
                crs = student.unique_courses[course]
                if int(crs.repeat) == 1:
                    crs = crs.past_attempts[0]
                #if time_isolation and crs.seq_int >= target_course.seq_int and crs.name != target_course.name:
                if time_isolation and crs.seq_int != target_course.seq_int and crs.name != target_course.name:
                    raise KeyError
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
                #if time_isolation:
                    #use = False
                for x in range(0, len(course_fields)+1):
                    student_data.append(np.nan)
        all_data.append(student_data)
    print("****")
    print(len(all_data))
    print("****")

    df = pd.DataFrame(np.asarray(all_data), columns=columns)

    return df

#tester function for linear regression
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



def pearsonr_pval(x,y):
    return pearsonr(x,y)[1]


def correlation_analysis(df, filename):
    corrmat = df.corr(method='pearson', min_periods=25)
    pvaL_corrmat = df.corr(method=pearsonr_pval, min_periods=25)
    corrmat.to_excel(filename + ".xlsx")
    pvaL_corrmat.to_excel(filename + "_pvals.xlsx")


#function to sequential impact tests. Runs two sql queries, one to collect all students who took coures A before B,
#and then again to collect all those who took B before A. Returns list of positive relationsthips (A before B), and
# #negative (B before A) in small coures object, which contains a flag to identifiy students who took B but never took A
# "NT" or who took them out of ordere "OOO". "NT" results were never used.
def grade_compare_positive_query(course_a, course_b, cnx):
    positive_results = []
    negative_results = []
    cursor = cnx.cursor(buffered=True)
    #sql = "select distinct(a.ref_id), a.student_id, a.course_name, a.grade, b.course_name, b.grade from course_data a join course_data b on" \
    #      " a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and a.semester = b.semester " \
    #      "and a.repeat_ = 0 order by a.student_id"
    sql_pos = "select distinct(b.ref_id), b.student_id, b.course_name, b.grade, a.course_name, a.grade from course_data a join course_data b on" \
          " a.student_id = b.student_id where a.course_name = %s and b.course_name = %s and a.semester <  b.semester " \
          "and a.repeat_ = 0 and b.repeat_ = 0 order by a.student_id"
#          " a.student_id = b.student_id where a.type = %s and b.course_name = %s and a.semester " + compare_op +" b.semester order by a.student_id"
    key = (course_a, course_b)
    cursor.execute(sql_pos, key)
    results = cursor.fetchall()
    for result in results: # Results are a list of students who took a before b. Grades are of course B when taken class a prior
        temp = SmallCourse()
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        positive_results.append(temp)

    #old combined sql query
    sql_combo_neg = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join course_data " \
          "y on x.student_id = y.student_id where x.repeat_ = 0 and y.repeat_= 0 and ((x.course_name = %s and y.course_name = %s and" \
          " x.semester < y.semester) OR (%s not in (select course_name from course_data where student_id = x.student_id) " \
          "and x.course_name = %s)) order by x.student_id"

    sql_never_take = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join " \
                     "course_data y on x.student_id = y.student_id where x.repeat_= 0 and %s not in " \
                     "(select course_name from course_data where student_id = x.student_id) and " \
                     "x.course_name = %s order by x.student_id"

    sql_out_of_order = "select distinct(x.ref_id), x.student_id, x.course_name, x.grade from course_data x join "\
                        "course_data y on x.student_id = y.student_id where x.repeat_ = 0 and y.repeat_= 0 and " \
                        "(x.course_name = %s and y.course_name = %s and x.semester < y.semester)"

    #old_key and execute
    key = (course_b, course_a, course_a, course_b)
    cursor.execute(sql_combo_neg, key)
    results = cursor.fetchall()
    for result in results:
        temp = SmallCourse()  # grades are of class b and of students who did not take class a before b.
        temp.student_id = result[1]
        temp.course_name = result[2]
        temp.grade = result[3]
        temp.flag = "combo"
        negative_results.append(temp)

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

#same as sequence impact function above but instead with equivalent grades, only looking for courses taken same time for
#postive relationships and out of order for negative.
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

#builds grad dict. Returns dict of all possible pairs of course combinations. The key is the course combination (MATH226_MATH227),
#and the value is a list of students with that relationship based on using the above two functions
def build_grade_comp(compare_type):
    comp_dict = {}
    course_cat = import_tools.get_course_names_by_type()
    core_courses = course_cat['core']
    compare_courses = course_cat['core']
    compare_courses.extend(course_cat['elective'])
    compare_courses.extend(["MATH228", "MATH199", "MATH109", "MATH400", "MATH338", "MATH245"])
    #compare_courses.extend(course_cat['ge'])

    ran_courses = []
    for x in range(0, len(core_courses)):
        print("build " + str(x+1) + " of " + str(len(core_courses)))
        course_b = core_courses[x]
        for course_a in compare_courses:
            ran_courses.append([course_a, course_b])
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
    #for crs in ran_courses:
    #    print(crs)
    return comp_dict


#function set up to run iteratively overall CS couress, and test each pair based on set of courses flagged, run type (equiv or sequence,
# grade dict, and score_type ("NT", or "OOO")
def iterative_impact_comp(test_course, students, run_type, comp_dict, score_type): #  TO DO update to reflect this is
    course_cat = import_tools.get_course_names_by_type()
    prereq_cat = []
    core_courses = course_cat['core']
    #test courses can be one of prereqs for prereqs only , allall_cs for only CSC core courses, and allall for all courses in DB.
    if test_course == 'prereqs':
        prereq_cat = import_tools.get_class_prereqs()
        core_courses = list(prereq_cat.keys())

    elif type(test_course) is list:
        compare_courses = test_course

    elif test_course == "allall_cs":
        compare_courses = course_cat['core']
        compare_courses.extend(course_cat['elective'])
        compare_courses.extend(["MATH228", "MATH199", "MATH109", "MATH400", "MATH338", "MATH245", "MATH59", "MATH60",
                                "MATH70", "MATH197", "MATH199", "PHYS121", "PHYS111", "PHYS112", "PHYS101"])
    elif test_course == "allall":
        compare_courses = course_cat['core']
        compare_courses.extend(course_cat['elective'])
        compare_courses.extend(course_cat['ge'])
    else:
        compare_courses = (course_cat['elective'])



    #header of output
    result_set = [["course_a", "op", "course_b", "t", "p", "pos_n", "pos_min_max", "pos_mean", "pos_vari", "neg_n", "neg_min_max",
                  "neg_mean", "neg_vari"]]

    op = " before "
    for course_b in core_courses:
        if test_course == 'prereqs':
            compare_courses = prereq_cat[course_b]
        for course_a in compare_courses:
            #print(course_a)
            if course_a == course_b or course_a == "":
                continue
            if run_type == 'equiv':
                op = " concurrent "
                #compare_data = grade_compare_equiv(course_a, course_b, cnx=utils.get_connection())
                #comp_results = comp_dict[course_a+"_"+course_b]
                #comp_results = [[compare_data[0], compare_data[1], course_a, course_b],
                #              [compare_data[2], compare_data[3], course_b, course_a]]
                #compare_data = grade_compare_positive_query(course_a, course_b, cnx=utils.get_connection()) # testing effect of taking course a before b and not.
            try:
                comp_results = comp_dict[course_a+"_"+course_b]

            except KeyError:
                print("comp not found " + course_a+"_"+course_b )
                continue
            for result in comp_results:
                try:
                    output = calc_pval_tval(result[0], result[1], score_type, filter=students, starter=[result[2], op, result[3]])
                    result_set.append(output)

                except ValueError:
                    #print(result)
                    continue

#        print(results)
    return utils.remove_dupes(result_set)


#not used anymore
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

#function takes positive and negative relationships, scoring type, and then calcs pvalues for each coures relationship.
def calc_pval_tval(positive_data, negative_data, score_type, **kwargs):
    positive_scores = []
    negative_scores = []
    student_ids = set()
    output = []
    op = kwargs['starter'][1]
    #filter keyword allows to filter out stdents at this stage.
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
        #checks for scoring type, all or concurrent
        if score_type != "all":
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


    #calcs necessary data
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


