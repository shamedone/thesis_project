import utils
import numpy as np
from sklearn.cluster import KMeans, AffinityPropagation, AgglomerativeClustering, MeanShift
import cluster_analysis as ca
import os
from sklearn import metrics
from sklearn.metrics import jaccard_similarity_score


#TODO current plan is to build up to predictor using combination of three vectors, one for class progres, one for
# grades, one for repeats, and one final overal GPA score. Prediction will work by identifying possible course, building
# a test set for students out to those courses, and then predicting in sequence noting the effect on GPA. The courses
# that help GPA the most will be

def build_class_key_vector(core_data, elective_data, request_type):
    key_dict = {}
    i = 0
    for data in core_data:
        key_dict[data[0]] = i
        i+=1
    if request_type == "all":
        for data in elective_data:
            key_dict[data[0]] = i
            i+=1
    #for keys in key_dict:
    #    print(keys + " " + str(key_dict[keys]))

    return key_dict

def build_student_vector(student, class_dict, request, vect_type):
    course_history = student.course_history
    sequence_vect = [0] * len(class_dict)
    grade_vect = [0] * len(class_dict)
    repeat_vect = [0] * len(class_dict)
    seq_int = 1
    current_semester = course_history[0].semester
    grades = []
    for course in course_history:
        if course.class_type != "core" and request == "core":
            #print(course.name)
            continue
        semester = course.semester
        grade = course.grade
        name = course.name
        if semester != current_semester:
            seq_int +=1
            current_semester = semester
        sequence_vect[class_dict[name]] = seq_int
        if grade_vect[class_dict[name]] != 0:
            temp = repeat_vect[class_dict[name]]
            temp+=1
            repeat_vect[class_dict[name]] = temp
            temp_grade = grade_vect[class_dict[name]]
            temp_grade.append(grade)
            grade_vect[class_dict[name]] = temp_grade
        else:
            grade_vect[class_dict[name]] = [grade]
        grades.append(grade)
    for x in range(0, len(grade_vect)):
        if grade_vect[x] == 0:
            continue
        grade_vect[x] = sum(grade_vect[x])/float(len(grade_vect[x]))


    #print(sequence_vect)
    #print(grade_vect)
    #print(repeat_vect)
    #print([sum(grades)/float(len(grades))])
    if vect_type == "simple":
        return grade_vect
    else:
        return sequence_vect + grade_vect + repeat_vect + [sum(grades)/float(len(grades))]




def cluster(student_vects, request_type, vect_type, base_dir, dissim_path):
    cluster_data = []
    student_list = []
    student_output = []
    for student in student_vects:
        cluster_data.append(student_vects[student])
        student_output.append(str(student.id_num) + "," +str(student.grade_adj) + ","+str(student.age))
        student_list.append(student)

    #ms = MeanShift().fit_predict(cluster_data)
    #ward = AgglomerativeClustering(n_clusters=5, linkage='ward').fit_predict(cluster_data)
    #utils.list_to_file(base_dir+"/test_labels_"+request_type+"_"+vect_type, student_output)
    #utils.list_to_file("test_clusters_ms", ms)
    n_set = [5]
    #dissim_list = utils.list_from_file(dissim_path,"\n", ",", False)
    #dissim_dict = ca.format_dissim_list(dissim_list)
    """
    for n in n_set:
        pred_clusters = KMeans(n_clusters=n).fit(cluster_data)
        analysis_set = ca.cluster_analysis(cluster_data, pred_clusters.labels_, student_list, dissim_dict)
        os.mkdir(base_dir+"/"+str(n)+"_run")
        for clust in analysis_set:
            ca.print_stats(analysis_set[clust], clust, base_dir+"/"+str(n)+"_run")
            utils.list_to_file("test_clusters_kmeans_"+str(n)+"_"+request_type+"_"+vect_type, pred_clusters.labels_)

    """
    utils.list_to_file("test_labels_2_2"+vect_type+"_"+request_type+".csv", student_output)

    af = AffinityPropagation().fit(cluster_data)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    n_clusters_ = len(cluster_centers_indices)

    #print('Estimated number of clusters: %d' % n_clusters_)
    #print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    #print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    #print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    #print("Adjusted Rand Index: %0.3f"
    #      % metrics.adjusted_rand_score(labels_true, labels))
    #print("Adjusted Mutual Information: %0.3f"
    #      % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, labels, metric='sqeuclidean'))
    utils.list_to_file("test_clusters_af_"+vect_type+"_"+request_type, af.labels_)
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, af.labels_))


    print("km 10")
    pred_clusters = KMeans(n_clusters=10).fit(cluster_data)
    utils.list_to_file("test_clusters_kmeans_10_"+vect_type+"_"+request_type, pred_clusters.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, pred_clusters.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, pred_clusters.labels_))
    print("km 15")
    pred_clusters = KMeans(n_clusters=15).fit(cluster_data)
    utils.list_to_file("test_clusters_kmeans_15_"+vect_type+"_"+request_type, pred_clusters.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, pred_clusters.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, pred_clusters.labels_))
    print("km 5")
    pred_clusters = KMeans(n_clusters=5).fit(cluster_data)
    utils.list_to_file("test_clusters_kmeans_5_"+vect_type+"_"+request_type, pred_clusters.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, pred_clusters.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, pred_clusters.labels_))
    #pred_clusters = KMeans(n_clusters=15).fit(cluster_data)
    #utils.list_to_file("test_clusters_kmeans_15_cls_core", pred_clusters.labels_)
    #utils.list_to_file("test_clusters_ward", ward)
    print("ward5")
    ward = AgglomerativeClustering(n_clusters= 5).fit(cluster_data)
    utils.list_to_file("test_clusters_ward_5clust"+vect_type+"_"+request_type, ward.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, ward.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, ward.labels_))
    print("ward10")
    ward = AgglomerativeClustering(n_clusters= 10).fit(cluster_data)
    utils.list_to_file("test_clusters_ward_10clust"+vect_type+"_"+request_type, ward.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, ward.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, ward.labels_))
    print("ward15")
    ward = AgglomerativeClustering(n_clusters= 15).fit(cluster_data)
    utils.list_to_file("test_clusters_ward_15clust"+vect_type+"_"+request_type, ward.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, ward.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, ward.labels_))
    print("ms")
    ms = MeanShift().fit(cluster_data)
    utils.list_to_file("test_clusters_ms" + vect_type + "_" + request_type, ms.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, ms.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, ms.labels_))

def run_student_vectors(core_path, elective_path, request_type, vect_type, base_dir, sim_path):
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", "," ,False)
    class_dict = build_class_key_vector(core_data, elective_data, request_type)
    student_list = utils.get_students_history()
    student_vects = {}
    for student in student_list:
        vect = build_student_vector(student, class_dict, request_type, vect_type)
        student_vects[student] = vect
    sim_path = sim_path+request_type+"_"+vect_type+".csv"
    cluster(student_vects, request_type, vect_type, base_dir, sim_path)
    return

run_student_vectors("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv",
                    "all",
                    "simple",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/prediction_tests",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/student_sims_")


def precompute_sim(core_path, elective_path, request_type, vect_type, outpath):
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", ",", False)
    class_dict = build_class_key_vector(core_data, elective_data, request_type)
    student_list = utils.get_students_history()
    student_vects = {}
    for student in student_list:
        vect = build_student_vector(student, class_dict, request_type, vect_type)
        student_vects[student] = vect
    output = []
    for x in range(0, len(student_list)):
        student_a_vect = utils.grade_vect_to_bit(student_vects[student_list[x]])
        print(x)
        for y in range(x+1, len(student_list)):
            student_b_vect = utils.grade_vect_to_bit(student_vects[student_list[y]])
            tani = 1.0 - jaccard_similarity_score(student_a_vect, student_b_vect)
            output.append(str(student_list[x].id_num)+","+str(student_list[y].id_num)+","+str(tani))
    utils.list_to_file(outpath, output)

#TODO FIX THIS TO PRECOMPUTE SIMS
"""
precompute_sim("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv",
                    "core",
                    "simple",
               "/Users/thomasolson/Documents/workspace/advising_revamp/student_dissims_core_simple_1_22_19.csv"
               )

precompute_sim("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv",
                    "core",
                    "all",
               "/Users/thomasolson/Documents/workspace/advising_revamp/student_dissims_core_all_1_22_19.csv"
               )

precompute_sim("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv",
                    "all",
                    "simple",
               "/Users/thomasolson/Documents/workspace/advising_revamp/student_dissims_all_simple_1_22_19.csv"
               )

precompute_sim("/Users/thomasolson/Documents/workspace/advising_revamp/core.csv",
                    "/Users/thomasolson/Documents/workspace/advising_revamp/electives.csv",
                    "all",
                    "all",
               "/Users/thomasolson/Documents/workspace/advising_revamp/student_dissims_all_all_1_22_19.csv"
               )
"""