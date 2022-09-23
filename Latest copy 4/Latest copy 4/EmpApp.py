from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import logging
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion


output = {}
table = 'employee'

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

@app.route("/", methods=['GET', 'POST'])
def home():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    cursor = db_conn.cursor()
    cursor.execute("select * from employee")
    data = cursor.fetchall()  # data from database
    return render_template('ViewSummary.html', value=data)

@app.route("/showaddemp", methods=['GET', 'POST'])
def showaddemp():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    return render_template('AddEmp.html')

@app.route("/showsummary", methods=['GET', 'POST'])
def showsummary():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    cursor = db_conn.cursor()
    cursor.execute("select * from employee")
    data = cursor.fetchall()  # data from database
    return render_template('ViewSummary.html', value=data)
    # return render_template('ViewSummary.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    fmno = request.form['fmno']
    name = request.form['name']
    contact = request.form['contact']
    team = request.form['team']
    location = request.form['location']
    certification = request.form['certification']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    if emp_image_file.filename == "":
       return "Please select a file"

    try:

        cursor.execute(insert_sql, (fmno, name,contact, team, location, certification))
        db_conn.commit()
        # # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "fmno-" + str(fmno) + "_image_file"
        s3 = boto3.resource('s3')

        try:
             print("Data inserted in MySQL RDS... uploading image to S3...")
             s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
             s3_location = (bucket_location['LocationConstraint'])

             if s3_location is None:
                 s3_location = ''
             else:
                 s3_location = '-' + s3_location

             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                 s3_location,
                 custombucket,
                 emp_image_file_name_in_s3)

        except Exception as e:
             return str(e)


    except Exception as e:
        print(e)
        logging.info(msg=e);

    finally:
        print("finally")

    cursor.execute("select * from employee")
    data = cursor.fetchall()  # data from database
    return render_template('ViewSummary.html', value=data)

###

@app.route("/deletemp", methods=['POST'])
def DeleteEmp():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    fmno = request.form['emp_id']
    delete_sql = "DELETE FROM employee WHERE fmno = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(delete_sql, (fmno))
        db_conn.commit()
        print("Data deleted from MySQL RDS... deleting image from S3...")
        emp_image_file_name_in_s3 = "emp-id-" + str(fmno) + "_image_file"
        s3 = boto3.resource('s3')
        s3.Object(custombucket, emp_image_file_name_in_s3).delete()

    finally:
        cursor.close()

    print("all modification done...")
    return "Deleted employee with id: " + fmno


@app.route("/getemp", methods=['POST', 'GET'])
def GetEmp():
    return render_template('GetEmp.html')


@app.route("/fetchdata", methods=['POST'])
def GetEmpOutput():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    fmno = request.form['fmno']
    select_sql = "SELECT * FROM employee WHERE fmno = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (fmno))
        db_conn.commit()
        print("Data fetched from MySQL RDS... fetching image from S3...")
        (fmno, name, contact, team, location, certification) = cursor.fetchone()

        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        # s3 = boto3.resource('s3')
        # s3.Bucket(custombucket).download_file(emp_image_file_name_in_s3, emp_image_file_name_in_s3)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetEmpOutput.html', fmno=fmno, name=name, contact=contact, team=team,
                           location=location, certification=certification)

####
##view record
@app.route("/viewAttendance", methods=['GET', 'POST'])
def showattendance():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    cursor = db_conn.cursor()
    cursor.execute("select * from attendance")
    data = cursor.fetchall()  # data from database
    return render_template('viewAttendance.html', value=data)
    # return render_template('ViewSummary.html')

###
#check in to work
@app.route("/addattendance", methods=['GET', 'POST'])
def showcheckin():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    return render_template('AddAttendance.html')

@app.route("/checkin", methods=['POST'])
def checkin():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    emp_id = request.form['emp_id']
    name = request.form['name']
    contact = request.form['contact']
    officeteam = request.form['officeteam']
    Branchlocation = request.form['Branchlocation']
    date = request.form['date']
    checkIn = request.form['checkIn']
    #emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    #if emp_image_file.filename == "":
     #  return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, name,contact, officeteam, Branchlocation, date, checkIn))
        db_conn.commit()
        # # Uplaod image file in S3 #
     #   emp_image_file_name_in_s3 = "fmno-" + str(emp_id) + "_image_file"
     #   s3 = boto3.resource('s3')

     #   try:
      #       print("Data inserted in MySQL RDS... uploading image to S3...")
       #      s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
       #      bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        #     s3_location = (bucket_location['LocationConstraint'])

         #    if s3_location is None:
          #       s3_location = ''
           #  else:
            #     s3_location = '-' + s3_location

             #object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
              #   s3_location,
               #  custombucket,
                # emp_image_file_name_in_s3)

       # except Exception as e:
        #     return str(e)


    except Exception as e:
        print(e)
        logging.info(msg=e);

    finally:
        print("finally")

    cursor.execute("select * from attendance")
    data = cursor.fetchall()  # data from database
    return render_template('viewAttendance.html', value=data)

#####
#search check in
@app.route("/getcheckin", methods=['POST', 'GET'])
def GetCheckIn():
    return render_template('GetCheckIn.html')

@app.route("/fetchcheckin", methods=['POST'])
def GetCheckInOutput():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    emp_id = request.form['emp_id']
    select_sql = "SELECT * FROM attendance WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        db_conn.commit()
        print("Data fetched from MySQL RDS... fetching image from S3...")
        (emp_id, name, contact, officeteam, BranchLocation, date, checkIn) = cursor.fetchone()

        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        # s3 = boto3.resource('s3')
        # s3.Bucket(custombucket).download_file(emp_image_file_name_in_s3, emp_image_file_name_in_s3)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetCheckInOutput.html', emp_id=emp_id, name=name, contact=contact, officeteam=officeteam,
                           BranchLocation=BranchLocation, date=date, checkIn=checkIn )


#############################################################

###
#submit leave
@app.route("/addleave", methods=['GET', 'POST'])
def showleave():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    return render_template('leaveForm.html')

@app.route("/leavesub", methods=['POST'])
def addleave():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    emp_id = request.form['emp_id']
    name = request.form['name']
    office = request.form['office']
    fdate = request.form['fdate']
    date = request.form['date']
    contact = request.form['contact']
    team = request.form['team']
    emp_image_file = request.files['emp_image_file']


    insert_sql = "INSERT INTO leaveEmployee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    if emp_image_file.filename == "":
       return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, name, office, fdate, date, contact, team))
        db_conn.commit()
        # # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "fmno-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
             print("Data inserted in MySQL RDS... uploading image to S3...")
             s3.Bucket(custombucket1).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
             bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket1)
             s3_location = (bucket_location['LocationConstraint'])

             if s3_location is None:
                 s3_location = ''
             else:
                 s3_location = '-' + s3_location

             object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                 s3_location,
                 custombucket,
                 emp_image_file_name_in_s3)

        except Exception as e:
             return str(e)


    except Exception as e:
        print(e)
        logging.info(msg=e);

    finally:
        print("finally")

    cursor.execute("select * from leaveEmployee")
    data = cursor.fetchall()  # data from database
    return render_template('viewLeave.html', value=data)

#####
#search check in
@app.route("/getleave", methods=['POST', 'GET'])
def GetLeave():
    return render_template('GetLeave.html')

@app.route("/fetchleave", methods=['POST'])
def Getleavet():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    emp_id = request.form['emp_id']
    select_sql = "SELECT * FROM leaveEmployee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id))
        db_conn.commit()
        print("Data fetched from MySQL RDS... fetching image from S3...")
        (emp_id, name, office, fdate, contact, team, date) = cursor.fetchone()

        # emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        # s3 = boto3.resource('s3')
        # s3.Bucket(custombucket).download_file(emp_image_file_name_in_s3, emp_image_file_name_in_s3)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetLeaveOutput.html', emp_id, name=name, office=office, fdate=fdate, date=date,
                           contact=contact, team=team)

##view record
@app.route("/viewleave", methods=['GET', 'POST'])
def showleave1():
    db_conn = connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
    cursor = db_conn.cursor()
    cursor.execute("select * from leaveEmployee")
    data = cursor.fetchall()  # data from database
    return render_template('viewLeave.html', value=data)
    # return render_template('ViewSummary.html')

##############################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)


