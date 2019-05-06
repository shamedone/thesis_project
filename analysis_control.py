import dataset_analysis as da
import dataset_predictor as dp
import utils

def dropout_run():
    #analyze_series("/Users/thomasolson/Documents/workspace/advising_revamp/journal.pone.0171207.s008.csv")
    students = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/G1077_data.csv", "\n", ",", True)
    g1077_dict = da.build_class_key_vector(students, 4)
    student_dict = da.build_student_dict(students, 2, 4, 5, 1)
    students = utils.dict_to_list(student_dict)
    for student in students:
        student.major = "G1077"
    da.build_student_class_seq(students)
    #da.student_series_analysis(students)
    #da.year_count(students)
    da.label_drop_outs(students)
    #da.find_successful(students)
    da.lable_successfull(students)

    da.build_student_vector(students, g1077_dict)
    pred_sets = dp.split_dataset(students)
    dp.classifiy_dropout(pred_sets[0], pred_sets[1], "grades")

    print("break")
    students = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/G1042_data.csv", "\n", ",", True)
    g1042_dict = da.build_class_key_vector(students, 4)
    student_dict = da.build_student_dict(students, 2, 4, 5, 1)
    students = utils.dict_to_list(student_dict)
    for student in students:
        student.major = "G1042"
    #da.year_count(students)
    da.build_student_class_seq(students)
    #da.student_series_analysis(students)


    da.label_drop_outs(students)
    #da.find_successful(students)
    da.lable_successfull(students)
    da.build_student_vector(students, g1042_dict)
    pred_sets = dp.split_dataset(students)
    dp.classifiy_dropout(pred_sets[0], pred_sets[1], "grades")

    #da.analyze_drop_outs(students, outpath="/Users/thomasolson/Documents/workspace/advising_revamp/dropout_G1077_data.csv")
    #students = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/G1042_data.csv", "\n", ",", True)
    #da.analyze_drop_outs(students, outpath="/Users/thomasolson/Documents/workspace/advising_revamp/dropout_G1042_data.csv")

def class_pred_run(grade_seq, pred_class):
    students = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/G1077_data.csv", "\n", ",",
                                    True)
    g1077_dict = da.build_class_key_vector(students, 4)
    student_dict = da.build_student_dict(students, 2, 4, 5, 1)
    students = utils.dict_to_list(student_dict)
    for student in students:
        student.major = "G1077"
    da.build_student_class_seq(students)
    #da.student_series_analysis(students)
    # da.year_count(students)
    da.label_drop_outs(students)
    #da.lable_successfull(students)

    pred_sets = dp.split_dataset(students)
    pred_class_dict = da.get_course_pred_vect_key_dict(pred_sets[0], pred_sets[1], grade_seq, pred_class)
    da.build_student_vector(pred_sets[0], pred_class_dict)
    da.build_student_vector(pred_sets[1], pred_class_dict)
    dp.pred_student_grade(pred_sets[0], pred_sets[1], pred_class, grade_seq, "grades")



def class_vects():
    da.print_class_dict("/Users/thomasolson/Documents/workspace/advising_revamp/G1077_data.csv",
                        outpath="/Users/thomasolson/Documents/workspace/advising_revamp/class_ints_G1077_data.csv" )
    da.print_class_dict("/Users/thomasolson/Documents/workspace/advising_revamp/G1042_data.csv",
                        outpath="/Users/thomasolson/Documents/workspace/advising_revamp/class_ints_G1042_data.csv" )


#class_pred_run(2,"364310")
#class_pred_run(2,"364308")
class_pred_run(2,"364296")
#class_pred_run(2,"364302")
#class_pred_run(2,"364307")

#dropout_run()
#class_vects()