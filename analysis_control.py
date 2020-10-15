import dataset_stage as ds
import dataset_predictor as dp
import curriculum_analysis as ca
import import_tools as it
import output_tools as ot
import series_analysis as sa
import group_analysis as ga
import utils

#imports raw data from file
def import_students_dict():
    students_raw = utils.list_from_file(
        "/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_data_v2.csv", "\n", ",", True)
    student_dict = it.build_student_dict(students_raw, student_id=0, sex=4, ethnic=5, age=6, resident_status=7,
                                         standing=8, entry_major=13, final_major=33, spring_19_major=37,
                                         admin_descript=9, crs_abbr=15, crs_num=16, grade_str=21, year_int=3, term_gpa=22,
                                         sfsu_gpa=23, term_units=25, sfsu_units=26, grad_flag=31, spring_19_flag=35,
                                         crs_college_long=19, crs_dept_long=20, total_units=27)
    return student_dict

#command to import students from raw file.
def import_student_data():
    student_dict = import_students_dict()
    students = utils.dict_to_list(student_dict)
    ds.build_student_class_seq(students)
    ds.calc_sem_avg_grade(students)
    ds.calc_semester_load(students)
    ds.label_drop_outs_sfsu(students) #must do prior to update final
    ds.update_final_sem(students)
    ds.update_gpas(students)
    ds.flag_serious(students)
    ds.label_student_prepardness(students)
    it.combine_phys(students)
    ds.update_load_list(students)
    it.persist_student_data(students)
    return 0
    #init_students(students)

#sequence mining function
def sequence_analysis(students, filter_type, support):
    output = [["count", "seq_length", "sequence"]]
    datas = sa.run_sequence_mining(students, support, filter_type)
    for data in datas:
        if len(data[1][0]) < 3:
            continue
        output.append([data[0], str(len(data[1][0])),";".join(data[1][0])])
    return output

#sequence mining function wrapper
def iterative_sequence_tests(students, filter,  **kwargs):
    suffix = ".csv"
    if filter:
        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students, kwargs)
            suffix = ga.translate_header(kwargs['groupings'], group_set)
            datas = sequence_analysis(filtered_students, kwargs['class_filter'], kwargs['support'])
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/test_series_stats" + suffix+".csv",
                datas)
    else:
         datas = sequence_analysis(students, kwargs['class_filter'], kwargs['support'])
         utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/series_stats" + suffix,
            datas)

#iterative impacts test setup
def iterative_impact_tests(students, filter, compare_type, compare_dict, score_type, **kwargs):
    suffix = ".csv"
    if filter:  #if the fitler flag is true, then in splits students up in groupings, if not, it just runs them as is.
        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            print("init")
            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students, **kwargs)
            datas = run_impact_tests(filtered_students, compare_type, compare_dict, score_type)

            suffix = ga.translate_header(kwargs['groupings'], group_set)

            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/3_18" + compare_type +
                "_prereq_impact_stats" + suffix + "_score_" + score_type + ".csv", datas[0])
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/3_18" + compare_type +
                "_elect_impact_stats" + suffix + "_score_" + score_type + ".csv", datas[1])
    else:
        datas = run_impact_tests(students, compare_type, compare_dict, score_type)
        if len(datas) == 1:
            return
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/3_18" + compare_type +
            "_prereq_impact_stats" + suffix, datas[0])
        utils.list_to_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/3_18" + compare_type +
            "_all_impact_stats" + suffix, datas[1])

#impact analysis wrapper
def run_impact_tests(students, comp_type, comp_dict, score_type):
    #results_preq = ca.iterative_impact_prereq(students)

    #results_preq = ca.iterative_impact_comp("prereqs", students, comp_type, comp_dict, score_type) #I dont use this one any more, just easier to run allall
    results_elect = ca.iterative_impact_comp("allall_cs", students, comp_type, comp_dict, score_type)
    if len(results_elect) == 1:
        results_elect = []

    return [], results_elect
    #return ["hi", results_elect]


def feature_analysis_tests(students, socio_factors, course_factors, courses, target_course, time_isolation, **kwargs):
    isolation_set = False
    if 'groupings' in kwargs:

        group_types = ga.get_grouping_types(kwargs['groupings'])
        for group_set in group_types:
            if 'isolation' in kwargs:
                isolation_set = kwargs['isolation']

            filtered_students = ga.filter_students(kwargs['groupings'], group_set, students, kwargs)
            if len(filtered_students) == 0:
                continue

            suffix = ga.translate_header(kwargs['groupings'], group_set)
            df = ca.create_corr_dataframe(filtered_students, [], course_factors,  #socio factors are disabled for lr
                                          courses)
            datas = ca.LinearRegression(df, target_course+"_grade")
            utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/linear_reg_extraction_"
                               + suffix +"_"+target_course +".csv", datas)
            df = ca.create_corr_dataframe(filtered_students, socio_factors, course_factors,
                                          courses)
            datas = ca.generic_impact_rf_feature_extract(df, target_course+"_grade")
            utils.list_to_file(
                "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/random_forest_extraction_"
                + suffix +target_course+".csv", datas)
            ca.correlation_analysis(df, "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/corr_grid_"
                                    + suffix +"_"+target_course)
    else:
        df = ca.create_corr_dataframe(students, course_factors,
                                      courses, time_isolation, target_course
                                      )
        #datas = ca.LinearRegression(df, target_course+"_grade")
        #utils.list_to_file(
        #    "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/linear_reg_extraction_allall"+target_course+".csv", datas)
        #df = ca.create_corr_dataframe(students, socio_factors, course_factors,
        #                                courses,
        #                                )
        #datas = ca.generic_impact_rf_feature_extract(df, target_course+"_grade")
        #utils.list_to_file(
        #    "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/random_forest_extraction_allall"+target_course+".csv", datas)
        if time_isolation:
            target_course += "_isolated"
        ca.correlation_analysis(df,
                                "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/concurrent_7_29_corr_grid_allall_"+target_course)


def init_impact_set(students):
    print("impact_start")
    compare_dict = ca.build_grade_comp("sequence")
    #iterative_impact_tests(students, False, "sequence", compare_dict,"OOO")
    #iterative_impact_tests(students, True, "sequence", compare_dict, "OOO", groupings=['admin_descript', 'entry_standing', 'global_status'], isolation=["global_status", "cs"])
    #iterative_impact_tests(students, True, "sequence", compare_dict, "NT", groupings=['prep_assess_summary'])
    iterative_impact_tests(students, True, "sequence", compare_dict, "OOO", groupings=['prep_assess_summary'])
    iterative_impact_tests(students, True, "sequence", compare_dict, "OOO", groupings=['prep_assess_summary', 'entry_standing'])

    #iterative_impact_tests(students, True, "sequence", compare_dict, groupings=['admin_descript', 'sex'])

    compare_dict = ca.build_grade_comp("equiv")
    #iterative_impact_tests(students, False, "equiv", compare_dict, "all")
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['global_status'],
    #                       isolation=['global_status', "cs_4_9"])
    iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['prep_assess_summary'])
    iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['prep_assess_summary', 'entry_standing'])
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['global_status', "admin_descript"], isolation=['global_status', "cs_4_9"])
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['global_status', "admin_descript", "entry_standing"])
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=["admin_descript", "entry_standing"])
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=["admin_descript", "entry_standing", "status"])
    #iterative_impact_tests(students, True, "equiv", compare_dict, "all", groupings=['admin_descript','global_status', "status"], isolation=['global_status', "CS_12_SET"])


    print('impact_end')

def init_sequence_set(students):
    print("seq_start")
    #iterative_sequence_tests(students, True, groupings=['resident_status'], class_filter="all", support=30)
    iterative_sequence_tests(students, True, groupings=['admin_descript', 'entry_standing'], class_filter="all", support=30)
    iterative_sequence_tests(students, True, groupings=['admin_descript', 'entry_standing', 'global_status'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['ethnicity'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex','admin_descript'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['type_descript_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['prep_assess_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex', 'admin_descript', 'type_descript_summary'], class_filter="all", support=30)
    #iterative_sequence_tests(students, True, groupings=['sex', 'resident_status', 'type_descript_summary', 'prep_assess_summary'], class_filter="all", support=30)
    print("seq_end")


def init_features_tests(students):
    print("feat start")


    feature_analysis_tests(students, [],
                            [],
                            ["MATH226", "MATH227", "MATH324", "MATH325", "PHYS220", "PHYS222", "PHYS230", "PHYS232",
                            "CSC210", "CSC220", "CSC230","CSC256", "CSC340", "CSC300", "CSC413", "CSC415", "CSC510",
                            "CSC600", "CSC648"], "CSC210", True)


    #feature_analysis_tests(students, [],
    #                        [],
    #                        ["MATH226", "MATH227", "MATH324", "MATH325", "PHYS220", "PHYS222", "PHYS230", "PHYS232",
    #                        "CSC210", "CSC220", "CSC230","CSC256", "CSC340", "CSC300", "CSC413", "CSC415", "CSC510",
    #                        "CSC600", "CSC648"], "allall", False)


    print("feat_end)")


def series_analysis():
    students = it.package_student_data()

    #students = sa.compare_series(students, "cs_only_seq", "sfsu_seq_check", True, False)
    #df = ot.students_to_pandas(students, sequence_score=True)
    #ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/7_25_counter_sfsu_comp_fresh_cs_seq_only_hard_combo.csv")

    students = sa.compare_series(students, "cs_only_seq", "freshman_8", True, True)
    df = ot.students_to_pandas(students, sequence_score=True)
    ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/7_25_counter_top1_sfsu_score_recheck_fresh_cs_seq_only_hard_combo.csv")


    # test = sa.find_possible_semester_sequence(["0_CSC210", "0_MATH226", "0_MATH227", "0_PHYS220", "0_PHYS230", "0_CSC220", "0_CSC230"], 1)
    # datas = find_all_sequences(test, 1)
    # print(datas)
    # utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_xfer_8.csv", datas)

    # test = find_possible_semester_sequence([], 1)
    # datas = find_all_sequences(test, 1)
    # utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/6_19_all_possible_series_8_old_cir.csv", datas)

    # test = find_possible_semester_sequence(["1_MATH226", "1_CSC210", "1_CSC211"], 2)
    # datas = find_all_sequences(test, 2)
    # print(datas)
    # utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_10_math226_csc210_211.csv", datas)

    #sa.score_series_set("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_8_old_cir_only.csv",
    #                "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/6_25_all_possible_series_8_scored_211_412_add_combo_score.csv", True, True, "freshman") # xfer long

    #sa.score_series_set("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/SFSU_Recommended_Seq.csv",
    #                 "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/6_25_SFSU_Recommended_Seq_score_freshman_bonus_thres5_combo.csv", False, False, "freshman")

    #datas = sa.utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/aboveSFSU_6_25_all_possible_series_8_scored_211_412_add_combo_score_412add_211add.csv", '\n', ",", False)
    #output = sa.build_series_historgram(datas, True)
    #utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/aboveSFSU_6_25_all_possible_series_8_scored_211_412_add_combo_score_412add_211add_histo.csv", output)


def histo_analysis():
    students = it.package_student_data()
    filtered_students = ga.filter_students(["admin_descript"], ["Transfer_Start"], students)
    datas = sa.course_semester_histogram(filtered_students, True)
    utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/xfer_class_histo.csv", datas)



def prediction_set_test(students, student_fields, course_fields, course_list, target, outpath, exclusive):
    #student_fields_master_order = ["status", "sex", "ethnicity", "resident_status", "prep_summary", "total_college_count"]
    #crs_fields_master_order = ["tu",  "tech_u", "ge_u", "seq_int", "age", "sfsu_gpa", "term_gpa", "repeat", "crs_bus_units",
    #                           "crs_edu_units", "crs_ethnic_units", "crs_hss_units", "crs_inter_units",
    #                           "crs_lca_units", "crs_cose_units"]
    local_students = []
    for student in students:
        if "progress" in student.status and "status" in target:
            continue
        local_students.append(student)
    

    df = dp.create_predictor_data_frame(local_students, student_fields, course_fields, course_list, target, exclusive)
   # print("rf")
    #outputs = dp.kbase_target(df, target, course_fields)
    #utils.list_to_file(outpath+"_"+target+"_kbest.csv", outputs)
    outputs = dp.classify_tester(df, target, course_fields, 5)

    
    return

def prediction_set(students, student_fields, course_fields, course_list, target, outpath, exclusive):

    local_students = []
    for student in students:
        if "progress" in student.status and "status" in target:
            continue
        local_students.append(student)


    df = dp.create_predictor_data_frame(local_students, student_fields, course_fields, course_list, target, exclusive)
    outputs = dp.classify_target(df, target, course_fields, 5)

    pred_output = outputs[0]
    value_output = outputs[1]
    pred_output[0].extend([" "])
    pred_output[0].extend(student_fields)
    pred_output[1].extend([" "])
    pred_output[1].extend(course_fields)
    pred_output[2].extend([" "])
    pred_output[2].extend(course_list)

    suffix = "_inclusive.csv"
    if exclusive:
        suffix = "_exclusive.csv"
    utils.list_to_file(outpath+"_"+target+suffix, pred_output)
    utils.list_to_file(outpath+"_"+target+"_feat_weight"+suffix, value_output)

    return

def prediction_tester():
    students = it.package_student_data()
    students = it.combine_phys(students)
    #course_fields = ["tu", "seq_int", "age", "term_gpa", "repeat", "crs_bus_units",
    #                          "crs_edu_units", "crs_ethnic_units", "crs_hss_units", "crs_inter_units",
    #                          "crs_lca_units", "crs_cose_units"]

    course_fields = []
    sem2_course_list = ["MATH226", "MATH227", "CSC210"]

    #sem3_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230"]
    sem3_course_list =["MATH226", "MATH227", "PHYS220COMBO", "CSC210", "CSC220", "CSC230"]
    #sem4_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230"]
    sem4_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230"]
    #sem5_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230",
    #                   "MATH324", "MATH325", "CSC256", "CSC340"]

    sem5_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230",
                       "MATH324", "MATH325", "CSC256", "CSC340"]
    sem6_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230",
                       "MATH324", "MATH325", "CSC256", "CSC340", "CSC300", "CSC413", "CSC415", "CSC510"]
    custom_340_list = ["PHYS230", "PHYS232", "CSC220", "CSC230", "CSC256", "CSC340"]

    custom_415_list =["CSC230", "MATH324", "MATH325", "CSC256", "CSC340", "CSC413", "CSC415"]
    custom_600_list =["CSC230", "MATH324", "MATH325", "CSC256", "CSC340", "CSC413", "CSC415", "CSC510", "CSC600"]


    student_field_list = ["status", "sex", "ethnicity", "resident_status", "prep_summary"]

    prediction_set_test(students, student_field_list, course_fields, sem3_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_3sem_grade_only", False)

    print("*************")
    prediction_set_test(students, student_field_list, course_fields, sem3_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_3sem_grade_only", True)

    student_field_list = ["sex", "ethnicity", "resident_status", "prep_summary"]
    print("*************")
    print("*************")

    sem4_course_list.append("CSC340")

    prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem_256add",
                   True)
    print("*************")

    prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem_256add",
                   False)


#prediction analysis wrapper
def prediction_analysis():
    students = it.package_student_data()
    students = it.combine_phys(students)
    #course_fields = ["tu", "seq_int", "age", "term_gpa", "repeat", "crs_bus_units",
    #                          "crs_edu_units", "crs_ethnic_units", "crs_hss_units", "crs_inter_units",
     #                         "crs_lca_units", "crs_cose_units"]

    course_fields = []
    sem2_course_list = ["MATH226", "MATH227", "CSC210"]

    #sem3_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230"]
    sem3_course_list =["MATH226", "MATH227", "PHYS220COMBO", "CSC210", "CSC220", "CSC230"]
    #sem4_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230"]
    sem4_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230"]
    #sem5_course_list =["MATH226", "MATH227", "CSC210", "CSC220", "CSC230",
    #                   "MATH324", "MATH325", "CSC256", "CSC340"]

    sem5_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230",
                       "MATH324", "MATH325", "CSC256", "CSC340"]
    sem6_course_list =["MATH226", "MATH227", "PHYS220COMBO", "PHYS230COMBO", "CSC210", "CSC220", "CSC230",
                       "MATH324", "MATH325", "CSC256", "CSC340", "CSC300", "CSC413", "CSC415", "CSC510"]
    custom_340_list = ["PHYS230", "PHYS232", "CSC220", "CSC230", "CSC256", "CSC340"]

    custom_415_list =["CSC230", "MATH324", "MATH325", "CSC256", "CSC340", "CSC413", "CSC415"]
    custom_600_list =["CSC230", "MATH324", "MATH325", "CSC256", "CSC340", "CSC413", "CSC415", "CSC510", "CSC600"]


    student_field_list = ["status", "sex", "ethnicity", "resident_status", "prep_summary"]

    prediction_set(students, student_field_list, course_fields, sem5_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_5sem_grade_only", False)

    #prediction_set(students, student_field_list, course_fields, sem5_course_list, "status",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_5sem_grade_only", True)

    #prediction_set(students, student_field_list, course_fields, sem2_course_list, "status",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_2sem_grade_only", False)

    prediction_set(students, student_field_list, course_fields, sem2_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_2sem_grade_only", True)

    prediction_set(students, student_field_list, course_fields, sem3_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_3sem_grade_only", False)

    prediction_set(students, student_field_list, course_fields, sem3_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_3sem_grade_only", True)


    prediction_set(students, student_field_list, course_fields, sem4_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_4sem_grade_only", False)

    prediction_set(students, student_field_list, course_fields, sem4_course_list, "status",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_pred_avg_4sem_grade_only", True)


    student_field_list = ["sex", "ethnicity", "resident_status", "prep_summary"]

    sem4_course_list.append("CSC340")
    #prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem", False)

    prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem", True)

    sem4_course_list.append("CSC256")
    #prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem_256add",
    #               False)

    prediction_set(students, student_field_list, course_fields, sem4_course_list, "CSC340_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_4sem_256add",
                   True)

    sem5_course_list.append("CSC413")
    #prediction_set(students, student_field_list, course_fields,  sem5_course_list, "CSC415_grade",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_5sem", False)

    prediction_set(students, student_field_list, course_fields, sem5_course_list, "CSC413_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_5sem", True)

    #prediction_set(students, student_field_list, course_fields, sem6_course_list,  "CSC510_grade",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_6sem", False)

    prediction_set(students, student_field_list, course_fields, sem6_course_list, "CSC510_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_6sem", True)

    sem6_course_list.append("CSC600")
    #prediction_set(students, student_field_list, course_fields, sem6_course_list,  "CSC600_grade",
    #               "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_6sem", False)

    prediction_set(students, student_field_list, course_fields, sem6_course_list,  "CSC600_grade",
                   "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/7_22_multilgrade_simp_pred_avg_6sem", True)

#function allows for isolation of students by grade in course
def isolation_tests(students):
    grade_criteria = [["PHYS230", ["C"]],
                        ["PHYS232", ["C"]]]
    test_students = ga.filter_by_course_performance(grade_criteria, students)
    ot.pandas_to_csv(ot.students_to_pandas(test_students),
                     "/Users/thomasolson/Documents/workspace/advising_revamp/feature_extraction/phys230_test_C_set.csv")


#prediction_tester()

#students = it.package_student_data()


#ca.semester_hist(serious_list)
#ca.total_cs_count(serious_list)

#ds.flag_serious(students)
#isolation_tests(students)
#init_features_tests(students)
#init_sequence_set(students)
#init_trip_classes(students)
#series_analysis()
#fail_data = ga.detailed_dropout_data(students)
#utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/more_fail_data.csv",fail_data)
#df = ot.students_to_pandas(students)
#ot.pandas_to_csv(df, "/Users/thomasolson/Documents/workspace/advising_revamp/complete_student_data_9_9_20.csv")
#init_impact_set(students)

