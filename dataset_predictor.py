import utils
import numpy as np
from sklearn.cluster import KMeans, AffinityPropagation, AgglomerativeClustering, MeanShift
import cluster_analysis as ca
import os
from sklearn import metrics
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import datasets, svm
import random

def split_dataset(students, **kwargs):
    test_set = []
    train_set = []
    type_dict = {}

    if "one_year_run" in kwargs:
        for student in students:
            if len(student.sem_seq_dict) == 1 and student.sem_seq_dict[1] == "2014":
                continue
            if len(student.sem_seq_dict) > 1:
                train_set.append(student)
            else:
                test_set.append(student)
    elif "rm_dropouts" in kwargs:
        for student in students:
            if (len(student.sem_seq_dict) == 1 and student.sem_seq_dict[1] == "2014") or "dropout" in student.status:
                continue
            if len(student.sem_seq_dict) > 1:
                train_set.append(student)
            else:
                test_set.append(student)
    else:
        for student in students:
            if len(student.sem_seq_dict) == 1 and student.sem_seq_dict[1] == "2014":
                continue
            utils.add_to_dict_list(student.major, student, type_dict)
        for types in type_dict:
            workingset = type_dict[types]
            for student in workingset:
                check = random.random()
                if check > .7:
                    test_set.append(student)
                else:
                    train_set.append(student)

    return train_set, test_set




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


def precompute_sim(students, vect_type, outpath):
    output = []
    for x in range(0, len(students)):
        student_a = students[x]
        print(x)
        for y in range(x+1, len(students)):
            student_b = students[y]
            dissim = 1 - cosine_similarity(student_a.fp_dict["vect_type"], student_b.fp_dict["vect_type"])
            output.append(str(student_a.id_num)+","+str(student_b.id_num)+","+str(dissim))
    utils.list_to_file(outpath, output)

def classifiy_dropout(training_set, testing_set, vect):
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    X = []
    y = []
    for student in training_set:
        X.append(student.fp_dict[vect])
        if "drop_out" not in student.status:
            y.append("Pass")
        else:
            y.append("Failout")

    clf = svm.SVC(kernel='rbf', C=1.0)
    clf.fit(X, y)

    for student in testing_set:
        pred = clf.predict([student.fp_dict[vect]])
        print("********")
        print(pred[0])
        print(student.status)
        if pred[0] == "Pass" and "drop_out" not in student.status:
            tp += 1
            print("tp")
        elif pred[0] == 'Pass' and "drop_out" in student.status:
            fp += 1
            print("fp")
        elif pred[0] == 'Failout' and "drop_out" not in student.status:
            fn += 1
            print("fn")
        else:
            tn += 1
            print("tn")

        print("*********")

    print(str(len(testing_set)) +" total prediction")
    print (tp)
    print (tn)
    print (fp)
    print (fn)
    print("___")


def pred_student_grade(training_set, testing_set, pred_class, pred_class_seq, vect): #TODO build stats for success, train in bulk using year 1, year 2 etc
    X = []
    y = []

    for student in training_set:
        ref_course_list = []
        for x in range(1,pred_class_seq):
            ref_course_list.extend(student.course_seq_dict[x])
        if pred_class not in student.unique_courses:
            continue
        X.append(student.fp_dict[vect])
        y.append(int(student.unique_courses[pred_class][0].grade))

    clf = svm.SVC(kernel='rbf', C=1.0)
    clf.fit(X, y)
    acc_avg = 0
    total = 0
    for student in testing_set:

        pred = clf.predict([student.fp_dict[vect]])
        try:
            real_grade = student.unique_courses[pred_class][0].grade
        except KeyError:
            continue
        diff = abs(pred - real_grade)[0]
        if real_grade == 0:
            pct_off = 1
        else:
            pct_off = diff/real_grade
            if pct_off > .3:
                print("-----")
                print(student.id_num)
                print(real_grade)
                print(pred)
                print("-----")
            acc_avg += pct_off
            total += 1
        print(pct_off)
    print(acc_avg/total)