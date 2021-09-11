import pandas as pd
import mysql.connector
import AL_model
import time
from datetime import datetime, timedelta

global last_list_of_surgeries, durations
global cnx, cursor

def get_preferences():
    update_patients_age()
    update_waiting_time()
    update_pre_operation_due_date()
    update_schedule_summon_date()
    update_duration()

def update_patients_age():
    # find patient's details from DB dbo_req755_staticdemography
    global cursor,cnx
    sql ="SELECT d.BirthDate, i.PID FROM dbo_req755_staticdemography as d" \
         " join incoming_surgeries as i on d.PID=i.PID " \
         "WHERE i.Age is null "
    cursor.execute(sql)
    SQLresult = cursor.fetchall()

    # calculate age and update
    for x in SQLresult:
        bdate= datetime.strptime(x[0], '%d/%m/%Y')
        today = datetime.today()
        delta = round((today - bdate).days / 365, 1)
        update_age_sql= "UPDATE incoming_surgeries SET Age = %s WHERE PID = %s" % (delta, x[1])
        cursor.execute(update_age_sql)
    cnx.commit()


def update_waiting_time():
    #  take date arrival from DB
    global cursor,cnx
    today = datetime.today().date()
    sql = "SELECT ArrivalDate, MS_Nituah FROM incoming_surgeries"
    cursor.execute(sql)
    SQLresult = cursor.fetchall()

    # for each result, calculate waiting time (delta between today to data arrival)
    for x in SQLresult:
        arrivalDate = x[0]
        delta = (today - arrivalDate).days
        update_age_sql = "UPDATE incoming_surgeries SET WaitingTime = %s WHERE MS_Nituah = %s" % (delta,  x[1])
        cursor.execute(update_age_sql)
    cnx.commit()


def update_pre_operation_due_date(validity=60):
    # take Pre_Surgery_Date from DB
    global cursor,cnx
    sql = "SELECT Pre_Surgery_Date, PS.MS_Nituah " \
          "FROM dbo_req755_presurgeryfrombridgesystem as PS " \
          "join incoming_surgeries as ISS " \
          "on PS.MS_Nituah=ISS.MS_Nituah " \
          "WHERE Pre_Surgery_Date = " \
          "(SELECT min(Pre_Surgery_Date) FROM dbo_req755_presurgeryfrombridgesystem " \
          "WHERE ISS.MS_Nituah=MS_Nituah)"

    cursor.execute(sql)
    SQLresult = cursor.fetchall()
    cnx.commit()

    # for each result, calculate due date (Pre_Surgery_Date+ validity)
    for x in SQLresult:
        preSurgeryDate = datetime.strptime(x[0], '%d/%m/%Y').date()
        dueDate = preSurgeryDate + timedelta(days=validity)
        update_dueDate_sql = "UPDATE incoming_surgeries " \
                             "SET PreOperation_DueDate = '%s',preSurgeryDate = '%s'  WHERE MS_Nituah=%s " \
                             % (dueDate,preSurgeryDate, x[1])
        cursor.execute(update_dueDate_sql)
    cnx.commit()


def update_schedule_summon_date():
    # schedule_summon_date
    # the date that scheduled by the pre-surgery department (need to connect to Noa's Algorithm results)
    pass


def update_duration():
    global cursor,cnx, durations
    sql = "SELECT TypeOfSurgery, OperationType, MS_Nituah FROM incoming_surgeries WHERE Duration is null"
    cursor.execute(sql)
    SQLresult = cursor.fetchall()

    for x in SQLresult:
        typeOfSurgery = x[0]
        operationType = x[1]
        mS_Nituah = x[2]
        try:
            avg = durations[ (durations['Type_of_surgery'] == typeOfSurgery) & (durations['OperationType'] == operationType)]['avg'].item()
            sql2 = "UPDATE incoming_surgeries SET Duration = %s WHERE MS_Nituah = %s" % (avg,  mS_Nituah)
            cursor.execute(sql2)
        except: #there is no data for combination of: Type_of_surgery + OperationType
            pass # in this case the cell will stay empty

    cnx.commit()


def connect_sql():
    global cnx, cursor
    cnx= mysql.connector.connect(user='root', password='311330500',
                                  host='127.0.0.1',
                                  database='data',
                                  auth_plugin='mysql_native_password')

    cursor = cnx.cursor()



def get_surgeries():
    # get surgeriws list
    global last_list_of_surgeries
    last_list_of_surgeries = pd.read_excel(r"surgeries list.xlsx")

    # fill missing details
    # default fill : OperationType=0 , cancelations=0, TypeOfSurgery=0, ArrivalDate=today
    today= datetime.today().date()
    df = last_list_of_surgeries.fillna({'OperationType': 0, 'cancelations': 0, 'TypeOfSurgery':0, 'ArrivalDate':today})

    # insert data to sql
    sql = "INSERT IGNORE INTO incoming_surgeries " \
          "(MS_Nituah, PID,ArrivalDate, TypeOfSurgery, OperationType, cancelations) " \
          "VALUES ( %s,%s, %s,%s, %s, %s)"
    for index, row in df.iterrows():
        date = row['ArrivalDate'].strftime('%Y-%m-%d')
        val = (row['MS_Nituah'], row['PID'], date, row['TypeOfSurgery '], row['OperationType'], row['cancelations'])
        cursor.execute(sql, val)
    cnx.commit()
    print("data was inserted.")


def connect_AL_model():
    global cursor,cnx
    AL_model.init(cursor,cnx)

def take_durations():
    global durations
    durations = pd.read_excel(r"files/duration_data.xlsx", index_col=False)


def new_data_loaded ():
    # return: true in case there is a new data
    global last_list_of_surgeries
    list_of_surgeries = pd.read_excel(r"surgeries list.xlsx")
    data_frame_same = list_of_surgeries.equals(last_list_of_surgeries)
    return not data_frame_same

def finish():
    # for GUI- if user chose to close the system
    cursor.close()
    cnx.close()

def initialize():
    global last_list_of_surgeries
    last_list_of_surgeries = pd.DataFrame()
    connect_sql()
    take_durations()

    get_surgeries()
    get_preferences()
    connect_AL_model()
    AL_model.active(max_queries=7)

if __name__ == "__main__":

    initialize()
    while True:
        time.sleep(10)
        while(new_data_loaded()):
            get_surgeries()
            get_preferences()
            AL_model.active(max_queries=10)

    finish()






