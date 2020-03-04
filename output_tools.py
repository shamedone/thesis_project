import utils
import numpy as np
import pandas as pd


def students_to_pandas(students, **kwargs):
    all_data = []
    for student in students:
        base_data = [student.id_num, decoder["sex"][int(student.sex)], decoder["ethnicity"][int(student.ethnic)],
                     decoder["resident_status"][int(student.resident_status)], decoder["admin_descript"][int(student.admin_descript)],
                     student.status, student.prep_assess, student.prep_assess_summary,
                     student.type_descript, student.type_descript_summary, student.final_gpa, student.final_cs_gpa, student.final_gen_gpa,
                     student.serious, student.first_sem, student.dropout_semester, student.prior_units]

        for course in sorted(student.course_history, key=lambda x: x.semester):
            line_data = []
            line_data.extend(base_data)
            line_data.extend([course.student_age, decoder["student_level"][int(course.student_standing)],
                              course.semester, course.seq_int, course.name,
                              course.equiv_name, course.course_type, course.grade_str, int(course.grade),
                              course.term_units, course.term_gpa, course.sfsu_units, course.sfsu_gpa, course.grad_flag,
                              course.spring_19_flag, course.ge_load, course.tech_load, course.repeat, course.college,
                              course.department])
            if 'student_prediction' in kwargs:
                line_data.extend([student.pred, student.pred_class])
            if 'course_prediction' in kwargs:
                line_data.extend([course.pred, course.pred_class])
            if 'sequence_score' in kwargs:
                line_data.extend([student.seq_sim_score])
            all_data.append(line_data)
    columns = ['student_id', "sex", "ethnic_desc", "resident_stat", "admin_desc", "student_status",
               "student_prep_assess", "prep_assess_summary", "type_descript", "type_descript_summary", "final_gpa",
               "final_cs_gpa", "final_gen_gpa", "serious_student", "first_semester", "dropout_semester", "prior_units", "student_age",
               "student_standing","semester", "class_seq", "course", "course_equiv","course_type", "grade_str",
               "grade_int", "term_units", "term_gpa", "sfsu_units", "sfsu_gpa", "graduated", "spring_19", "ge_load",
               "tech_load", "repeat", "college", "department"]
    if 'student_prediction' in kwargs:
        columns.extend([kwargs['student_prediction'] + "_predict", kwargs['student_prediction'] + "_pred_class"])
    if 'course_prediction' in kwargs:
        columns.extend([kwargs['course_prediction'] + "_predict", kwargs['course_prediction'] + "_pred_class"])
    if 'sequence_score' in kwargs:
        columns.extend(["sequence_sim_score"])
    df = pd.DataFrame(np.array(all_data), columns=columns)
    df['grade_int'] = df['grade_int'].astype(int)
    df['term_units'] = df['term_units'].astype(float)
    df['term_gpa'] = df['term_gpa'].astype(float)
    df['sfsu_units'] = df['sfsu_units'].astype(float)
    df['sfsu_gpa'] = df['sfsu_gpa'].astype(float)
    df['class_seq'] = df['class_seq'].astype(int)
    df['student_age'] = df['student_age'].astype(int)
    df['ge_load'] = df['ge_load'].astype(int)
    df['tech_load'] = df['term_gpa'].astype(int)
    df['repeat'] = df['repeat'].astype(int)
    df['prior_units'] = df['prior_units'].astype(int)
    df['final_gen_gpa'] = df['final_gen_gpa'].astype(float)

    return df

def pandas_to_csv(df, outpath):
    df.to_csv(outpath)

def dictionary_output_to_list(dictionary, output_type):
    output = []
    if output_type == "count":  # count types refer to results where we are getting numbers as reusults : sex
        output.append(["category", "value"])
        for cat in dictionary:
            output.append([cat, dictionary[cat]])
        # utils.list_to_file(outpath+filename + ".csv", output)
    if output_type == "list":  # list output is when we are getting returned a sub dictonary
        stats_output = []
        for cat in dictionary:
            sub_dict = dictionary[cat]
            output.append([cat+"_stats", "value"])
            try:
                for sub_cat in sub_dict:
                    output.append([sub_cat, sub_dict[sub_cat]])
            except TypeError:
                stats_output.append([cat, sub_dict])
            if len(stats_output) != 0:
                output.extend(stats_output)

    return output


decoder = {
    "prep_assess": {#
        0:"OK",
        1:"UN_MATH",
        2:"UN_PHYS",
        3:"UN_PHYS;UN_MATH",
    },
    "prep_assess_summary": {#
        0:"OK_PREP",
        1:"UNPREPARED",
    },
    "sex":{#
        0: "male",
        1: "female"
    },
    "resident_status": {#
        1:"Bay Area (6 counties)",
        2:"San Diego",
        3:"Southern California",
        4:"Northern California",
        5:"Central California",
        6:"U.S. outside of CA",
        7:"International"
    },

    "ethnicity": {#
            1:"AmInd",
            2:"Black",
            3:"Asian",
            5:"PacIsl",
            6:"Hisp",
            7:"White",
            8:"Intl",
            4:"TwoMore",
            9:"Unknown"
    },
    "admin_descript": {#
        1: "Freshman_Start",
        2: "Transfer_Start",
        3: "Transitory_Start",
    },
    "student_level" : {
        1: "Freshman",
        2: "Sophomore",
        3: "Junior",
        4: "Senior",
    },
    "serious" : {
        0: "Not_Serious",
        1: "Serious"
    }

}