import utils
import import_tools
import output_tools as ot
from itertools import product



def get_demographic_makeup(filtered_students):
    demo_data = {
        "sex": {},
        "ethnicity": {},
        "resident_status": {},
        "admin_descript": {},
        "prep_assess": {}
    }
    for item in ot.decoder['sex']:
        utils.sum_to_dict(ot.decoder['sex'][item],0, demo_data["sex"])
    for item in ot.decoder['ethnicity']:
        utils.sum_to_dict(ot.decoder['ethnicity'][item],0, demo_data["ethnicity"])
    for item in ot.decoder['resident_status']:
        utils.sum_to_dict(ot.decoder['resident_status'][item],0, demo_data["resident_status"])
    for item in ot.decoder['admin_descript']:
        utils.sum_to_dict(ot.decoder['admin_descript'][item],0, demo_data["admin_descript"])
    for item in ot.decoder['prep_assess']:
        utils.sum_to_dict(ot.decoder['prep_assess'][item],0, demo_data["prep_assess"])

    for student in filtered_students:
        sex = ot.decoder["sex"][int(student.sex)]
        ethn = ot.decoder["ethnicity"][int(student.ethnic)]
        res = ot.decoder["resident_status"][int(student.resident_status)]
        admin = ot.decoder["admin_descript"][int(student.admin_descript)]
        prep = student.prep_assess
        utils.sum_to_dict(sex, 1, demo_data["sex"])
        utils.sum_to_dict(ethn, 1, demo_data["ethnicity"])
        utils.sum_to_dict(res, 1, demo_data["resident_status"])
        utils.sum_to_dict(admin, 1, demo_data["admin_descript"])
        utils.sum_to_dict(prep, 1, demo_data["prep_assess"])
    combo_data = []

    for x in range(0,10):
        try:
            combo_data.append(demo_data["sex"][ot.decoder["sex"][x]])
        except KeyError:
            continue
    for x in range(0,10):
        try:
            combo_data.append(demo_data["ethnicity"][ot.decoder["ethnicity"][x]])
        except KeyError:
            continue
    for x in range(0,10):
        try:
            combo_data.append(demo_data["resident_status"][ot.decoder["resident_status"][x]])
        except KeyError:
            continue
    for x in range(0,10):
        try:
            combo_data.append(demo_data["admin_descript"][ot.decoder["admin_descript"][x]])
        except KeyError:
            continue
    for x in range(0,10):
        try:
            combo_data.append(demo_data["prep_assess"][ot.decoder["prep_assess"][x]])
        except KeyError:
            continue

    return demo_data, combo_data  # list type return


def get_grade_stats(filtered_students):
    gpas = []
    cs_gpas = []
    enroll_lengths = []
    max_ages = []
    grades_data = {
        "max_student_age": {},
        "mean_max_student_age": 0,
        "enrollment_len": {},
        "mean_enroll_len": 0,
        "final_course": {},
        "mean_gpa": 0,
        "mean_cs_gpa": 0,
        "cs_gpas": {},
        "gpas": {}
    }
    for student in filtered_students:
        gpas.append(student.final_gpa)
        cs_gpas.append(student.final_cs_gpa)
        max_enroll = max(student.sem_seq_dict.keys())
        enroll_lengths.append(max_enroll)
        max_age = int(student.course_seq_dict[max_enroll][0].student_age)
        max_ages.append(max_age)
        utils.sum_to_dict(utils.group_gpa(student.final_gpa), 1, grades_data["gpas"])
        utils.sum_to_dict(utils.group_gpa(student.final_cs_gpa), 1, grades_data["cs_gpas"])
        utils.sum_to_dict(max_age, 1, grades_data["max_student_age"])
        utils.sum_to_dict(max_enroll, 1, grades_data["enrollment_len"])

    grades_data["mean_gpa"] = sum(gpas) / len(gpas)
    grades_data["mean_cs_gpa"] = sum(cs_gpas) / len(cs_gpas)
    grades_data["mean_enrollment_length"] = sum(enroll_lengths) / len(enroll_lengths)
    grades_data["mean_max_student_age"] = sum(max_ages) / len(max_ages)
    combo_data = [grades_data["mean_gpa"], grades_data["mean_cs_gpa"], grades_data["mean_enrollment_length"], grades_data["mean_max_student_age"]]
    return grades_data, combo_data  # list type return


def dropout_analysis(students):
    dropout_cat = {
        "drop_out_count": 0,
        "grad_count": 0,
        "total_students": 0,
        "dropout_w_u_math": 0,
        "dropout_w_u_phys": 0,
        "dropout_w_u_mathphys": 0,
        "grad_w_u_math": 0,
        "grad_w_u_phys": 0,
        "grad_w_u_mathphys": 0,
        "in_progress_count": 0
    }

    for student in students:
        utils.sum_to_dict("total_students", 1, dropout_cat)
        if "dropout" in student.status:
            utils.sum_to_dict("drop_out_count", 1, dropout_cat)
            raw_reason = student.type_descript
            utils.sum_to_dict(raw_reason, 1, dropout_cat)
            split_reason = raw_reason.split(";")
            for reason in split_reason:
                utils.sum_to_dict(reason, 1, dropout_cat)
            if student.prep_assess != "OK":
                if "MATH" in student.prep_assess:
                    utils.sum_to_dict("dropout_w_u_math", 1, dropout_cat)
                if "PHYS" in student.prep_assess:
                    utils.sum_to_dict("dropout_w_u_phys", 1, dropout_cat)
                if "MATH" in student.prep_assess and "PHYS" in student.prep_assess:
                    utils.sum_to_dict("dropout_w_u_mathphys", 1, dropout_cat)

        elif "graduated" in student.status:
                utils.sum_to_dict("grad_count", 1, dropout_cat)
                if student.prep_assess != "OK":
                    if "MATH" in student.prep_assess:
                        utils.sum_to_dict("grad_w_u_math", 1, dropout_cat)
                    if "PHYS" in student.prep_assess:
                        utils.sum_to_dict("grad_w_u_phys", 1, dropout_cat)
                    if "MATH" in student.prep_assess and "PHYS" in student.prep_assess:
                        utils.sum_to_dict("grad_w_u_mathphys", 1, dropout_cat)
        else:
            utils.sum_to_dict("in_progress_count", 1, dropout_cat)

    combo_data = [dropout_cat["total_students"], dropout_cat["grad_count"], dropout_cat["drop_out_count"],
                  dropout_cat["dropout_w_u_math"],  dropout_cat["dropout_w_u_phys"],  dropout_cat["dropout_w_u_mathphys"],
                  dropout_cat["grad_w_u_math"],  dropout_cat["grad_w_u_phys"], dropout_cat["grad_w_u_mathphys"],
                  dropout_cat["in_progress_count"]]


    return dropout_cat, combo_data



def gather_group_stats(group_name):
    students = import_tools.package_student_data()
    filtered_students = []
    for student in students:
        if group_name in student.type_descript:
            filtered_students.append(student)
    grade_stats = get_grade_stats(filtered_students)
    count = len(filtered_students)
    demographics = get_demographic_makeup(filtered_students)

    return grade_stats, count, demographics


def get_grouping_types(groupings):
    cnx = utils.get_connection()
    cursor = cnx.cursor(buffered=True)
    combos = []
    for grouping in groupings:
        if grouping == "admin_descript":
            sql = "select distinct(admin_descript) from student_data"
        elif grouping == "resident_status":
            sql = "select distinct(resident_status) from student_data"
        elif grouping == "ethnicity":
            sql = "select distinct(ethnicity) from student_data"
        elif grouping == "type_descript":
            sql = "select distinct(type_descript) from student_data"
        elif grouping == "type_descript_summary":
            sql = "select distinct(type_descript_summary) from student_data"
        elif grouping == "sex":
            sql = "select distinct(sex) from student_data"
        elif grouping == "prep_assess":
            sql = "select distinct(prep_assess) from student_data"
        elif grouping == "prep_assess_summary":
            sql = "select distinct(prep_assess_summary) from student_data"
        elif grouping == "serious":
            sql = "select distinct(serious_student) from student_data"
        else:
            print("invalid type")
            print(grouping)
            raise TypeError

        cursor.execute(sql)
        results = cursor.fetchall()
        temp = []
        for result in results:
            temp.append(result[0])
        combos.append(temp)
    cursor.close()
    cnx.close()


    return list(product(*combos))

def filter_students(categories, criterias, students, **kwargs):
    #  TODO build tool to filter students based on demographics,

    skip_list = set()
    isolation = False # Isolaiton variable gives funciton ability to isoloate out a single group, ie. freshman, transfer etc.
    if 'isolation' in kwargs:
        isolation = kwargs['isolation']

    for x in range(0, len(categories)):
        category = categories[x]
        criteria = criterias[x]

        if isolation and category == isolation[0] and criteria != isolation[1]:
            return []
        for student in students:
            if category == "sex" and student.sex != criteria:
                skip_list.add(student.id_num)
            elif category == "ethnicity" and student.ethnic != criteria:
                skip_list.add(student.id_num)
            elif category == "resident_status" and student.resident_status != criteria:
                skip_list.add(student.id_num)
            elif category == "admin_descript" and student.admin_descript != criteria:
                skip_list.add(student.id_num)
            elif category == "status" and student.status != criteria:
                skip_list.add(student.id_num)
            elif category == "type_descript" and student.type_descript != criteria:
                skip_list.add(student.id_num)
            elif category == "type_descript_summary" and student.type_descript_summary != criteria:
                skip_list.add(student.id_num)
            elif category == "prep_assess" and student.prep_assess != criteria:
                skip_list.add(student.id_num)
            elif category == "prep_assess_summary" and student.prep_assess_summary != criteria:
                skip_list.add(student.id_num)
            elif category == "serious" and student.serious != criteria:
                skip_list.add(student.id_num)
    output = []
    for student in students:
        if student.id_num not in skip_list:
            output.append(student)

    return output


def translate_header(categories, criterias):
    suffix = ""
    for x in range(0, len(categories)):
        category = categories[x]
        criteria = criterias[x]
        if category in ["sex", "resident_status", "ethnicity", "admin_descript", "student_level", "prep_assess_summary", "serious"]:
            suffix += "_" + ot.decoder[category][int(criteria)]
        else:
            suffix += "_" + criteria
    return suffix