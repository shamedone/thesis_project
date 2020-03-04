import dataset_stage as ds
import dataset_predictor as dp
import curriculum_analysis as ca
import import_tools as it
import output_tools as ot
import series_analysis as sa
import group_analysis as ga
import utils

def import_students_dict():
    students_raw = utils.list_from_file(
        "/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_data_v2.csv", "\n", ",", True)
    student_dict = it.build_student_dict(students_raw, student_id=0, sex=4, ethnic=5, age=6, resident_status=7,
                                         standing=8,
                                         admin_descript=9, crs_abbr=15, crs_num=16, grade_str=21, year_int=3, term_gpa=22,
                                         sfsu_gpa=23, term_units=25, sfsu_units=26, grad_flag=31, spring_19_flag=35,
                                         crs_college_long=19, crs_dept_long=20, total_units=27)
    return student_dict


def import_student_data():
    student_dict = import_students_dict()
    students = utils.dict_to_list(student_dict)
    ds.build_student_class_seq(students)
    ds.calc_sem_avg_grade(students)
    for student in students:
        student.calc_semester_load()
        student.major = "CSC"
    ds.update_final_cs_gpa(students)
    ds.update_final_gpa(students)
    ds.flag_serious(students)
    ds.label_student_prepardness(students)
    ds.update_load_list(students)
    ds.label_drop_outs_sfsu(students)
    it.persist_student_data(students)
    return 0
    #init_students(students)


def sfsu_class_impact_run():
    student_dict = import_students_dict()
    sfsu_class_dict = ds.build_class_key_vector(student_dict)

    students = utils.dict_to_list(student_dict)

    it.build_student_class_seq(students)
    for student in students:
        student.calc_semester_load()
        student.major = "CSC"
    binned_students = ca.bin_students_by_course(students,["CSC210"],["CSC340"])
    results = {}
    for bin in binned_students:
        data = ca.test_list_by_course(binned_students[bin],["CSC211"],["CSC340"],query_load_lim=[3,4])
        results[bin] = data
        print(bin)
        print(results[bin][1])
        print(results[bin][3])
    return results

def sfsu_do_run():
    #analyze_series("/Users/thomasolson/Documents/workspace/advising_revamp/journal.pone.0171207.s008.csv")
    students = it.package_student_data()
    sfsu_class_dict = ds.build_class_key_vector(students, generic_ge=True)
    ds.build_variable_student_vector(students, sfsu_class_dict, 4)
    pred_sets = dp.split_dataset(students, sfsu_do_run=True, sem_count=4) #This current make up does not account or semesters. we need to create a new run
    pred_result = dp.classifiy_dropout(pred_sets[0], pred_sets[1], "master")
    df = ot.students_to_pandas(pred_result, student_prediction="status")
    df.to_excel("/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_do_g_check.xlsx")

def sequence_analysis_old():
    students = it.package_student_data(admin='1', status='graduated')
    sa.run_sequence_mining(students,20,None)
    #transactions = sa.build_class_transactions(students)
    #sa.run_apriori(transactions, [1,2,3,4,5,6,7,8], .13, .5)
    print("******")
    students = it.package_student_data(admin='1', status='dropout')
    sa.run_sequence_mining(students,20,None)

    #transactions = sa.build_class_transactions(students)
    #sa.run_apriori(transactions, [1,2,3,4,5,6,7,8], .13, .5)
    #compare_data = ca.compare_course_pairing(students, ["CSC256", "CSC340"], sem_check=4)
    #ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)

def sequence_analysis(students, filter_type, support):
    output = [["count", "seq_length", "sequence"]]
    datas = sa.run_sequence_mining(students, support, filter_type)
    for data in datas:
        if len(data[1][0]) < 3:
            continue
        output.append([data[0], str(len(data[1][0])),";".join(data[1][0])])
    return output


def cluster_run(n):
    students = it.package_student_data()
    sfsu_class_dict = ds.build_class_key_vector(students)
    #ds.build_student_vector_test(students, sfsu_class_dict, 4)
    ds.build_student_vector_cs_only(students, sfsu_class_dict, 4)
    pred_sets = dp.split_dataset(students, sfsu_do_run=True) #This current make up does not account or semesters. we need to create a new run
    filtered_students = []
    filtered_students.extend(pred_sets[1])
    filtered_students.extend(pred_sets[0])
    #dp.cluster_plots(students)
    clust_result = dp.cluster_run(filtered_students, n)
    #df = it.students_to_pandas(clust_result, student_prediction="cluster")
    #df.to_excel("/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_clust_csonly_run_"+str(n)+".xlsx")
    return


    #ds.analyze_drop_outs(students, outpath="/Users/thomasolson/Documents/workspace/advising_revamp/dropout_G1042_data.csv")


def class_vects():
    ds.print_class_dict("/Users/thomasolson/Documents/workspace/advising_revamp/G1077_data.csv",
                        outpath="/Users/thomasolson/Documents/workspace/advising_revamp/class_ints_G1077_data.csv" )
    ds.print_class_dict("/Users/thomasolson/Documents/workspace/advising_revamp/G1042_data.csv",
                        outpath="/Users/thomasolson/Documents/workspace/advising_revamp/class_ints_G1042_data.csv" )


def course_impact_run(query_course, prep_courses, students):
    print("---------------------------")
    print(",".join(prep_courses) +"-->"+ query_course)
    ca.generic_impact(students, query_course, prep_courses)
    print("---------------------------")


def run_update():
    cnx = utils.get_connection("advisor", "passadvise", "localhost", "SFSU_STUDENT_HISTORY")
    students = it.package_student_data()
    it.update_student_gpa(cnx, students)
    it.update_course_loads(cnx, students)
    cnx.close()


def load_access(students, course, tech, ge, overall):
    print(course + "*****")
    compare_data = ca.grade_compare_by_course_load(course, tech, "tech_load",
                                                   cnx=utils.get_connection(user="advisor", password="passadvise",
                                                                            host="localhost",
                                                                            database="SFSU_STUDENT_HISTORY"))
    print("tech stats:")
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)

    compare_data = ca.grade_compare_by_course_load(course, ge, "ge_load",
                                                   cnx=utils.get_connection(user="advisor", password="passadvise",
                                                                            host="localhost",
                                                                            database="SFSU_STUDENT_HISTORY"))
    print("ge stats:")

    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)

    print("overall stats:")

    compare_data = ca.grade_compare_by_course_load(course, overall, "term_units",
                                                   cnx=utils.get_connection(user="advisor", password="passadvise",
                                                                            host="localhost",
                                                                            database="SFSU_STUDENT_HISTORY"))
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)

    print("**********")

def get_data_frame():
    students = it.package_student_data()
    df = it.students_to_pandas(students)

    return df


def group_runs(grouping):
    grouping_types = ga.get_grouping_types(grouping)
    all_students = it.package_student_data()
    metrics = ga.dropout_analysis(all_students) # count return
    demos = ga.get_demographic_makeup(all_students)  # list return
    stats = ga.get_grade_stats(all_students) # list return

    ot.dictionary_output_to_list(metrics[0],"count")
    ot.dictionary_output_to_list(demos[0], "list")
    ot.dictionary_output_to_list(stats[0],"list")


    combo_data = [["group", "male", "female", "AmInd", "Black", "Asian", "PacIsl", "Hisp", "White", "Intl", "TwoMore", "Unknown",
                  "Bay Area (6 counties)", "San Diego", "Southern California", "Northern California",
                  "Central California", "U.S. outside of CA", "International", "Freshman_start", "Transitory_Start",
                  "Transfer_Start", "OK", "UN_MATH", "UN_PHYS","UN_PHYS;UN_MATH", "mean_gpa", "mean_cs_gpa",
                  "mean_enrollment_length", "mean_max_student_age", "total_students", "grad_count",
                  "drop_out_count", "dropout_w_u_math", "dropout_w_u_phys", "dropout_w_u_mathphys", "grad_w_u_math",
                  "grad_w_u_phys", "grad_w_u_mathphys", "in_progress_count"]]
    line_data = ["all_groups"]
    line_data.extend(demos[1])
    line_data.extend(stats[1])
    line_data.extend(metrics[1])
    combo_data.append(line_data)

    for result in grouping_types:
        print(result)
        group = ga.filter_students(grouping, result, all_students)
        metrics = ga.dropout_analysis(group)
        demos = ga.get_demographic_makeup(group)
        stats = ga.get_grade_stats(group)
        group_label = ""

        for x in range(0, len(result)):
            label = result[x]
            try:
                group_label += ot.decoder[grouping[x]][int(label)]
            except (KeyError, ValueError) as e:
                group_label += label

        line_data = [group_label]
        line_data.extend(demos[1])
        line_data.extend(stats[1])
        line_data.extend(metrics[1])

        demos = ot.dictionary_output_to_list(demos[0],"list")
        metrics = ot.dictionary_output_to_list(metrics[0],"count")
        stats = ot.dictionary_output_to_list(stats[0],"list")
        metrics.extend(demos)
        metrics.extend(stats)
        utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/" + group_label +
                           "_stats.csv", metrics)
        combo_data.append(line_data)


        #print("hi")

    utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/" + "_".join(grouping) +
                       "_combo_stats.csv", combo_data)

    return combo_data

def combo_run_start_1():
    complete_combo = []
    complete_combo.extend(group_runs(["type_descript_summary"]))
    complete_combo.extend(group_runs(["admin_descript"]))
    complete_combo.extend(group_runs(["resident_status"]))
    complete_combo.extend(group_runs(["ethnicity"]))
    complete_combo.extend(group_runs(["sex"]))
    complete_combo.extend(group_runs(["prep_assess"]))
    complete_combo.extend(group_runs(["prep_assess_summary"]))
    complete_combo = utils.remove_dupes(complete_combo)
    utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/admin_sex_group_run_combo_stats.csv", complete_combo)

def combo_run_start_2():
    complete_combo = []
    complete_combo.extend(group_runs(["admin_descript", "sex"]))




#course_impact_run("CSC340", ["CSC210", "CSC256"], students)
#ca.correlation_analysis(students_temp, ["CSC210", "CSC211", "CSC220", "CSC256", "CSC340"], "corr_test_early_non103")
#load_access(course, "CSC210", 9,9,20)
##load_access(course, "CSC340", 9,9,20)
#load_access(course, "CSC413", 9,9,20)
#load_access(course, "CSC648", 9,9,20)

#course_impact_run("CSC640", ["CSC415", "CSC412"], students)
#course_impact_run("CSC413", ["CSC340"], students)
#course_impact_run("CSC520", ["CSC412"], students)
#course_impact_run("CSC648", ["CSC413", "CSC340"], students)
#students = it.package_student_data()
#ca.perform_count()


def iterative_sequence_tests(students, filter,  **kwargs):
    suffix = ".csv"
    if filter:
        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students)
            suffix = ga.translate_header(kwargs['groupings'], group_set)
            datas = sequence_analysis(filtered_students, kwargs['class_filter'], kwargs['support'])
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/test_series_stats" + suffix+".csv",
                datas)
    else:
         datas = sequence_analysis(students, kwargs['class_filter'], kwargs['support'])
         utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis /series_stats" + suffix,
            datas)


def iterative_impact_tests(students, filter, compare_type, compare_dict, **kwargs):
    suffix = ".csv"
    if filter:  # TODO we need to fix the labels.
        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            print("init")
            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students)
            datas = run_impact_tests(filtered_students, compare_type, compare_dict)
            suffix = ga.translate_header(kwargs['groupings'], group_set)
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/11_26" + compare_type +
                "_prereq_impact_stats" + suffix + ".csv", datas[0])
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/11_26" + compare_type +
                "_elect_impact_stats" + suffix + ".csv", datas[1])
    else:
        datas = run_impact_tests(students, compare_type, compare_dict)
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/11_26" + compare_type +
            "_prereq_impact_stats" + suffix, datas[0])
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/11_26" + compare_type +
            "_all_impact_stats" + suffix, datas[1])

def run_impact_tests(students, comp_type, comp_dict):
    #results_preq = ca.iterative_impact_prereq(students)

    results_preq = ca.iterative_impact_comp("prereqs", students, comp_type, comp_dict)
    results_elect = ca.iterative_impact_comp("allall_cs", students, comp_type, comp_dict)

    return results_preq, results_elect
    #return ["hi", results_elect]


def feature_analysis_tests(students, socio_factors, course_factors, courses, target_course, **kwargs):
    isolation_set = False
    if 'groupings' in kwargs:

        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            if 'isolation' in kwargs:
                isolation_set = kwargs['isolation']

            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students, isolation=isolation_set)
            if len(filtered_students) == 0:
                continue

            suffix = ga.translate_header(kwargs['groupings'], group_set)
            df = ca.create_custom_dataframe(filtered_students, [], course_factors, #socio factors are disabled for lr
                                            courses)
            datas = ca.LinearRegression(df, target_course+"_grade")
            utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/linear_reg_extraction_"
                               + suffix +"_"+target_course +".csv", datas)
            df = ca.create_custom_dataframe(filtered_students, socio_factors, course_factors,
                                            courses)
            datas = ca.generic_impact_rf_feature_extract(df, target_course+"_grade")
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/random_forest_extraction_"
                + suffix +target_course+".csv", datas)
            ca.correlation_analysis(df, "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/corr_grid_"
                                    + suffix +"_"+target_course)
    else:
        df = ca.create_custom_dataframe(students, [], course_factors,
                                        courses,
                                        )
        datas = ca.LinearRegression(df, target_course+"_grade")
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/linear_reg_extraction_allall"+target_course+".csv", datas)
        df = ca.create_custom_dataframe(students, socio_factors, course_factors,
                                        courses,
                                        )
        datas = ca.generic_impact_rf_feature_extract(df, target_course+"_grade")
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/random_forest_extraction_allall"+target_course+".csv", datas)
        ca.correlation_analysis(df,
                                "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/corr_grid_allall_"+target_course)


def init_impact_set():
    students = it.package_student_data()
    compare_dict = ca.build_grade_comp("sequence")
    #iterative_impact_tests(students, False, "sequence", compare_dict)
    iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['admin_descript','ethnicity'])
    iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['ethnicity'])
    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['serious','type_descript'])
    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['serious','admin_descript','type_descript'])
    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['serious', 'sex','admin_descript'])
    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['serious', 'sex','admin_descript','type_descript'])
    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['admin_descript', 'sex'])

    compare_dict = ca.build_grade_comp("equiv")
    iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['admin_descript','ethnicity'])
    iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['ethnicity'])
    #iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['serious','type_descript'])
    #iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['serious','admin_descript', 'type_descript'])
    #iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['serious','sex','admin_descript', 'type_descript'])
    #iterative_impact_tests(students, True, "equiv", compare_dict, groupings=['serious','sex','admin_descript'])
    #iterative_impact_tests(students, False, "equiv", compare_dict)

    #iterative_impact_tests(students, True, groupings=['admin_descript', 'sex','type_descript_summary'])
    #iterative_impact_tests(students, True, groupings=['admin_descript', 'sex'])
    #iterative_impact_tests(students, True, groupings=['admin_descript', 'type_descript_summary', 'sex'])
    #iterative_impact_tests(students, True, groupings=['admin_descript', 'type_descript_summary', 'resident_status'])
    #iterative_impact_tests(students, True, grouping='type_descript_summary')
    #iterative_impact_tests(students, True, grouping='prep_assess_summary')
    #iterative_impact_tests(students, True, grouping='prep_assess')
    #iterative_impact_tests(students, True, grouping='sex')
    #iterative_impact_tests(students, True, grouping='resident_status')


def init_sequence_set():
    students = it.package_student_data()
    #iterative_sequence_tests(students, True, groupings=['resident_status'], class_filter="all", support=30)
    iterative_sequence_tests(students, True, groupings=['admin_descript', 'ethnicity'], class_filter="all", support=30)
    iterative_sequence_tests(students, True, groupings=['ethnicity'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex','admin_descript'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['type_descript_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['prep_assess_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex', 'admin_descript', 'type_descript_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex', 'resident_status', 'type_descript_summary', 'prep_assess_summary'], class_filter="all", support=30)

def init_features_tests():
    students = it.package_student_data()
    #feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
    #                       ["tu", "sfsu_u"],
    #                       ["CSC210", "CSC220", "CSC256", "CSC230", "MATH324", "MATH325", "CSC340", "CSC413", "CSC415", "CSC510", "CSC520", "CSC600"], "CSC600")

                           #["CSC210", "CSC220", "CSC256", "CSC230", "MATH324", "MATH227", "CSC340"], "CSC340")
    #feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
    #                       ["tu", "sfsu_u"],
    #                       ["CSC210", "CSC220", "CSC256", "CSC230", "MATH324", "MATH325", "CSC340"], "CSC340")


    feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
                           ["tu", "sfsu_u"],
                           ["CSC210", "CSC220", "CSC256", "CSC230", "MATH324", "MATH325", "CSC340", "CSC413", "CSC415", "CSC510", "CSC520", "CSC600"], "CSC600",
                           groupings=['admin_descript', 'ethnicity'],
                           isolation=['admin_descript', "1"])

    feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
                           ["tu", "sfsu_u"],
                           ["MATH324", "MATH325", "CSC340", "CSC413", "CSC415", "CSC510", "CSC520", "CSC600"], "CSC600",
                           groupings=['admin_descript', 'ethnicity'],
                           isolation=['admin_descript', "2"])

    #feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
    #                       ["tu", "sfsu_u"],
    #                       ["CSC210", "CSC220", "CSC256", "CSC230", "MATH324", "CSC340"], "CSC340",
    #                       groupings=['admin_descript'],
    #                       isolation=['admin_descript', "1"])
    #feature_analysis_tests(students, ['sex', 'ethnicity', 'resident_status', 'prep_summary'],
    #                       ["tu", "sfsu_u"],
    #                       ["CSC220", "CSC256", "CSC230", "MATH324", "MATH325", "CSC340"], "CSC340",
    #                       groupings=['admin_descript'],
    #                       isolation=['admin_descript', "2"])


def run_trip_classes(students, **kwargs):
    suffix = "allall_trip_classes.csv"
    if 'groupings' in kwargs:
        groups = ga.get_grouping_types(kwargs['groupings'])
        for group_set in groups:
            print(group_set)
            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students)
            datas = ca.find_trip_classes(filtered_students)
            suffix = ga.translate_header(kwargs['groupings'], group_set)
            utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/trip_classes_"+suffix + ".csv", datas[0])
            utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/trip_semesters_"+suffix + ".csv", datas[1])
    else:
        datas = ca.find_trip_classes(students)
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/trip_classes_" + suffix, datas[0])
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/trip_semesters_" + suffix, datas[1])


def init_trip_classes():
    students = it.package_student_data()
    run_trip_classes(students)
    run_trip_classes(students, groupings=['ethnicity'])
    run_trip_classes(students, groupings=['admin_descript', 'ethnicity'])
    #run_trip_classes(students, groupings=['type_descript'])
    #run_trip_classes(students, groupings=['admin_descript', 'sex'])
    #run_trip_classes(students, groupings=['admin_descript', 'prep_assess_summary'])

def graduate_random_forest_extract():
    students = it.package_student_data()
    filtered_students = ga.filter_students(["status"], ["dropout"], students)
    filtered_students.extend(ga.filter_students(["status"], ["graduated"], students))

    df = ca.create_custom_dataframe(filtered_students,["status"], [], ["CSC210", "CSC220", "CSC256", "CSC230",
                 "MATH227", "MATH324", "MATH325", "CSC340", "CSC413", "CSC415", "CSC510", "CSC520", "CSC600"])
    results = ca.generic_impact_rf_feature_extract(df, "status")
    utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/rf_grad_test.csv", results)

#graduate_random_forest_extract()

def series_analysis():
    students = it.package_student_data()
    students = sa.compare_series(students, "cs_only_seq", "sfsu_seq_check", True)
    df = ot.students_to_pandas(students, sequence_score=True)
    ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_comp_fresh_cs_seq_only_final_12_11.csv")

#series_analysis()

def histo_analysis():
    students = it.package_student_data()
    filtered_students = ga.filter_students(["admin_descript"], ["Transfer_Start"], students) # this wont work now, need to change to godes
    datas = sa.course_semester_histogram(filtered_students, True)
    utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/xfer_class_histo.csv", datas)

#students = it.package_student_data()
#df = ot.students_to_pandas(students)
#ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/student_data_012020.csv")

#histo_analysis()
print("combo_runs")
#combo_run_start_1()
#combo_run_start_2()
print("trip")
#init_trip_classes()
print("feature")
#init_features_tests()


#sfsu_class_dict = ds.build_class_key_vector(students_temp)
#ca.correlation_analysis(students_temp, ["CSC210", "CSC211", "CSC220", "CSC256", "CSC340"], "corr_test_fails")
print("impact")
#init_impact_set()
print("sequence")
#init_sequence_set()

#students = it.package_student_data()
#df = ot.students_to_pandas(students)
#ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/complete_student_data_3_2_20.csv")



"""
ds.build_student_vector_test(students_temp, sfsu_class_dict, 3)
#ds.build_student_vector_cs_only(students_temp, sfsu_class_dict, 4)
#datas = ds.build_named_fp(students_temp, ["CSC210", "CSC220", "CSC256", "CSC230"])
cluster_dict = dp.cluster_run(students_temp, 3)[1]

#cluster_dict = ca.cluster_named(datas[0], datas[1], 2)
for clust in cluster_dict:
    students = cluster_dict[clust]

    print("Clust :"+str(clust)+" ***************")
    print(str(len(students)) + " cluster size")
    #ca.correlation_analysis(students, ["CSC210", "CSC211", "CSC340", "CSC413", "CSC415", "CSC648"], "corr_test_211_2_sem"+str(clust))
    compare_data = ca.grade_compare_positive_query("CSC648", "CSC412", ">",
                                cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)
    compare_data = ca.grade_compare_positive_query("CSC413", "CSC412", ">",
                                cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)
    compare_data = ca.class_type_grade_compare("CSC340", "bonus", ">",
                                cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)
    compare_data = ca.class_type_grade_compare("CSC648", "bonus", ">",
                                cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
    ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students)
    print("**********************")
    


compare_data = ca.grade_compare_positive_query("CSC340", "CSC211", ">",
                            cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students_temp)
compare_data = ca.grade_compare_positive_query("CSC413", "CSC412", ">",
                            cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students_temp)
compare_data = ca.grade_compare_positive_query("CSC415", "CSC412", ">",
                            cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students_temp)
compare_data = ca.class_type_grade_compare("CSC340", "bonus", ">",
                            cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students_temp)
compare_data = ca.class_type_grade_compare("CSC648", "bonus", ">",
                            cnx = utils.get_connetion(user="advisor", password="passadvise", host="localhost", database="SFSU_STUDENT_HISTORY"))
ca.calc_pval_tval(compare_data[0], compare_data[1], filter=students_temp)
"""

#sfsu_do_run()

#print(sfsu_class_impact_run())
#class_pred_run(2,"364310")
#class_pred_run(2,"364308")
#class_pred_run(2,"364296")
#class_pred_run(2,"364302")
#class_pred_run(2,"364307")
#persist_student_data()

#dropout_run()
#class_vects()

#cluster_run(2)
#cluster_run(4)
#sfsu_do_run()
#run_update()

#get_data_frame()
#sfsu_do_run()
#sequence_analysis()
import_student_data()
students = it.package_student_data()
df = ot.students_to_pandas(students)
ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/complete_student_data_3_2_20.csv")