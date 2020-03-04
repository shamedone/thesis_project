import utils
import dataset_stage as ds
import numpy as np
from sklearn.cluster import KMeans, AffinityPropagation, AgglomerativeClustering, MeanShift
import cluster_analysis as ca
import os
from sklearn import metrics
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import datasets, svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

import random


def split_dataset_old(students, **kwargs): #need to revamp for sfsu - remove one semesters wonders,
    test_set = []
    train_set = []
    type_dict = {}

    if "one_year_run" in kwargs:
        for student in students:
            if len(student.sem_seq_dict) == 1 and student.sem_seq_dict[1] == kwargs['one_year_run']:
                check = random.random()
                if check > .7:
                    train_set.append(student)
                else:
                    test_set.append(student)
    elif "rm_dropouts" in kwargs:
        for student in students:
            if "dropout" in student.status:
                continue
            check = random.random()
            if check > .7:
                test_set.append(student)
            else:
                train_set.append(student)
    elif "sfsu_do_run" in kwargs:
        for student in students:
#            if len(student.course_seq_dict) < 2 or student.admin_descript != "1" or student.spring_19_flag == "1":
            if len(student.course_seq_dict) < 2 or student.admin_descript != "1":
                continue
            check = random.random()
            if check > .7:
                test_set.append(student)
            else:
                train_set.append(student)


    return train_set, test_set


def split_dataset(students): #assumes dataset already split up
    test_set = []
    train_set = []
    type_dict = {}
    for student in students:
        check = random.random()
        if check > .7:
            test_set.append(student)
        else:
            train_set.append(student)


    return train_set, test_set


def cluster_run(students, n):
    cluster_data = []
    student_list = []
    student_output = []
    for student in students:
        cluster_data.append(student.fp_dict['master'])
        student_list.append(student)

    clusterer = KMeans(n_clusters=n, max_iter=500)
    #clusterer = AffinityPropagation()
    #clusterer = MeanShift()
    pred_clusters = clusterer.fit_predict(cluster_data)

    silhouette_avg = silhouette_score(cluster_data, pred_clusters)
    # Create a subplot with 1 row and 2 columns
    fig, (ax1) = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)

    ax1.set_xlim([-0.1, 1])
    ax1.set_ylim([0, len(cluster_data) + (n + 1) * 10])

    labels = set()
    for clust in pred_clusters:
        labels.add(clust)

    print("For n_clusters =", len(labels),
          "The average silhouette_score is :", silhouette_avg)

    # Compute the silhouette scores for each sample
    sample_silhouette_values = silhouette_samples(cluster_data, pred_clusters)

    y_lower = 10
    for i in range(len(labels)):
        # Aggregate the silhouette scores for samples belonging to
        # cluster i, and sort them
        ith_cluster_silhouette_values = \
            sample_silhouette_values[pred_clusters == i]

        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        color = cm.nipy_spectral(float(i) / n)
        ax1.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

        # Label the silhouette plots with their cluster numbers at the middle
        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

        # Compute the new y_lower for next plot
        y_lower = y_upper + 10  # 10 for the 0 samples

    ax1.set_title("The silhouette plot for the various clusters.")
    ax1.set_xlabel("The silhouette coefficient values")
    ax1.set_ylabel("Cluster label")

    # The vertical line for average silhouette score of all the values
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                  "with n_clusters = %d" % n),
                 fontsize=14, fontweight='bold')

    #plt.show()

    cluster_dict = {}
    for x in range(0, len(pred_clusters)):
        result = pred_clusters[x]
        student = students[x]
        student.pred = result
        student.pred_class = "cluster"
        utils.add_to_dict_list(result,student, cluster_dict)

    return students, cluster_dict

def cluster_plots(students):
    cluster_data = []
    student_list = []
    student_output = []
    for student in students:
        cluster_data.append(student.fp_dict['master'])
        student_list.append(student)

    print(len(cluster_data))
    n_set = [2,3,4,5,6,7,8,10,12,14]
    sil_dict = {}

    for n in n_set:
        clusterer = KMeans(n_clusters=n)
        pred_clusters = clusterer.fit_predict(cluster_data)

        silhouette_avg = silhouette_score(cluster_data, pred_clusters)
        # Create a subplot with 1 row and 2 columns
        fig, (ax1) = plt.subplots(1, 1)
        fig.set_size_inches(10, 10)


        ax1.set_xlim([-0.1, 1])
        ax1.set_ylim([0, len(cluster_data) + (n + 1) * 10])

        print("For n_clusters =", n,
              "The average silhouette_score is :", silhouette_avg)

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(cluster_data, pred_clusters)

        y_lower = 10
        for i in range(n):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = \
                sample_silhouette_values[pred_clusters == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n)
            ax1.fill_betweenx(np.arange(y_lower, y_upper),
                              0, ith_cluster_silhouette_values,
                              facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])


        plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                      "with n_clusters = %d" % n),
                     fontsize=14, fontweight='bold')

    plt.show()

"""
def run_student_vectors(core_path, elective_path, request_type, vect_type, base_dir, sim_path):
    elective_data = utils.list_from_file(elective_path, "\n", ",", False)
    core_data = utils.list_from_file(core_path, "\n", "," ,False)
    class_dict = ds.build_class_key_vector(core_data, elective_data, request_type)
    student_list = utils.get_students_history()
    student_vects = {}
    for student in student_list:
        vect = ds.build_student_vector(student, class_dict, request_type, vect_type)
        student_vects[student] = vect
    sim_path = sim_path+request_type+"_"+vect_type+".csv"
    cluster(student_vects, request_type)
    return
"""

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
        if "dropout" not in student.status:
            y.append("Pass")
        else:
            y.append("Failout")

    #clf = svm.SVC(kernel='rbf', C=1.0)
    #clf = ComplementNB()
    #clf = ExtraTreesClassifier(n_estimators=300)
    #clf = AdaBoostClassifier(n_estimators=400)
    clf = RandomForestClassifier(n_estimators=400)
    clf.fit(X, y)

    pred_dict = {}
    for student in testing_set:
        pred = clf.predict([student.fp_dict[vect]])

        #print("********")
        #print(pred[0])
        #print(student.status)
        student.pred = pred[0]
        if pred[0] == "Pass" and "dropout" not in student.status:
            tp += 1
            #print("tp")
            student.pred_class = "tp"
        elif pred[0] == 'Pass' and "dropout" in student.status:
            fp += 1
            #print("fp")
            student.pred_class ="fp"

        elif pred[0] == 'Failout' and "dropout" not in student.status:
            fn += 1
            #print("fn")
            student.pred_class ="fn"

        else:
            tn += 1
            #print("tn")
            student.pred_class = "tn"


        #print("*********")

    print(str(len(testing_set)) +" total prediction")
    print (str(tp) + " true positive")
    print (str(fn) + " true neg")
    print (str(fp) + " false positive")
    print (str(fn) + " false neg")
    print("___")
    return testing_set

def pred_student_grade_spanish(training_set, testing_set, pred_class, pred_class_seq, vect): #TODO build stats for success, train in bulk using year 1, year 2 etc
    X = []
    y = []

    for student in training_set:
        ref_course_list = []
        for x in range(1,pred_class_seq):
            ref_course_list.extend(student.course_seq_dict[x])
        if pred_class not in student.unique_courses: #skips if that student has not taken class for predicition
            continue
        X.append(student.fp_dict[vect])
        y.append(int(student.unique_courses[pred_class].grade))

    clf = svm.SVC(kernel='rbf', C=1.0)

    clf.fit(X, y)
    acc_avg = 0
    total = 0
    for student in testing_set:

        pred = clf.predict([student.fp_dict[vect]])
        try:
            real_grade = student.unique_courses[pred_class].grade
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

def assess_possible_classes_sfsu(student, sfsu_core_classes): #return a list of courses possible to take

    taken = student.passed_classes
    possible = []
    for course in sfsu_core_classes:
        if course.name in taken:
            continue #skip course taken
        eligible = student.check_prereqs(course.prereqs)
        if eligible:
            possible.append(course)
    return possible



def pred_student_grade_sfsu(): #So lets things about this. IRL, the student wouldnt not have all the neceessary classes
    return                      #but where we can still do same thing as spanish and set a cutoff for the semesters, then make predictions for the next
                                #set of possible classes.


def cluster_old(student_vects, request_type, vect_type, base_dir, dissim_path):
    cluster_data = []
    student_list = []
    student_output = []
    for student in student_vects:
        cluster_data.append(student_vects[student])
        student_output.append(str(student.id_num) + "," + str(student.grade_adj) + "," + str(student.age))
        student_list.append(student)

    # ms = MeanShift().fit_predict(cluster_data)
    # ward = AgglomerativeClustering(n_clusters=5, linkage='ward').fit_predict(cluster_data)
    # utils.list_to_file(base_dir+"/test_labels_"+request_type+"_"+vect_type, student_output)
    # utils.list_to_file("test_clusters_ms", ms)
    n_set = [5]
    # dissim_list = utils.list_from_file(dissim_path,"\n", ",", False)
    # dissim_dict = ca.format_dissim_list(dissim_list)

    for n in n_set:
        pred_clusters = KMeans(n_clusters=n).fit(cluster_data)
        analysis_set = ca.cluster_analysis(cluster_data, pred_clusters.labels_, student_list, dissim_dict)
        os.mkdir(base_dir + "/" + str(n) + "_run")
        for clust in analysis_set:
            ca.print_stats(analysis_set[clust], clust, base_dir + "/" + str(n) + "_run")
            utils.list_to_file("test_clusters_kmeans_" + str(n) + "_" + request_type + "_" + vect_type,
                               pred_clusters.labels_)

    # utils.list_to_file("test_labels_2_2"+vect_type+"_"+request_type+".csv", student_output)

    # af = AffinityPropagation().fit(cluster_data)
    # cluster_centers_indices = af.cluster_centers_indices_
    # labels = af.labels_

    # n_clusters_ = len(cluster_centers_indices)

    # print('Estimated number of clusters: %d' % n_clusters_)
    # print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    # print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    # print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    # print("Adjusted Rand Index: %0.3f"
    #      % metrics.adjusted_rand_score(labels_true, labels))
    # print("Adjusted Mutual Information: %0.3f"
    #      % metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, labels, metric='sqeuclidean'))
    utils.list_to_file("test_clusters_af_" + vect_type + "_" + request_type, af.labels_)
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, af.labels_))

    print("km 10")
    pred_clusters = KMeans(n_clusters=10).fit(cluster_data)
    utils.list_to_file("test_clusters_kmeans_10_" + vect_type + "_" + request_type, pred_clusters.labels_)
    print("Silhouette Coefficient: %0.3f"
          % metrics.silhouette_score(cluster_data, pred_clusters.labels_, metric='sqeuclidean'))
    print("DB Index: %0.3f"
          % metrics.davies_bouldin_score(cluster_data, pred_clusters.labels_))


def predict_course(classifier, query_student, query_seq, query_tu, prep_courses, **kwargs):
    prep_courses.sort()
    any_prior_course = query_student.course_seq_dict[query_seq-1][0]
    query_student_data = [query_seq,query_tu, any_prior_course.sfsu_units, any_prior_course.sfsu_gpa]
    for prep_course in prep_courses:
        query_student_data.append(query_student.unique_courses[prep_course].grade)
        query_student_data.append(query_student.unique_courses[prep_course].term_units)
        if "prior_ge" in kwargs:
            ge_count =0
            for course in query_student.course_history:
                if course.type == "ge" and course.seq_int < query_seq:
                    ge_count+=1
            query_student_data.append(ge_count)
        if "concurrent_ge" in kwargs:
            cge_count = 0
            course_list = query_student.course_seq_dict[query_seq]
            for course in course_list:
                if course.type == "ge":
                    cge_count += 1
            query_student_data.append(cge_count)
    pred_grade = classifier.predict(query_student_data)
    return pred_grade

def cluster_named(X, Y, n):
    cluster_dict = {}
    clusterer = KMeans(n_clusters=n, max_iter=500)
    # clusterer = AffinityPropagation()
    # clusterer = MeanShift()
    pred_clusters = clusterer.fit_predict(X)

    for x in range(0, len(pred_clusters)):
        result = pred_clusters[x]
        student = Y[x]
        student.pred = result
        student.pred_class = "cluster"
        utils.add_to_dict_list(result, student, cluster_dict)

    return cluster_dict
