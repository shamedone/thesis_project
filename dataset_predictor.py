import pandas as pd
import numpy as np
import utils
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.feature_selection import RFECV, SelectKBest, f_classif, SelectPercentile
from sklearn.ensemble import GradientBoostingClassifier

def simplify_grade(grade):
    grade = int(grade)
    if grade > 89:
        return "A"
    elif grade > 79:
        return "B"
    elif grade > 69:
        return "C"
    elif grade > 59:
        return "D"
    else:
        return "F"

def simplify_grade_int(grade):
    grade = int(grade)
    if grade > 89:
        return 90
    elif grade > 79:
        return 80
    elif grade > 69:
        return 70
    elif grade > 59:
        return 50
    else:
        return 40

def simplify_grade_pf(grade):
    if grade in ["A", "B", "C"]:
        return 1
    else:
        return 0

def simplify_status(status):
    if "dropout" in status or "non" in status:
        return 0
    else:
        return 1


#create predictor test frame, target is the field that is to be predicted, and exclusive is T/F indicating if only
#to include students with all course fields
def create_predictor_data_frame(students, student_fields, course_fields, course_list, target, exclusive):  # cor_fields names
    columns = []
    all_data = []

    if "status" in student_fields:
        columns.append("status")
    if "sex" in student_fields:
        columns.append("sex")
    if "ethnicity" in student_fields:
        columns.append("ethnicity")
    if "resident_status" in student_fields:
        columns.append("resident_status")
    if "admin_decript" in student_fields:
        columns.append("admin_decript")
    if "prep_summary" in student_fields:
        columns.append("prepardness")

    if "total_college_count" in student_fields:
        columns.append("business_units")
        columns.append("education_units")
        columns.append("ethnic_studies_units")
        columns.append("health_and_social_sci_units")
        columns.append("interdiciplinary_units")
        columns.append("liberal_and_creative_units")
        columns.append("science_and_engineering_units")

    for course in course_list:
        columns.append(course + "_grade")
        for field in course_fields:
            columns.append(course + "_" + field)
            # columns.append(field+"_sfu")
            # columns.append(field+"_seq")
            # columns.append(field+"_prior_ges")
            # columns.append(field+"_conc_ge")

    for student in students:
        student_data = []
        if "CSC" in target and target.split("_")[0] not in student.unique_courses:
            continue
        use = True
        if "status" in student_fields:
            #if student.status == 'graduated_non_cs':
            #    student_data.append('graduated_cs')
            #else:
            student_data.append(simplify_status(student.status))
        if "sex" in student_fields:
            student_data.append(student.sex)
        if "ethnicity" in student_fields:
            student_data.append(student.ethnic)
        if "resident_status" in student_fields:
            student_data.append(student.resident_status)
        if "admin_descript" in student_fields:
            student_data.append(student.admin_descript)
        if "prep_summary" in student_fields:
            student_data.append(student.prep_assess_summary)

        if "total_college_count" in student_fields:
            try:
                student_data.append(student.units_by_college_totals["Business"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Education"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Ethnic Studies"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Health and Social Sci"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Interdisciplinary Studies"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Liberal and Creative Arts"])
            except KeyError:
                student_data.append(0)
            try:
                student_data.append(student.units_by_college_totals["Science and Engineering"])
            except KeyError:
                student_data.append(0)

        for course in course_list:
            try:
                crs = student.unique_courses[course]

                if "CSC" in target and crs.name in target:
                    #student_data.append(simplify_grade_pf(simplify_grade(crs.grade)))
                    student_data.append(simplify_grade_int(crs.grade))
                else:
                    student_data.append(crs.grade)

                if "tu" in course_fields:
                    student_data.append(crs.term_units)
                if "sfsu_u" in course_fields:
                    student_data.append(crs.sfsu_units)
                if "tech_u" in course_fields:
                    student_data.append(crs.tech_load)
                if "ge_u" in course_fields:
                    student_data.append(crs.ge_load)
                if "seq_int" in course_fields:
                    student_data.append(crs.seq_int)
                if "age" in course_fields:
                    student_data.append(crs.student_age)
                if "sfsu_gpa" in course_fields:
                    student_data.append(crs.sfsu_gpa)
                if "term_gpa" in course_fields:
                    student_data.append(crs.term_gpa)
                if "repeat" in course_fields:
                    student_data.append(crs.repeat)
                if "crs_bus_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Business"])
                    except KeyError:
                        student_data.append(0)
                if "crs_edu_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Education"])
                    except KeyError:
                        student_data.append(0)
                if "crs_ethnic_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Ethnic Studies"])
                    except KeyError:
                        student_data.append(0)
                if "crs_hss_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Health and Social Sci"])
                    except KeyError:
                        student_data.append(0)
                if "crs_inter_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Interdisciplinary Studies"])
                    except KeyError:
                        student_data.append(0)
                if "crs_lca_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Liberal and Creative Arts"])
                    except KeyError:
                        student_data.append(0)
                if "crs_cose_units" in course_fields:
                    try:
                        student_data.append(crs.course_focus_dict['college']["Science and Engineering"])
                    except KeyError:
                        student_data.append(0)

            except KeyError:
                if exclusive:
                    use = False
                for x in range(0, len(course_fields) + 1):
                    student_data.append(-999)
        if use:
            all_data.append(student_data)
    print("****")
    print(len(all_data))
    print("****")

    df = pd.DataFrame(np.asarray(all_data), columns=columns)

    return df

def kbase_target(df, target_name, course_fields):
    localDF = df.copy(deep=True)
    target = pd.DataFrame(localDF[target_name], columns=[target_name])
    drop_fields = [target_name]

    if "CSC" in target_name:  #indicates not a graduation prediction
        crs = target_name.split("_")[0]
        for field in course_fields:
            drop_fields.append(crs+"_"+field)
    localDF = localDF.drop(columns=drop_fields)

    selector = SelectKBest(f_classif)
    selector.fit(localDF, target)


    check = list(selector.scores_)
    pcheck = list(selector.pvalues_)
    output = [list(localDF.columns)]
    output.append(check)
    output.append(pcheck)

    return output

#tester class
def classify_tester(df, target_name, course_fields, cv):
    localDF = df.copy(deep=True)
    target = pd.DataFrame(localDF[target_name], columns=[target_name])
    drop_fields = [target_name]

    if "CSC" in target_name:  # indicates not a graduation prediction
        crs = target_name.split("_")[0]
        for field in course_fields:
            drop_fields.append(crs + "_" + field)
    localDF = localDF.drop(columns=drop_fields)

    if "status" in target_name:
        f1 = 'f1'
        pres = 'precision'
        recall = 'recall'
    else:
        f1 = 'f1_micro'
        pres = 'precision_micro'
        recall = 'recall_micro'

    target = target.to_numpy().astype(np.int).ravel()
    tester_classifier = GradientBoostingClassifier(n_estimators=300)
    # tester_preds = cross_val_predict(tester_classifier, preprocessing.scale(localDF), target.to_numpy().ravel(), cv=cv)
    # scores = cross_val_score(tester_classifier, preprocessing.scale(localDF), target.to_numpy().ravel(), cv=cv)
    rfecv = RFECV(estimator=tester_classifier, step=1, cv=cv, scoring='accuracy')
    tester_classifier = GradientBoostingClassifier(n_estimators=300)
    mod_df = rfecv.fit_transform(preprocessing.scale(localDF), target)
    tester_preds = cross_val_predict(tester_classifier, mod_df, target, cv=cv)
    scores = cross_val_score(tester_classifier, mod_df, target, cv=cv)
    tester_f1 = cross_val_score(tester_classifier, mod_df, target, cv=cv, scoring=f1)
    tester_precision = cross_val_score(tester_classifier, mod_df, target, cv=cv, scoring=pres)
    tester_recall = cross_val_score(tester_classifier, mod_df, target, cv=cv, scoring=recall)
    tester_confuse = confusion_matrix(target, tester_preds)
    print(scores)
    print(sum(scores) / len(scores))
    tester_recall = sum(tester_recall) / len(tester_recall)
    tester_precision = sum(tester_precision) / len(tester_precision)
    tester_f1 = sum(tester_f1) / len(tester_f1)
    tester_avg = sum(scores) / len(scores)
    tester_feats = rfecv.ranking_
    #tester_coeff = rfecv.estimator_.coef_[0]
    print(tester_precision)
    print(tester_recall)
    print(tester_f1)
    print(tester_avg)
    print(tester_feats)
    #print(tester_coeff)

    return



#Large tester class, currently set to run battery of four machine learning algorithms
#df is dataframe, cv is number of crossvalidations
def classify_target(df, target_name, course_fields, cv):
    """
    if clf == "nb":
        classifier = GaussianNB()
    elif clf == "svm":
        classifier = svm.SVC(kernel='poly', C=1.0)
    elif clf == "rf":
        classifier = RandomForestClassifier(n_estimators=125)
    elif clf == "mlp":
        classifier = MLPClassifier(solver='lbfgs', hidden_layer_sizes=200)
    else:
        print("no classifier specified")
        return
    """
    localDF = df.copy(deep=True)
    target = pd.DataFrame(localDF[target_name], columns=[target_name])
    drop_fields = [target_name]

    if "CSC" in target_name:  #indicates not a graduation prediction
        crs = target_name.split("_")[0]
        for field in course_fields:
            drop_fields.append(crs+"_"+field)
    localDF = localDF.drop(columns=drop_fields)


    if "status" in target_name:
        f1= 'f1'
        pres='precision'
        recall ='recall'
    else:
        f1= 'f1_micro'
        pres='precision_micro'
        recall ='recall_micro'

    #currently set to run each classifier twice, once to determine correct factors using RFECV, and then once again
    #using crossvalidation and the modified dataframe to produce the predictions.
    target = target.to_numpy().astype(np.int).ravel()
    lr_classifier = linear_model.LogisticRegression(max_iter=300)
    #lr_preds = cross_val_predict(lr_classifier, preprocessing.scale(localDF), target.to_numpy().ravel(), cv=cv)
    #scores = cross_val_score(lr_classifier, preprocessing.scale(localDF), target.to_numpy().ravel(), cv=cv)
    rfecv = RFECV(estimator=lr_classifier, step=1, cv=cv, scoring='accuracy')
    lr_classifier = linear_model.LogisticRegression(max_iter=300)
    mod_df = rfecv.fit_transform(preprocessing.scale(localDF), target)
    lr_preds = cross_val_predict(lr_classifier, mod_df, target, cv=cv)
    scores = cross_val_score(lr_classifier, mod_df, target, cv=cv)
    lr_f1 = cross_val_score(lr_classifier, mod_df, target, cv=cv,  scoring=f1)
    lr_precision = cross_val_score(lr_classifier, mod_df, target, cv=cv,  scoring=pres)
    lr_recall = cross_val_score(lr_classifier, mod_df, target, cv=cv,  scoring=recall)
    lr_confuse = confusion_matrix(target, lr_preds)
    print(scores)
    print(sum(scores)/len(scores))
    lr_recall = sum(lr_recall)/len(lr_recall)
    lr_precision = sum(lr_precision)/len(lr_precision)
    lr_f1 = sum(lr_f1)/len(lr_f1)
    lr_avg = sum(scores)/len(scores)
    lr_feats = rfecv.ranking_
    lr_coeff = rfecv.estimator_.coef_[0]


    rf_classifier = RandomForestClassifier(n_estimators=300)
    #rf_preds = cross_val_predict(rf_classifier, preprocessing.scale(localDF), target, cv=cv)
    #scores = cross_val_score(rf_classifier, preprocessing.scale(localDF), target, cv=cv)
    rfecv = RFECV(estimator=rf_classifier, step=1, cv=cv, scoring='accuracy')
    mod_df = rfecv.fit_transform(preprocessing.scale(localDF), target)
    rf_classifier = RandomForestClassifier(n_estimators=300)
    rf_preds = cross_val_predict(rf_classifier, mod_df, target, cv=cv)
    scores = cross_val_score(rf_classifier, mod_df, target, cv=cv)
    rf_f1 = cross_val_score(rf_classifier, mod_df, target, cv=cv,  scoring=f1)
    rf_precision = cross_val_score(rf_classifier, mod_df, target, cv=cv,  scoring=pres)
    rf_recall = cross_val_score(rf_classifier, mod_df, target, cv=cv,  scoring=recall)
    rf_confuse = confusion_matrix(target, rf_preds)
    print(scores)
    print(sum(scores) / len(scores))
    rf_recall = sum(rf_recall) / len(rf_recall)
    rf_precision = sum(rf_precision) / len(rf_precision)
    rf_f1 = sum(rf_f1) / len(rf_f1)
    rf_avg = sum(scores)/len(scores)
    rf_feats = rfecv.ranking_
    rf_coeff = rfecv.estimator_.feature_importances_


    svm_classifier = svm.SVC(kernel='linear', C=1.5)
    #svm_preds = cross_val_predict(svm_classifier, preprocessing.scale(localDF), target, cv=cv)
    #scores = cross_val_score(svm_classifier, preprocessing.scale(localDF), target, cv=cv)
    rfecv = RFECV(estimator=svm_classifier, step=1, cv=cv, scoring='accuracy')
    mod_df = rfecv.fit_transform(preprocessing.scale(localDF), target)
    svm_classifier = svm.SVC(kernel='linear', C=1.5)
    svm_preds = cross_val_predict(svm_classifier, mod_df, target, cv=cv)
    scores = cross_val_score(svm_classifier, mod_df, target, cv=cv)
    svm_f1 = cross_val_score(svm_classifier, mod_df, target, cv=cv,  scoring=f1)
    svm_precision = cross_val_score(svm_classifier, mod_df, target, cv=cv,  scoring=pres)
    svm_recall = cross_val_score(svm_classifier, mod_df, target, cv=cv,  scoring=recall)
    svm_confuse = confusion_matrix(target, svm_preds)
    print(scores)
    print(sum(scores) / len(scores))
    svm_recall = sum(svm_recall) / len(svm_recall)
    svm_precision = sum(svm_precision) / len(svm_precision)
    svm_f1 = sum(svm_f1) / len(svm_f1)
    svm_avg = sum(scores)/len(scores)
    svm_feats = rfecv.ranking_
    svm_coeff = rfecv.estimator_.coef_[0]


    #classifier = MLPClassifier(solver='lbfgs', hidden_layer_sizes=200, max_iter=1000)
    pc_classifier = linear_model.Perceptron(max_iter=1200)
    #mlp_predtemp = cross_val_predict(mlp_classifier, preprocessing.scale(localDF), target, cv=cv)
    #scores = cross_val_score(mlp_classifier, preprocessing.scale(localDF), target, cv=cv)
    rfecv = RFECV(estimator=pc_classifier, step=1, cv=cv, scoring='accuracy')
    pc_classifier = linear_model.Perceptron(max_iter=1200)
    mod_df = rfecv.fit_transform(preprocessing.scale(localDF), target)
    mlp_predtemp = cross_val_predict(pc_classifier, mod_df, target, cv=cv)
    scores = cross_val_score(pc_classifier, mod_df, target, cv=cv)
    mlp_f1 = cross_val_score(pc_classifier, mod_df, target, cv=cv,  scoring=f1)
    mlp_precision = cross_val_score(pc_classifier, mod_df, target, cv=cv,  scoring=pres)
    mlp_recall = cross_val_score(pc_classifier, mod_df, target, cv=cv,  scoring=recall)
    mlp_preds = [] #fix odd bug
    for x in mlp_predtemp:
        mlp_preds.append(int(x))
    mlp_confuse = confusion_matrix(target, mlp_preds)
    print(scores)
    print(sum(scores) / len(scores))
    mlp_recall = sum(mlp_recall) / len(mlp_recall)
    mlp_precision = sum(mlp_precision) / len(mlp_precision)
    mlp_f1 = sum(mlp_f1) / len(mlp_f1)
    mlp_avg = sum(scores)/len(scores)
    mlp_feats = rfecv.ranking_
    mlp_coeff = rfecv.estimator_.coef_[0]

    #rest of coude is just output processing
    lr_feat_output = process_feat_output(lr_feats, lr_coeff, localDF, "lr")
    rf_feat_output = process_feat_output(rf_feats, rf_coeff, localDF, "rf")
    svm_feat_output = process_feat_output(svm_feats, svm_coeff, localDF, "svm")
    mlp_feat_output = process_feat_output(mlp_feats, mlp_coeff, localDF, "mlp")
    print(lr_feats)
    print(lr_coeff)
    print(rf_feats)
    print(rf_coeff)
    print(svm_feats)
    print(svm_coeff)
    print(mlp_feats)
    print(mlp_coeff)


    #Edited out to match output for pass fail preds only.
    if "grade" in target_name:
        output = [[target_name+"_true_value", target_name+"_pf_true",
                   "svm_pred", "svm_check", "svm_pf_pred", "svm_pf_check",
                   "rf_pred", "rf_check", "rf_pf_pred", "rf_pf_check",
                   "mlp_pred", "mlp_check", "mlp_pf_pred", "mlp_pf_check",
                   "lr_pred", "lr_check", "lr_pf_pred", "lr_pf_check"]]
    #if "grade" in target_name:
    #    output = [[target_name+"_true_value", "svm_pred", "svm_check", "rf_pred", "rf_check", "mlp_pred", "mlp_check",
    #               "lr_pred", "lr_check"]]
    else:
        output = [[target_name+"_true_value", "svm_pred", "svm_check", "rf_pred", "rf_check", "mlp_pred", "mlp_check",
                   "lr_pred", "lr_check"]]

    answers = target

    ans_pf = [0] * len(answers)
    svm_pf_preds = [0] * len(svm_preds)
    rf_pf_preds = [0] * len(rf_preds)
    lr_pf_preds = [0] * len(lr_preds)
    mlp_pf_preds = [0] * len(mlp_preds)

    simp_answers = [0] * len(answers)
    simp_svm_preds = [0] * len(answers)
    simp_rf_preds = [0] * len(answers)
    simp_lr_preds = [0] * len(answers)
    simp_mlp_preds = [0] * len(answers)


    for x in range(0, len(answers)):
        svm_pf_check = '0'
        rf_pf_check = '0'
        lr_pf_check = '0'
        mlp_pf_check = '0'
        svm_check = '0'
        rf_check = '0'
        lr_check = '0'
        mlp_check = '0'

        if "grade" in target_name:
            simp_answers[x] = simplify_grade(answers[x])
            simp_svm_preds[x] = simplify_grade(svm_preds[x])
            simp_rf_preds[x] = simplify_grade(rf_preds[x])
            simp_lr_preds[x] = simplify_grade(lr_preds[x])
            simp_mlp_preds[x] = simplify_grade(mlp_preds[x])

            ans_pf[x] = simplify_grade_pf(simp_answers[x])
            svm_pf_preds[x] = simplify_grade_pf(simp_svm_preds[x])
            rf_pf_preds[x] = simplify_grade_pf(simp_rf_preds[x])
            lr_pf_preds[x] = simplify_grade_pf(simp_lr_preds[x])
            mlp_pf_preds[x] = simplify_grade_pf(simp_mlp_preds[x])


        if simp_svm_preds[x] == simp_answers[x]:
            svm_check = '1'
        if simp_rf_preds[x] == simp_answers[x]:
            rf_check = '1'
        if simp_lr_preds[x] == simp_answers[x]:
            lr_check = '1'
        if simp_mlp_preds[x] == simp_answers[x]:
            mlp_check = '1'


        if svm_pf_preds[x] == ans_pf[x]:
            svm_pf_check = '1'
        if rf_pf_preds[x] == ans_pf[x]:
            rf_pf_check = '1'
        if lr_pf_preds[x] == ans_pf[x]:
            lr_pf_check = '1'
        if mlp_pf_preds[x] == ans_pf[x]:
            mlp_pf_check = '1'



        #print(answers[x]+','+ans_pf[x]+str(svm_preds[x])+","+svm_check+","+str(rf_preds[x])+","+rf_check+","+str(mlp_preds[x])
        #      +","+mlp_check+","+str(lr_preds[x])+","+lr_check)
        #print(target)
        #Code below commented out due to reducing operation to binary yes/no. It is still functional under these
        #conditions, but produces junk output so no need to create possiblity for confusion.
        if "grade" in target_name:
            output.append([answers[x], ans_pf[x],
                           str(svm_preds[x]), svm_check, svm_pf_preds[x], svm_pf_check,
                           str(rf_preds[x]), rf_check, rf_pf_preds[x], rf_pf_check,
                           str(mlp_preds[x]),mlp_check, mlp_pf_preds[x], mlp_pf_check,
                           str(lr_preds[x]), lr_check, lr_pf_preds[x], lr_pf_check])
        #if "grade" in target_name:
        #    output.append([answers[x], str(svm_preds[x]), svm_check, str(rf_preds[x]), rf_check, str(mlp_preds[x]),
        #                   mlp_check, str(lr_preds[x]), lr_check])
        else:
            output.append([answers[x], str(svm_preds[x]), svm_check, str(rf_preds[x]), rf_check, str(mlp_preds[x]),
                           mlp_check, str(lr_preds[x]), lr_check])


    spacer = [" "]
    output[4].extend(spacer)
    output[5].extend(spacer)
    output[6].extend(spacer)
    output[7].extend(spacer)

    output[4].extend(["lr avg", lr_avg])
    output[5].extend(["rf avg", rf_avg])
    output[6].extend(["svm avg", svm_avg])
    output[7].extend(["mlp avg", mlp_avg])

    #rf_output = rf_feature_importance(localDF, target, target_name)
    feat_output = write_feat_output([lr_feat_output, rf_feat_output, svm_feat_output])
    feat_output.append([""])
    feat_output.append(localDF.columns)
    feat_output.append(["****"])
    feat_output.append(["lr"])
    feat_output.append([lr_avg])
    feat_output.append(lr_feats)
    feat_output.append(lr_coeff)
    feat_output.append(["lr precision", "lr_recall", "lr_f1"])
    feat_output.append([lr_precision, lr_recall, lr_f1])
    feat_output.append([""])
    feat_output.append(["lr", "Predicted_false", "Predictied_true"])
    feat_output.append(["true_false", lr_confuse[0][0], lr_confuse[0][1]])
    feat_output.append(["true_positive", lr_confuse[1][0], lr_confuse[1][1]])
    feat_output.append(["****"])
    feat_output.append(["rf"])
    feat_output.append([rf_avg])
    feat_output.append(rf_feats)
    feat_output.append(rf_coeff)
    feat_output.append(["rf precision", "rf_recall", "rf_f1"])
    feat_output.append([rf_precision, rf_recall, rf_f1])
    feat_output.append([""])
    feat_output.append(["rf","Predicted_false", "Predictied_true"])
    feat_output.append(["true_false", rf_confuse[0][0], rf_confuse[0][1]])
    feat_output.append(["true_positive", rf_confuse[1][0], rf_confuse[1][1]])
    feat_output.append(["****"])
    feat_output.append(["svm"])
    feat_output.append([svm_avg])
    feat_output.append(svm_feats)
    feat_output.append(svm_coeff)
    feat_output.append(["svm precision", "svm_recall", "svm_f1"])
    feat_output.append([svm_precision, svm_recall, svm_f1])
    feat_output.append([""])
    feat_output.append(["svm","Predicted_false", "Predictied_true"])
    feat_output.append(["true_false", svm_confuse[0][0], svm_confuse[0][1]])
    feat_output.append(["true_positive", svm_confuse[1][0], svm_confuse[1][1]])
    feat_output.append(["****"])
    feat_output.append(["mlp"])
    feat_output.append([mlp_avg])
    feat_output.append(mlp_feats)
    feat_output.append(mlp_coeff)
    feat_output.append(["mlp precision", "mlp_recall", "mlp_f1"])
    feat_output.append([mlp_precision, mlp_recall, mlp_f1])
    feat_output.append([""])
    feat_output.append(["mlp", "Predicted_false", "Predictied_true"])
    feat_output.append(["true_false", mlp_confuse[0][0], mlp_confuse[0][1]])
    feat_output.append(["true_positive", mlp_confuse[1][0], mlp_confuse[1][1]])

    return output, feat_output

#unused code for feature importance using Random forest
def rf_feature_importance(localDF, target, target_name):
    output = [["variable", "importance"]]
    lr_classifier = linear_model.LogisticRegression(max_iter=300)
    rf_classifier = RandomForestClassifier(n_estimators=400)
    svm_classifier = svm.SVC(kernel='linear', C=1.5)

    lr_classifier.fit(localDF, target[target_name])
    rf_classifier.fit(localDF, target[target_name])
    svm_classifier.fit(localDF, target[target_name])
    for x in range(0, len(localDF.columns)):
        #print(localDF.columns[x] + "," + str(classifier.feature_importances_[x]))
        output.append([localDF.columns[x], str(rf_classifier.feature_importances_[x])])
    return output

#returns header from processed dataframe for output
def process_feat_output(feats, coefs, df, name):
    output_header = [[name+"_feat", name+"_weight"]]
    i = 0
    output = []
    for x in range(0, len(feats)):
        if feats[x] == 1:
            output.append([df.columns[x], abs(coefs[i])])
            i+=1
    output.sort(reverse=True, key=lambda x: x[1])
    output_header.extend(output)
    return output_header

#takes output from predictions and processes it to CSV file
def write_feat_output(lists):
    max_len = 0
    master_counter = {}
    for y in lists:
        if len(y) > max_len:
            max_len = len(y)

    master_output =[[lists[0][0][0], lists[0][0][1], "", lists[1][0][0], lists[1][0][1], "", lists[2][0][0], lists[2][0][1]]]

    for x in range(1, max_len):
        output = []
        z = 0
        for y in range(0, len(lists)):
            temp_list = lists[y]
            try:
                output.append(temp_list[x][0])
                output.append(abs(temp_list[x][1]))
                utils.sum_to_dict(temp_list[x][0], 1, master_counter)
            except IndexError:
                output.append("")
                output.append("")
            z+=1
            output.append("")
        master_output.append(output)

    counter_output = []
    for key in master_counter:
        counter_output.append(str(key)+","+str(master_counter[key]))
        counter_output.sort(reverse=True, key=lambda x: x[1])
    master_output.append("")
    for x in counter_output:
        master_output.append([x])

    return master_output


