import numpy as np
global X_pool, y_pool, committee,cursor,cnx
import pandas as pd
from datetime import datetime, timedelta


def change_date_to_str(list):
    ans=[]
    for obj in list:
        if obj is None:
          ans.append(None)
        else:
            ans.append(obj.strftime('%Y%m%d'))
    return ans

def init_data():
    global cnx
    df = pd.read_sql('SELECT * FROM incoming_surgeries as I  WHERE Urgency is null', con=cnx)
    df['ArrivalDate'] = change_date_to_str(df['ArrivalDate'])
    df['PreOperation_DueDate'] = change_date_to_str(df['PreOperation_DueDate'])
    df['preSurgeryDate'] = change_date_to_str(df['preSurgeryDate'])
    df['Surgery_request_deadline']=change_date_to_str(df['Surgery_request_deadline'])
    df = df.drop(columns={'Urgency', 'Initial_scheduling_gap'})
    df = df.fillna(value=0)
    df = pd.get_dummies(df, columns={'OperationType'})

    return np.array(df.values), list(df.columns)


def init(mycursor,mycnx):
    global X_pool, y_pool, committee, cursor,cnx
    cursor = mycursor
    cnx = mycnx
    X_pool, col_names = init_data()

    # initialize the learner
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.ensemble import RandomForestClassifier
    from modAL.models import ActiveLearner

    # initializing Committee members
    knn = KNeighborsClassifier(n_neighbors=3)
    forest = RandomForestClassifier()
    ann = MLPClassifier(max_iter=5000)
    models = (knn, forest, ann)
    learner_list = list()

    # Isolate our examples for our labeled dataset.
    n_labeled_examples = X_pool.shape[0]
    training_indices = np.random.choice(range(n_labeled_examples), 3, replace=False)

    X_train = X_pool[training_indices]

    user_answers=[]
    for sample in X_train:
        print_surgery_details(sample)
        user_input = int(input())

        user_answers.append(user_input)
        sql = "UPDATE incoming_surgeries SET Urgency = %s  WHERE MS_Nituah=%s" % (user_input, sample[0])
        cursor.execute(sql)
        cnx.commit()
    X_pool = np.delete(X_pool, training_indices, axis=0)

    for model in models:
        # initializing learner
        learner = ActiveLearner(estimator=model,X_training=X_train, y_training=user_answers)
        learner_list.append(learner)

    # assembling the committee
    from modAL import Committee
    committee = Committee(learner_list=learner_list)


def active(max_queries = np.inf):
    global X_pool, committee,cursor,cnx
    from modAL.uncertainty import classifier_uncertainty

    N_QUERIES = 0
    while len(X_pool) > 0 and N_QUERIES < max_queries:

        query_idx, query_inst = committee.query(X_pool=X_pool)
        uncertainty = classifier_uncertainty(committee, query_inst.reshape(1, -1))
        X = X_pool[query_idx].reshape(1, -1)

        if uncertainty >= 0.3:
            # ask user
            N_QUERIES+=1
            print_surgery_details(X[0])
            user_input = int(input())
            y = np.array(user_input).reshape(1, )
            committee.teach(X=X, y=y)

            sql = "UPDATE incoming_surgeries SET Urgency = %s  WHERE MS_Nituah= %s " % (y[0], X[0][0])
            if user_input:
                N_QUERIES += 1
                ask_for_Initial_scheduling_gap(user_input, X)


        else:
            # predict
            y = committee.predict(X)
            sql = "UPDATE incoming_surgeries SET Urgency = %s  WHERE MS_Nituah= %s " % (y[0], X[0][0])
            if y==1:
                N_QUERIES += 1
                print("\nfor surgery -\n"
                      "MS_Nituah:  %s\n"
                      "PID: %s\n"
                      % (X[0][0], X[0][1]))
                ask_for_Initial_scheduling_gap(y, X)

        cursor.execute(sql)
        cnx.commit()
        X_pool = np.delete(X_pool, query_idx, axis=0)



def ask_for_Initial_scheduling_gap(urgency, X):
    global cursor
    if urgency:
        print('Is there a deadline for surgery request?  (X coming  days) \n'
              'if yes- enter a number for X '
              'if there is no need- enter (-1)')
        user_input2 = int(input())
        y2 = np.array(user_input2).reshape(1, )

        sql2 = "UPDATE incoming_surgeries SET Initial_scheduling_gap = %s  WHERE MS_Nituah= %s " % (y2[0], X[0][0])
        cursor.execute(sql2)

        if user_input2 != -1:
            today = datetime.today().date()
            deadline_date = (today + timedelta(days=user_input2)).strftime('%Y-%m-%d')
            sql3 = "UPDATE incoming_surgeries SET Surgery_request_deadline = '%s'  WHERE MS_Nituah= %s " % (
            deadline_date, X[0][0])
            cursor.execute(sql3)
    else:
        sql2 = "UPDATE incoming_surgeries SET Initial_scheduling_gap = %s   WHERE MS_Nituah= %s " % (-1, X[0][0])
        cursor.execute(sql2)



def print_surgery_details(sample):

    print("\nfor surgery details-\n"
          "MS_Nituah:  %s\n" 
          "PID: %s\n"
        "Would you define this surgery as urgent?\n"
              "press (1 to Yes, 0 to No)" % (sample[0], sample[1]))
