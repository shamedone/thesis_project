import utils
import numpy as np
from sklearn import metrics
import plotly.plotly as py
import plotly.graph_objs as go

def cluster_analysis(cluster_data, labels, student_list):

    db = metrics.davies_bouldin_score(cluster_data, labels)
    ch = metrics.calinski_harabaz_score(cluster_data, labels)
    sh = metrics.silhouette_score(cluster_data, labels, metric='euclidean')
    cluster_dict = build_cluster_results(labels, student_list)
    cluster_set = []
    stat_package_set = {}
    for clust in cluster_dict:
        cluster_set.append(clust)
    cluster_set.sort()
    for clust in cluster_set:
        student_set = cluster_dict[clust]
        grades = get_grades(student_set)
#        tani_measures = compare_class_tanimoto(clust, cluster_dict, dissim_dict)
        stat_package = {}
        stat_package['db'] = db
        stat_package['ch'] = ch
        stat_package['sh'] = sh
        stat_package['mean_grade'] = np.mean(grades)
        stat_package['median_grade'] = np.median(grades)
        stat_package['std_grade'] = np.std(grades)
        stat_package['grades'] = grades
#        stat_package['tani_within'] = tani_measures[0]
#        stat_package['tani_without'] = tani_measures[1]
        stat_package['plot_data'] = [go.Histogram(x=grades)]
        stat_package_set[clust] = stat_package
    return stat_package_set

def print_stats(stat_pack, clust_index, filename):
    output = []
    output.append("Stats for cluster "+str(clust_index))
    output.append("DB index (lower is better) , "+str(stat_pack['db']))
    output.append("CH index (higher is better), "+str(stat_pack['ch']))
    output.append("SH index (1 is best), "+str(stat_pack['sh']))
    output.append("Jaccard within (sim), "+str(stat_pack['tani_within']))
    output.append("Jaccard without (sim), "+str(stat_pack['tani_within']))
    output.append("Mean grade, "+str(stat_pack['mean_grade']))
    output.append("Median grade, "+str(stat_pack['median_grade']))
    output.append("Standard div , "+str(stat_pack['std_grade']))
    py.plot(stat_pack['plot_data'], filename=filename+"/"+str(clust_index+"_grade_hist"))


def get_grades(student_set):
    grades = []
    for student in student_set:
        course_hist = student.course_history
        for course in course_hist:
            grades.append(course.grade)
    return grades

def compare_class_tanimoto(prime_clust, clust_dict, dissim_dict):
    within_dist = []
    without_dist = []
    student_set = clust_dict[prime_clust]

    for x in range(0, len(student_set)):
        print(x)
        #student_a_vect = grade_vect_to_bit(student_vects[studnet_set[x]])
        student_a = student_set[x].id_num
        for y in range(x+1, len(student_set)):
            student_b = student_set[y].id_num
            #student_b_ = grade_vect_to_bit(student_vects[studnet_set[y]])
            #tani = jaccard_similarity_score(student_a_vect, student_b_vect)
            tani = dissim_dict[student_a+student_b]
            within_dist.append(tani)
    compare_set = []

    for clust in clust_dict:
        if clust == prime_clust:
            continue
        compare_set.extend(clust_dict[clust])

    for x in range(0, len(student_set)):
        print(x)
        student_a = student_set[x].id_num
        #student_a_vect = grade_vect_to_bit(student_vects[studnet_set[x]])
        for y in range(0, len(compare_set)):
            student_b = compare_set[y].id_num
            #student_b_vect = grade_vect_to_bit(student_vects[compare_set[y]])
            #tani = jaccard_similarity_score(student_a_vect, student_b_vect)
            tani = dissim_dict[student_a+student_b]
            without_dist.append(tani)
    return within_dist, without_dist



def build_cluster_results(lables, student_list):
    dict = {}
    for x in range(0,len(lables)):
        student = student_list[x]
        clust = lables[x]
        utils.append_to_dict(clust, student, dict)
    return dict

def format_dissim_list(sim_list):
    sim_dict = {}
    for entry in sim_list:
        student_a = entry[0]
        student_b = entry[1]
        dissim = float(entry[2])
        sim_dict[student_a+student_b] = dissim
        sim_dict[student_b+student_a] = dissim
