import json
from flask import Flask
from flask import request
import sqlite3


# Setting the connection within a global variable
conn = sqlite3.connect('notable.db')


# Creating dummy data within SQLLite DB for interaction through APIs
def setup():
    conn.execute('''drop table APPOINTMENTS''')
    conn.execute('''CREATE TABLE APPOINTMENTS
     (PHYSICIAN TEXT,
     TIME TEXT,
     DATE TEXT,
     TYPE TEXT,
     PATIENT TEXT);''')

    conn.execute("DELETE FROM APPOINTMENTS;")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
  VALUES ('DR.SMITH', '08:15 AM', '2022-01-05', 'FOLLOW-UP', 'HARRY STYLES');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.BRETT', '10:15 AM', '2022-06-02', 'NEW', 'ROBERTO CARLOS');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.MATHUR', '12:15 PM', '2022-07-15', 'FOLLOW-UP', 'TOM HANKS');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.JOSH', '1:15 AM', '2021-12-15', 'NEW', 'OLIVIA NELSON');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.PALANKAR', '11:15 AM', '2021-05-15', 'FOLLOW-UP', 'JOHN DENVER');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.PALANKAR', '11:15 AM', '2021-05-15', 'NEW', 'JOHN OLIVER');")

    conn.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
          VALUES ('DR.PALANKAR', '11:15 AM', '2021-05-15', 'FOLLOW-UP', 'OLGA RICHARDSON');")

    conn.commit()
    print('Records created successfully')


app = Flask(__name__)
setup()


# Get all appointments
@app.route('/getAllAppointments/', methods=['GET'])
def getAllAppointments():
    conn_ = sqlite3.connect('notable.db')
    doctor = request.args.get('doctor_name')
    date = request.args.get('date')
    records = conn_.execute("SELECT * FROM APPOINTMENTS where PHYSICIAN = '" + doctor + "' and DATE = '" + date + "'")
    field_name_1 = "Doctor\'s Name:"
    field_name_2 = "Appointment Time:"
    field_name_3 = "Date:"
    field_name_4 = "Type:"
    field_name_5 = "Patient\'s Name:"
    out = {}
    res = ''
    for row in records:
        out[field_name_1] = row[0]
        out[field_name_2] = row[1]
        out[field_name_3] = row[2]
        out[field_name_4] = row[3]
        out[field_name_5] = row[4]

        res += ''.join(str(json.dumps(out, indent=4)))
    conn_.close()
    return res


# Create newer appointment
@app.route('/createAppointment/', methods=['POST'])
def createAppointment():
    conn_ = sqlite3.connect('notable.db')
    doctor = request.args.get('doctor_name')
    date = request.args.get('date')
    time = request.args.get('time')

    minutes = int(time.split(' ')[0].split(':')[1]) % 15

    # Validation for valid appointments
    if minutes != 0:
        return "Invalid appointment time selected. Please choose 15min intervals example : 8:15 AM "

    patient = request.args.get('patient')
    records = conn_.execute("SELECT count(*) FROM APPOINTMENTS where PHYSICIAN = '" + doctor + "' and DATE = '" + date + "' and TIME = '" + time + "'")
    c = 0

    # Check if doctor is available, max 3 appointments
    for p in records:
        if p[0] == 3:
            conn_.close()
            return "No appointments are available at the given time"

    # Check if patient already has an appointment during the same time
    records = conn_.execute("SELECT count(*) FROM APPOINTMENTS where PHYSICIAN = '" + doctor + "' and DATE = '" + date + "' and TIME = '" + time + "' and PATIENT = '" + patient + "'")
    for p in records:
        if p[0] >= 1:
            conn_.close()
            return "Patients appointment is already scheduled"

    # Check if existing patient
    patient_list = conn_.execute("SELECT DISTINCT PATIENT FROM APPOINTMENTS where PHYSICIAN = '" + doctor + "'")

    msg = ''
    for p in patient_list:
        if p[0] == patient:
            conn_.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
      VALUES ('" + doctor + "', '" + time + "', '" + date + "', 'FOLLOW-UP', '" + patient + "');")
            msg = 'Follow up appointment scheduled for existing patient: ' + patient
            break
        else:
            conn_.execute("INSERT INTO APPOINTMENTS (PHYSICIAN, TIME, DATE, TYPE, PATIENT) \
      VALUES ('" + doctor + "', '" + time + "', '" + date + "', 'NEW', '" + patient + "');")
            msg = 'New appointment created for ' + patient
            break

    conn_.commit()
    conn_.close()
    return msg


# Delete an existing appointment
@app.route('/deleteAppointment/', methods=['DELETE'])
def deleteAppointment():
    conn_ = sqlite3.connect('notable.db')
    doctor = request.args.get('doctor_name')
    date = request.args.get('date')
    time = request.args.get('time')
    patient = request.args.get('patient')

    # Check if appointment exists which needs to be deleted
    records = conn_.execute("select count(*) from APPOINTMENTS where PHYSICIAN = '" + doctor + "' and DATE = '" + date + "' and TIME = '" + time + "' and PATIENT = '" + patient + "'")
    for p in records:
        if p[0] == 0:
            conn_.close()
            return patient + ' does not have an appointment to cancel'

    # Delete appointment
    conn_.execute("DELETE FROM APPOINTMENTS where PHYSICIAN = '" + doctor + "' and DATE = '" + date + "' and TIME = '" + time + "' and PATIENT = '" + patient + "'")
    conn_.commit()
    conn_.close()
    return patient + '\'s appointment with ' + doctor + ' on ' + date + ' at ' + time + ' has been cancelled.'


# Get list of all doctors/physicians
@app.route('/getAllPhysicians/', methods=['GET'])
def getAllPhysicians():
    conn_ = sqlite3.connect('notable.db')
    records = conn_.execute('SELECT distinct PHYSICIAN FROM APPOINTMENTS')
    field_name_1 = "Physician\'s Name:"
    out = {}
    res = ''
    for row in records:
        out[field_name_1] = row[0]

        res += ''.join(str(json.dumps(out, indent=4)))

    conn_.close()
    return res


# Home page
@app.route("/")
def homePage():
    return "Welcome to the Notable Hospital Web UI"


# Running the Flask Application
app.run()
