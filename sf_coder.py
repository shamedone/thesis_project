import utils

def translate_sfsu_data(path, outpath):
    datas = utils.list_from_file(path,"\n",",",False)
    output = [datas.pop(0)]
    skipset = {"AU", "W", "RP", "RD",""}
    for data in datas:
        line = data
        if line[22] in  skipset:
            continue
        if line[4] == "M":
            line[4] = 0
        else:
            line[4] = 1

        if line[5] == "8TwoMore":
            line[5] = 4
        else:
            line[5] = int(line[5][0])

        line[7] = translate_abc(line[7][0])
        line[8] = translate_abc(line[8][0])
        line[9] = line[9][0]
        line[23] = get_intr_grade(line[22])
        output.append(line)

    utils.list_to_file(outpath, output)

def get_intr_grade(course_grade):
    if course_grade == "A":
        return 95
    if course_grade == "A-":
        return 92
    if course_grade == "B+":
        return 88
    if course_grade == "B":
        return 85
    if course_grade == "B-":
        return 82
    if course_grade == "C+":
        return 78
    if course_grade == "C":
        return 75
    if course_grade == "C-":
        return 72
    if course_grade == "D+":
        return 68
    if course_grade == "D":
        return 65
    if course_grade == "D-":
        return 62
    if course_grade == "F":
        return 50
    if course_grade == "NC":
        return 50
    if course_grade == "CR":
        return 80
    if course_grade == "I":
        return 30
    if course_grade == "IC":
        return 30
    if course_grade == "WU":
        return 30
    if course_grade == "WM":
        return 30
    else:
        return "NO MATCH"




def translate_abc(input):
    if input == "a":
        return 1
    if input == "b":
        return 2
    if input == "c":
        return 3
    if input == "d":
        return 4
    if input == "e":
        return 5
    if input == "f":
        return 6
    if input == "g":
        return 7
    else:
        return 0



translate_sfsu_data("/Users/thomasolson/Documents/workspace/advising_revamp/sfsu_data.csv", "/Users/thomasolson/Documents/workspace/advising_revamp/translated_sfsu_data.csv")

