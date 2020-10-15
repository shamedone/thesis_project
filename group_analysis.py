import utils
import import_tools
import output_tools as ot
from itertools import product

#rturns all possible types of students found in database for each grouping type, i.e for stading: freshman, sophmore, etc.
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
        elif grouping == "dropout_sem":
            sql = "select distinct(dropout_semester) from student_data"
        elif grouping == "first_sem":
            sql = "select distinct(first_semester) from student_data"
        elif grouping == "entry_major":
            sql = "select distinct(entry_major) from student_data"
        elif grouping == "final_major":
            sql = "select distinct(final_major) from student_data"
        elif grouping == "entry_standing":
            sql = "select distinct(entry_standing) from student_data"
        elif grouping == "status":
            sql = "select distinct(status) from student_data"
        elif grouping == "global_status":
            sql = "select distinct(global_status) from student_data"
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


#filters students based on list obejects [[categoryA, categoryB], [criteraA, critieraB]]
#students removed if they dont match each criteria to each category
def filter_students(categories, criterias, students, kwargs):

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
            elif category == "dropout_sem" and student.dropout_semester != criteria:
                skip_list.add(student.id_num)
            elif category == "first_semester" and student.first_sem != criteria:
                skip_list.add(student.id_num)
            elif category == "serious" and student.serious != criteria:
                skip_list.add(student.id_num)
            elif category == "entry_standing" and student.entry_standing != criteria:
                skip_list.add(student.id_num)
            elif category == "global_status" and student.global_status != criteria:
                skip_list.add(student.id_num)
            elif category == "serious_student" and student.serious != criteria:
                skip_list.add(student.id_num)
    output = []
    for student in students:
        if student.id_num not in skip_list:
            output.append(student)

    return output

#filters coureses by performance, parameters given by list object [course, [set of needed grades]
def filter_by_course_performance(performance_list, students):
    skip_list = []

    for performance_set in performance_list:
        crs_match = performance_set[0]
        criteria = performance_set[1]
        for student in students:
            if crs_match not in student.unique_courses:
                skip_list.append(student.id_num)
                continue
            for crs in student.course_history:
                if crs.name == crs_match and crs.repeat == 0:
                    if crs.grade_str not in criteria:
                        skip_list.append(student.id_num)

    output = []
    for student in students:
        if student.id_num not in skip_list:
            output.append(student)

    return output

#translates integers in columns to strings
def translate_header(categories, criterias):
    suffix = ""
    for x in range(0, len(categories)):
        category = categories[x]
        criteria = criterias[x]

        if category in ["sex", "resident_status", "ethnicity", "admin_descript", "entry_standing", "serious", "prep_assess_summary"]:
            suffix += "_" + ot.decoder[category][int(criteria)]
        else:
            suffix += "_" + criteria
    return suffix