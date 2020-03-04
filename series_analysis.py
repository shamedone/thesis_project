from efficient_apriori import apriori
from pymining import seqmining
import utils
import import_tools
from operator import itemgetter
from Bio import pairwise2
from Bio.pairwise2 import format_alignment

def build_class_transactions(students):
    transaction_dict = {}
    for student in students:
        sem_history = student.course_seq_dict
        for sem in sem_history:
            semester_list = sem_history[sem]
            data_set = []
            for course in semester_list:
#                if course.course_type == "ge":
#                    data_set.append("ge")
#                else:
                    data_set.append(course.name)
            utils.add_to_dict_list(sem, tuple(data_set), transaction_dict)

    return transaction_dict

def run_apriori(transaction_dict, semester_set, min_support, min_confidence):
    for semester in semester_set:
        itemsets, rules = apriori(transaction_dict[semester], min_support, min_confidence)
        print("SEMESTER "+str(semester))
        print(itemsets)
        print(rules)

def run_sequnce_testing():
    sequences = ("CSC100,CSC200,CSC300,MATH100,MATH200",
                 "CSC100,MATH100,MATH200,CSC200,CSC300",
                 "CSC100,MATH200,CSC300,CSC200,MATH100",
                 "CSC200,MATH100,CSC100,CSC300,MATH200",
                 "MATH100,MATH200,CSC100,CSC300,CSC200",
                 )
    datas = seqmining.freq_seq_enum(sequences, 4)
    for data in datas:
        print(data)

def run_sequence_mining(students, min_support, filter_type):
    sequences = []
    for student in students:
        course_list = []
        semester_keys = list(student.course_seq_dict.keys())
        semester_keys.sort()
        for seq_int in semester_keys:
            student_sem_hist = student.course_seq_dict[seq_int]
            temp_list = []
            for x in student_sem_hist:
                if filter_type == 'generic_ge':
                    if x.type == "ge":
                        temp_list.append("GE")
                elif filter_type == "cs_only":
                    if x.type == "core" or x.type == "bonus":
                        temp_list.append(x.name)
                else:
                    temp_list.append(str(seq_int)+"_"+x.name)
            temp_list.sort()
            course_list.extend(temp_list)
        sequences.append(course_list)
    print("init run")
    datas = seqmining.freq_seq_enum(sequences, min_support)
    output_data = []
    for data in datas:
        output_data.append([data[1], [data[0]]])
    return output_data

def course_semester_histogram(students, core_filter):
    course_histo_data = {}
    output = [["crs","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]]
    for student in students:
        course_hist = student.course_history
        for course in course_hist:
            if core_filter:
                if course.course_type != "core":
                    continue
            if course.name not in course_histo_data:
                course_histo_data[course.name] = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,
                                                  17:0,18:0,19:0,20:0}
            temp_dict = course_histo_data[course.name]
            utils.sum_to_dict(course.seq_int, 1, temp_dict)
            course_histo_data[course.name] = temp_dict
    for crs in course_histo_data:
        histo = course_histo_data[crs]
        output_line = [0] * 21
        output_line[0] = crs
        for seq in histo:
            output_line[seq] = str(histo[seq])
        output.append(output_line)
    return output


def build_seq_sem_dict(seq):
    sem_dict = {}
    for crs in seq:
        sem = int(crs.split("_")[0])
        course = crs.split("_")[1]
        utils.append_to_dict(sem, course, sem_dict)
    return sem_dict


def score_seq(seq_dict, equiv_score_map, seq_score_map):
    score = 0
    for x in range(1, len(seq_dict)+1):
        crs_list = seq_dict[x]
        comp_list = []

        for y in range(x+1, len(seq_dict)+1): #get every class taken
            comps = seq_dict[y]
            for comp in comps:
                comp_list.append(comp)

        for crs_a in crs_list:
            for crs_b in comp_list:
                try:
                    score += float(seq_score_map[crs_a+"_"+crs_b])
                except KeyError:
                    continue

        for i in range(0, len(crs_list)):
            for j in range(i+1, len(crs_list)):
                try:
                    score += float(equiv_score_map[crs_list[i]+"_"+crs_list[j]])
                except KeyError:
                    score += 0
                try:
                    score += float(equiv_score_map[crs_list[j]+"_"+crs_list[i]])
                except KeyError:
                    score += 0
    return score

def update_top_100(value, top_100):
    if len(top_100) < 300:
        top_100.append(value)
        top_100 = sorted(top_100, key=itemgetter(0), reverse=True)
    else:
        if value[0] > top_100[len(top_100)-1][0]:
            top_100.pop()
            top_100.append(value)
            top_100 = sorted(top_100, key=itemgetter(0), reverse=True)
    return top_100

def score_series_set(path, outpath, add_412, add_211):

    seq_score_map = utils.dict_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/sequence_score_map_xfer_30_no_lower_crs.csv",
                                        0,1,"\n", ",", True)
    equiv_score_map = utils.dict_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/equiv_score_map_xfer_30_no_lower_crs.csv",
                                        0,1,"\n", ",", True)
    #seq_score_map = utils.dict_from_file(
    #    "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/sequence_score_map_50.csv",
    #    0, 1, "\n", ",", True)
    #equiv_score_map = utils.dict_from_file(
    #    "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/concurrent_score_map_50.csv",
    #    0, 1, "\n", ",", True)
    i = 0

    top_100 = []
    with open(path, "r") as x:
        data = x.readline()
        while data:
            if i % 10000 == 0:
                print(i)
            i+=1
            #if "10_" in data or "9_" in data:
            #    data = x.readline()
            #    continue
            line = data.strip().replace(" ", "").replace("[","").replace("]","").replace("'","").split(",")

            if add_412 or add_211:
                for sem_x in range(0,len(line)):
                    if "CSC340" in line[sem_x] and add_412:
                        sem = line[sem_x].split("_")[0]
                        line.insert(sem_x+1, sem+"_CSC412")
                        break
                    if "CSC210" in line[sem_x] and add_211:
                        sem = line[sem_x].split("_")[0]
                        line.insert(sem_x+1, sem+"_CSC211")

            score_line = []
            for crs in line:
                if crs.startswith("0"):
                    continue
                score_line.append(crs)

            sem_dict = build_seq_sem_dict(score_line)
            score = score_seq(sem_dict, equiv_score_map, seq_score_map)
            top_100 = update_top_100([score, score_line], top_100)
            data = x.readline()
    print(i)
    if add_412:
        split_path = outpath.split(".")
        prefix = split_path[0]
        split_path[0] = prefix + "_412add"
        outpath = ".".join(split_path)
    if add_211:
        split_path = outpath.split(".")
        prefix = split_path[0]
        split_path[0] = prefix + "_211add"
        outpath = ".".join(split_path)
    utils.list_to_file(outpath, top_100)



def find_possible_courses(course_history):
    possible = []
    core_prqs = import_tools.preq_map
    temp_crs_hist = set()
    for crs in course_history:
        temp_crs_hist.add(crs.split("_")[1])
    for crs in core_prqs:
        if crs in temp_crs_hist:
            continue
        use = True
        prereq = core_prqs[crs]

        for req in prereq:
            if req == '':
                continue
            if req not in temp_crs_hist:
                use = False
        if use:
            possible.append(crs)
    return possible

def find_possible_semester_sequence(course_history, sem_count):
    possible_courses = find_possible_courses(course_history)
    possible_semester = []
    for x in range(0, len(possible_courses)):
        temp = [str(sem_count)+"_"+ possible_courses[x]]
        if len(course_history) == 0:
            possible_semester.append(temp.copy())
        else:
            temp_1 = course_history.copy()
            temp_1.extend(temp.copy())
            possible_semester.append(temp_1)

        for y in range(x+1, len(possible_courses)):
            temp.extend([str(sem_count)+"_"+possible_courses[y]])
            if len(course_history) == 0:
                possible_semester.append(temp.copy())
            else:
                temp_2 = course_history.copy()
                temp_2.extend(temp.copy())
                possible_semester.append(temp_2)
    return possible_semester

def check_core_incomplete(history):
    needed_crs = list(import_tools.preq_map.keys())
    temp_crs_hist = set()
    if history is []:
        return False
    for crs in history:
        temp_crs_hist.add(crs.split("_")[1])
    for crs in needed_crs:
        if crs not in temp_crs_hist:
            return True
    return False


def find_all_sequences(series_list, sem_count):
    complete_series = []
    for series in series_list:
        #print(sem_count)
        if (check_core_incomplete(series)):
            if sem_count >= 10:
                continue
            if sem_count > 8 and not any(crs.endswith("CSC340") for crs in series):
                continue
            #print(series)
            new_series_list = find_possible_semester_sequence(series, sem_count+1)
            for ser_n in new_series_list:
                #print(sem_count)
                #print(ser_n)
                check = find_all_sequences([ser_n], sem_count+1)
                for x in check:
                    complete_series.append(x)
        else:
            #print(series)
            complete_series.append(series)

    return complete_series


def get_top_series(grade_level, hard_seq):
    if grade_level == "freshman":
        top_set = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/seq_only_final_top300_freshman_start_add412_211_10max.csv",
                                      "\n", ",", False)
    elif grade_level == "sfsu_seq_check":
        top_set = utils.list_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/SFSU_Recommended_Seq.csv",
            "\n", ",", False)
    else:
        top_set = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/seq_only_final_top300_xfer_start_add412_8max.csv",
                                      "\n", ",", False)
    parsed_series = []
    for series in top_set:
        temp_list = []
        for ser in series:
            crs = ser.split("_")[1]
            count = ser.split("_")[0]
            if hard_seq:
                print(ser)
                temp_list.append(counter_list[int(count)]+"_"+crs)
            else:
                temp_list.append(crs)

        parsed_series.append(temp_list)

    return parsed_series

def compare_series(students, filter_type, level, hard_seq):
    top_series = get_top_series(level, hard_seq)
    output = []
    for student in students:
        skip = False
        #print(student.id_num)
        temp_list = []
        semester_keys = list(student.course_seq_dict.keys())
        semester_keys.sort()
        counter = 1
        for seq_int in semester_keys:
            student_sem_hist = student.course_seq_dict[seq_int]
            for x in student_sem_hist:
                if filter_type == 'generic_ge':
                    if x.course_type == "ge":
                        temp_list.append("GE")
                elif filter_type == "cs_only":
                    if x.course_type == "core" or x.course_type == "bonus":
                        temp_list.append(x.name)
                elif filter_type == "cs_only_seq":
                    if x.course_type == "core" or x.course_type == "bonus":
                        temp_list.append(counter_list[counter] + "_" + x.name)
                else:
                    temp_list.append(counter_list[counter]+"_"+x.name)
            counter +=1
        max_comp = 0
        if len(temp_list) == 0:
            output.append(student)
            continue
        for comp_ser in top_series:
            #print(comp_ser)
            score = pairwise2.align.globalxx(temp_list, comp_ser, score_only=True)
            #print(score)
            if score > max_comp:
                max_comp = score
        student.seq_sim_score = max_comp
        output.append(student)
    return output

counter_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "i", "l", "m", "n", "o", "p", "q",
                  "r", "s", "t", "u", "v", "w", "x", "y", "z","aa", "bb", "cc", "dd", "ee", "ff", "gg", "hh", "ii"]

#test = find_possible_semester_sequence(["0_CSC210", "0_MATH226", "0_MATH227", "0_PHYS220", "0_PHYS230", "0_CSC220", "0_CSC230"], 1)
#datas = find_all_sequences(test, 1)
#print(datas)
#utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_xfer_CSC210_230_M67_P2030.csv", datas)

#test = find_possible_semester_sequence([], 1)
#datas = find_all_sequences(test, 1)
#print(datas)
#utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_8.csv", datas)

#test = find_possible_semester_sequence(["1_MATH226", "1_CSC210", "1_CSC211"], 2)
#datas = find_all_sequences(test, 2)
#print(datas)
#utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_10_math226_csc210_211.csv", datas)

#test = find_possible_semester_sequence([], 1)
#datas = find_all_sequences(test, 1)
#print(datas)
#utils.list_to_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_10.csv", datas)

#score_series_set("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_10.csv",
#                "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/top_100_series_8_redo_clean_2.csv", True, True)

#score_series_set("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/SFSU_Recommended_Seq.csv",
#                 "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/SFSU_Recommended_Seq_score.csv", False, False)