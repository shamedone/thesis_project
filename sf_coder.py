import utils

def translate_sfsu_data(line):
    skipset = {"AU", "W", "RP", "RD",""}

    if line[4] == "M":
        line[4] = 0
    else:
        line[4] = 1

    if line[5] == "8TwoMore":
        line[5] = 4
    else:
        line[5] = int(line[5][0])
    if line[22] == "":
        line[22] = 0
    if line[25] == "":
        line[25] = 0
    if line[23] == "":
        line[23] = 0
    if line[26] == "":
        line[26] = 0

    line[7] = translate_abc(line[7][0])
    line[8] = translate_abc(line[8][0])
    line[9] = line[9][0]
    #line[23] = get_intr_grade(line[22])

    return line

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




