from efficient_apriori import apriori
from pymining import seqmining
import utils
import import_tools
from operator import itemgetter
from Bio import pairwise2

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

#old apriori method
def run_apriori(transaction_dict, semester_set, min_support, min_confidence):
    for semester in semester_set:
        itemsets, rules = apriori(transaction_dict[semester], min_support, min_confidence)
        print("SEMESTER "+str(semester))
        print(itemsets)
        print(rules)

#tester method
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

#counts how semesters students take a course
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

def build_crs_hist(seq):
    crs_dict = {}
    for crs in seq:
        sem = int(crs.split("_")[0])
        course = crs.split("_")[1]
        if course not in crs_dict:
            crs_dict[course] = [0]*11
        temp = crs_dict[course]
        temp[sem] = temp[sem]+1
        crs_dict[course] = temp

    return crs_dict

#scoring function to score a sequence based on scores found from impact analysis
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

#scores sequneces based on score map. Returns top 100 scoring sequences, has options to force add CSC211 and CSC412/
#also includes options to only do transfer, combo, or freshman.
def score_series_set(path, outpath, add_412, add_211, class_type):

    #score maps are built from sequence analysis and I have included examples of their format in git.
    if class_type.lower() == "transfer":
        seq_score_map = utils.dict_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/subset_transfer_sequence_score_map_25.csv",
                                            0,1,"\n", ",", True)
        equiv_score_map = utils.dict_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/subset_transfer_concurrent_score_map_25.csv",
                                            0,1,"\n", ",", True)
    elif class_type.lower() == "49_set":#This was some testing work I did
        seq_score_map = utils.dict_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/49_cs_sequence_score_map_25.csv",
            0, 1, "\n", ",", True)
        equiv_score_map = utils.dict_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/49_cs_concurrent_score_map_25.csv",
            0, 1, "\n", ",", True)
    else:
        seq_score_map = utils.dict_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/combo_score_seq_mod_bonus.csv",
            0, 1, "\n", ",", True)
        equiv_score_map = utils.dict_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/group analysis runs/combo_score_equiv_mod_bonus.csv",
            0, 1, "\n", ",", True)



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
                    #if "PHYS220" in line[sem_x]:  #Typically unneeded due to presence of PHYS230/222 scores that capture same info.
                    #    sem = line[sem_x].split("_")[0]
                    #    line.insert(sem_x+1, sem+"_PHYS222")
                    #if "PHYS230" in line[sem_x]:
                    #    sem = line[sem_x].split("_")[0]
                    #    line.insert(sem_x+1, sem+"_PHYS232")

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


#returns all possible courses that can be taken based on prereqs
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

#finds all possible semster course combinations given a starting semester
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

#checks to see if all core courses are complete
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

#recursive sequence builds all possible semester sequences based on starting coures history, which can be initalized or blank ([]).
#includes sem count to halt sequence if semester count is exceeded
def find_all_sequences(series_list, sem_count):
    complete_series = []
    for series in series_list:
        #print(sem_count)
        if (check_core_incomplete(series)):
            if sem_count >= 8:
                continue
            if sem_count > 6 and not any(crs.endswith("CSC340") for crs in series):
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


def get_top_series(grade_level, hard_seq, score_format):
    if grade_level.lower() == "freshman_10":
        top_set = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/top1_subset_all_possible_series_10_old_cir_only_score_freshman_bonus_412add_211add.csv",
                                      "\n", ",", False)
    elif grade_level.lower() == "freshman_8":
        top_set = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/7_25_top_1_impact_summary_seq.csv",
                                      "\n", ",", False)
    elif grade_level == "sfsu_seq_check":
        top_set = utils.list_from_file(
            "/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/SFSU_Recommended_Seq.csv",
            "\n", ",", False)
    else:
        top_set = utils.list_from_file("/Users/thomasolson/Documents/workspace/advising_revamp/series analysis/all_possible_series_xfer_6_scored_412add.csv",
                                      "\n", ",", False)
    parsed_series = []
    for series in top_set:
        temp_list = []
        y =0
        if score_format:
            y=1
        for x in range (y, len(series)):
            ser = series[x]
            if score_format:
                ser = ser.strip("[]\\' ")
            crs = ser.split("_")[1]
            count = ser.split("_")[0]
            if hard_seq:
                temp_list.append(counter_list[int(count)]+"_"+crs)
                #temp_list.append(count+"_"+crs)
            else:
                temp_list.append(crs)

        parsed_series.append(temp_list)

    return parsed_series


#scores similarity of sequences based on pairwise alignment. can be hard sequence, meaning coruess must match sequence a
#sequence, or soft, in which names only count. Course names and sequence are combined ex: "1_CSC210", "1_CSC211, "2_CSC220.
# For hard sequencing, the code replaces integers with letters so as long as courses are taken in same sequence, it does not
#matter if they take them the same semesters, since it only looks at core courses. So "1_CSC210, 2_ENG100, 3_CSC220 would be
#treated the same as "1_CSC210, 2_ENG100, 2_CSC210" as the translated sequence for each would be "A_CSC210, B_CSC220
def compare_series(students, filter_type, level, hard_seq, score_format):
    top_series = get_top_series(level, hard_seq, score_format)
    output = []
    if "sfsu" in level:
        level = "freshman_8"
    for student in students:
        if student.status != "graduated_cs":
            continue
        if student.admin_descript != "1" and "freshman" in level.lower():
            continue
        if student.admin_descript != "2" and "transfer" in level.lower():
            continue
        skip = False
        print(student.id_num)
        temp_list = []
        semester_keys = list(student.course_seq_dict.keys())
        semester_keys.sort()
        counter = 1
        for seq_int in semester_keys:
            student_sem_hist = student.course_seq_dict[seq_int]
            found = False
            for x in student_sem_hist:
                if filter_type == 'generic_ge':
                    if x.course_type == "ge":
                        temp_list.append("GE")
                elif filter_type == "cs_only":
                    if x.course_type == "core" or x.course_type == "bonus":
                        temp_list.append(x.name)
                elif filter_type == "cs_only_seq":
                    if x.course_type == "core" or x.course_type == "bonus" or x.name in ["CSC412", "CSC211"]:
                        if hard_seq:
                            print(counter_list[counter])
                            temp_list.append(counter_list[counter] + "_" + x.name)
                            #temp_list.append(str(seq_int) + "_" + x.name)
                            found = True
                        else:
                            temp_list.append(x.name)

                else:
                    temp_list.append(counter_list[counter] + "_" + x.name)
                    found = True
#                    if x.course_type == "core" or x.course_type == "bonus":
#                        temp_list.append(str(seq_int) + "_" + x.name)
#                else:
#                    temp_list.append(str(seq_int)+"_"+x.name)

            if found:
                counter +=1

        max_comp = 0
        if len(temp_list) == 0:
            output.append(student)
            continue
        for comp_ser in top_series:
            #print(comp_ser)
            score = pairwise2.align.globalxx(temp_list, comp_ser, score_only=True)
            #print(score)
            if score == []:
                continue
            if score > max_comp:
                max_comp = score
        student.seq_sim_score = max_comp
        output.append(student)
    return output


def build_series_historgram(series, score_included):

    all_series = []
    for data in series:
        x = 0
        if score_included:
            x+=1
        for y in range(x, len(data)):
            all_series.append(data[y].strip("[]\\' "))
    dict = build_crs_hist(all_series)
    output = []
    for data in dict:
        output.append([data, str(dict[data]).strip("[]")])
    return output


counter_list = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "i", "l", "m", "n", "o", "p", "q",
                  "r", "s", "t", "u", "v", "w", "x", "y", "z","aa", "bb", "cc", "dd", "ee", "ff", "gg", "hh", "ii"]

