from flask import Flask, request, session, render_template, make_response, redirect, url_for
from datetime import timedelta
import pypyodbc
import pyAesCrypt
from DoctorModel import DoctorModel
from PatientModel import PatientModel
from EHRRecordModel import EHRRecordModel
from UserModel import UserModel
import ftplib
import smtplib, ssl
import json
from web3 import Web3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

msgText = ""
msgType = ""
otp = ""
doc_email = ""

def verifyNonce(nonce):
    if nonce != "null":
        return 1
    return 0
    
@app.route("/")
def home():
    global msgText, msgType, otp, doc_email
    return render_template('Login.html')

@app.route("/DoctorLogin")
def home_doctor():
    global msgText, msgType, otp, doc_email
    return render_template('DoctorLogin.html')

@app.route("/test", methods=['GET'])
def test():
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[1]
    # Get stored abi and contract_address
    with open("data.json", 'r') as f:
        datastore = json.load(f)
        abi = datastore["abi"]
        contract_address = datastore["contract_address"]
    contract = w3.eth.contract(address=contract_address, abi=abi)
    contract.functions.setUser(
        "Ram","male"
    ).transact()
    user_data = contract.functions.getUser().call()
    print(user_data)
    contract.functions.addFiles(1,["hello","how","are"]).transact()
    files = contract.functions.getFiles(1).call()
    print(files)
    return 'Okay'

@app.route("/OTPGeneration", methods=['GET'])
def OTPGeneration():
    global doc_email, otp
    print(request)
    doc_email = request.args['email']
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1',autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Doctors WHERE emailid = '" + doc_email + "' ";
    print(sqlcmd1)
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if row:

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "nijamathan@gmail.com"  # Enter your address
        receiver_email = "rvram2000+1@gmail.com"  # Enter receiver address
        password = "harivishak"
        #input("Type your password and press enter: ")
        name = "Ram R V"
        otp = "54321"
        subject = "MedicalRecord Login"
        message_text = "Dear "+name+",\n\nYour MedicalRecord login OTP is: "+otp
        message = """From:<%s>\nTo:<%s>\nSubject:%s\n%s""" % (sender_email,receiver_email,subject,message_text)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)
            return 'OTP sent to mail id'

        except smtplib.SMTPException as e:
            print(e)
            return 'Error. Please try again'
    return 'Mail id not registered. Enter a valid one'


@app.route("/Dashboard", methods=['GET'])
def Dashboard():
    if 'username' in session:
        resp = make_response(render_template('Dashboard.html'))
        resp.headers["Cache-Control"] = "no-store"
        print(session.permanent)
        print(request.cookies)
        return resp
    return render_template('ErrorPage.html')


@app.route("/AuthenticateLogin", methods=['POST'])
def AuthenticateLogin():
    global msgText, msgType
    emailid = request.form['emailid']
    password = request.form['password']
    nonce = request.form['nonce']
    if(not verifyNonce(nonce)):
        return '<h3>Blockchain verification failed. Please try again <a href =/>Login</a></h3>'

    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '"+emailid+"' AND password = '"+password+"'";
    print(sqlcmd1)
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if row:
        session.new = True
        session['username'] = emailid
        print(request.form)
        if 'remember' in request.form:
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=2)
            print('yes')
        else:
            session.permanent = True
            app.permanent_session_lifetime = timedelta(seconds=10)
        return redirect("/Dashboard")
    return render_template('ErrorPage.html')

@app.route("/AuthenticateDoctorLogin", methods=['POST'])
def AuthenticateDoctorLogin():
    global otp, doc_email
    emailid = request.form['emailid']
    OTP = request.form['otp']
    nonce = request.form['nonce']
    if(not verifyNonce(nonce)):
        return '<h3>Blockchain verification failed. Please try again <a href =/>Login</a></h3>'
    print(request.form)
    print(otp+doc_email)
    if (emailid == doc_email) and (otp == OTP):
        session.new = True
        session['username'] = emailid
        print(request.form)
        if 'remember' in request.form:
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=2)
            print('yes')
        else:
            session.permanent = True
            app.permanent_session_lifetime = timedelta(seconds=10)
        return redirect("/Dashboard")
    return '<h3>Incorrect Details. Please try again <a href =/DoctorLogin>Login</a></h3>'

@app.route("/LogOut", methods=['GET'])
def LogOut():
    session.pop('username', None)
    return render_template('Login.html')


@app.route("/UserListing")

def UserListing():
    global msgText, msgType
    print("UserListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
        records.append(row)
    if 'username' in session:
        return render_template('UserListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')



@app.route("/UserOperation")
def UserOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = UserModel(0, "", "", "")
    
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Users WHERE userID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            print("dbrow[0]", dbrow[0])
            row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
    if 'username' in session:
        return render_template('UserOperation.html', row = row, operation=operation )
    return render_template('ErrorPage.html')


@app.route("/ProcessUserOperation",methods = ['POST'])
def ProcessUserOperation():
    global msgText, msgType
    print(request.form)
    operation = request.form['operation']
    isCloudAuditor = 0
    if operation != "Delete" :
        print('OKKK')
        emailid= request.form['emailid']
        password= request.form['password']
        if request.form.get("isCloudAuditor") != None :
            isCloudAuditor = 1

    unqid = request.form['unqid'].strip()
    
    
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    

    if operation == "Create" :
        sqlcmd = "INSERT INTO Users (emailid, password, isCloudAuditor) VALUES('"+emailid+"', '"+password+"', '"+str(isCloudAuditor)+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Users SET emailid = '"+emailid+"', password = '"+password+"', isCloudAuditor = '"+str(isCloudAuditor)+"' WHERE userID = '"+unqid+"'"
    if operation == "Delete" :
        sqlcmd = "DELETE FROM Users WHERE userID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('UserListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("UserListing"))
    return render_template('ErrorPage.html')





@app.route("/DoctorListing")

def DoctorListing():
    global msgText, msgType
    print("DoctorListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT doctorID, doctorName, specialization, contactnbr FROM Doctors WHERE doctorName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = DoctorModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3])
        records.append(row)
    if 'username' in session:
        return render_template('DoctorListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')


@app.route("/DoctorOperation")
def DoctorOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = DoctorModel(0, "", "", "")
    row = None
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Doctors WHERE doctorID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = DoctorModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5])
    if 'username' in session:
        return render_template('DoctorOperation.html', row = row, operation=operation )
    return render_template('ErrorPage.html')


'''
This route will be called when the processUploadImage will be clicked (ie the inner page) is called from the browser.
This means that when the processUploadImage url is triggered (means clicking the submit button) processUploadData method is called.

'''

@app.route("/ProcessDoctorOperation",methods = ['POST'])
def ProcessDoctorOperation():
    global msgText, msgType
    operation = request.form['operation']
    if operation != "Delete" :
        doctorname= request.form['doctorName']
        specialization= request.form['specialization']
        contactNbr= request.form['contactNbr']
        emailID= request.form['emailID']
        address= request.form['address']

    
    unqid = request.form['unqid'].strip()
    
    
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    
    
    if operation == "Create" :
        sqlcmd = "INSERT INTO Doctors (doctorname, specialization, contactNbr,  emailID, address) VALUES('"+doctorname+"', '"+specialization+"', '"+contactNbr+"', '"+emailID+"', '"+address+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Doctors SET doctorname = '"+doctorname+"', specialization = '"+specialization+"', contactNbr = '"+contactNbr+"', emailID = '"+emailID+"', address = '"+address+"' WHERE doctorID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM Doctors WHERE doctorID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('DoctorListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("DoctorListing"))
    return render_template('ErrorPage.html')



@app.route("/PatientListing")

def PatientListing():
    global msgText, msgType
    print("PatientListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT patientID, patientName, doctorID, disease, contactNbr, emailID, address FROM Patients WHERE patientName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[2])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
        
        row = PatientModel(dbrow[0], dbrow[1], doc, dbrow[3], dbrow[4], dbrow[5], dbrow[6])
        records.append(row)
    if 'username' in session:
        return render_template('PatientListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')


@app.route("/PatientOperation")
def PatientOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    doc = DoctorModel(0, "")
    row = PatientModel(0, "", doc, "")
    doctors = []
    conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor3 = conn3.cursor()
    sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors ORDER BY doctorName"
    cursor3.execute(sqlcmd3)
        
    while True:
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
            doctors.append(doc)
        else:
            break
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT patientID, patientName, doctorID, disease, contactNbr, emailID, address FROM Patients WHERE patientID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            print("dbrow[5]", dbrow[5])
            
            conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
            cursor3 = conn3.cursor()
            sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[2])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                doc = DoctorModel(dbrow3[0], dbrow3[1])
            row = PatientModel(dbrow[0], dbrow[1], doc, dbrow[3], dbrow[4], dbrow[5], dbrow[6])
        
        
    if 'username' in session:
        return render_template('PatientOperation.html', row = row, operation=operation, doctors=doctors )
    return render_template('ErrorPage.html')


'''
This route will be called when the processUploadImage will be clicked (ie the inner page) is called from the browser.
This means that when the processUploadImage url is triggered (means clicking the submit button) processUploadData method is called.

'''

@app.route("/ProcessPatientOperation",methods = ['POST'])
def ProcessPatientOperation():
    global msgText, msgType
    operation = request.form['operation']
    if operation != "Delete" :
        patientName= request.form['patientName']
        doctorID= request.form['doctorID']
        disease= request.form['disease']
        contactNbr= request.form['contactNbr']
        emailID= request.form['emailID']
        address= request.form['address']

    
    unqid = request.form['unqid'].strip()
    
    
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    
    
    if operation == "Create" :
        sqlcmd = "INSERT INTO Patients (patientName, doctorID, disease, contactNbr, emailID, address) VALUES('"+patientName+"','"+doctorID+"',  '"+disease+"', '"+contactNbr+"', '"+emailID+"', '"+address+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Patients SET patientName = '"+patientName+"', doctorID = '"+doctorID+"', disease = '"+disease+"', contactNbr = '"+contactNbr+"', emailID = '"+emailID+"', address = '"+address+"' WHERE patientID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM Patients WHERE patientID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('PatientListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("PatientListing"))
    return render_template('ErrorPage.html')



@app.route("/EHRRecordListing")

def EHRRecordListing():
    global msgText, msgType
    print("EHRRecordListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT ehrRecordID, effDate, EHRRecords.doctorID, EHRRecords.patientID,  EHRRecords.disease,prescriptionFileName, isBlindedFileGenerated FROM EHRRecords INNER JOIN Patients ON Patients.patientID = EHRRecords.patientID WHERE patientName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
    
        conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[2])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
        
        conn4 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor4 = conn4.cursor()
        sqlcmd4 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[3])+"'"
        cursor4.execute(sqlcmd4)
        dbrow4 = cursor4.fetchone()
        if dbrow4:
            pat = PatientModel(dbrow4[0], dbrow4[1])
        row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], isBlindedFileGenerated = dbrow[6])
        records.append(row)
    if 'username' in session:
        return render_template('EHRRecordListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')


@app.route("/EHRRecordOperation")
def EHRRecordOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = EHRRecordModel(0, "", "", "")
    
    conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor3 = conn3.cursor()
    sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors ORDER BY doctorName"
    cursor3.execute(sqlcmd3)
    doctors = []
    while True:
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
            doctors.append(doc)
        else:
            break
    
    sqlcmd3 = "SELECT patientID, patientName FROM Patients ORDER BY patientName"
    cursor3.execute(sqlcmd3)
    patients = []
    while True:
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            pat = PatientModel(dbrow3[0], dbrow3[1])
            patients.append(pat)
        else:
            break
        
        
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            
            sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                doc = DoctorModel(dbrow3[0], dbrow3[1])
            
            sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                pat = PatientModel(dbrow3[0], dbrow3[1])
            
            row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5], dbrow[6])
        
    if 'username' in session:
        return render_template('EHRRecordOperation.html', row = row, operation=operation, doctors=doctors, patients=patients )
    return render_template('ErrorPage.html')




@app.route("/ProcessEHRRecordOperation",methods = ['POST'])
def ProcessEHRRecordOperation():
    global msgText, msgType
    print("1111")
    operation = request.form['operation']
    isBlindedFileGenerated = request.form['isBlindedFileGenerated'].strip()
    if isBlindedFileGenerated == "True":
        return redirect(url_for("EHRRecordListing"))
    if operation != "Delete" :
        effDate= request.form['effDate']
        patientID= request.form['patientID']
        doctorID= request.form['doctorID']
        disease= request.form['disease']


    unqid = request.form['unqid'].strip()
    
    prescriptionFileName = ""
    if len(request.files) != 0 :
        file = request.files['filetoupload']
        if file.filename != '':
            prescriptionFileName = file.filename
            f = os.path.join('static/UPLOADED_DATA', prescriptionFileName)
            file.save(f)
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    print("2222")
    
    if operation == "Create" :
        sqlcmd = "INSERT INTO EHRRecords (effDate, patientID, doctorID, disease, prescriptionFileName) VALUES('"+effDate+"', '"+str(patientID)+"','"+str(doctorID)+"',  '"+disease+"', '"+prescriptionFileName+"')"
    if operation == "Edit" :
        print("edit inside")
        if prescriptionFileName == "" :
            sqlcmd = "UPDATE EHRRecords SET effDate = '"+effDate+"', patientID = '"+str(patientID)+"', doctorID = '"+str(doctorID)+"', disease = '"+disease+"' WHERE ehrRecordID = '"+unqid+"'" 
        else:
            sqlcmd = "UPDATE EHRRecords SET effDate = '"+effDate+"', patientID = '"+str(patientID)+"', doctorID = '"+str(doctorID)+"', disease = '"+disease+"', prescriptionFileName = '"+prescriptionFileName+"' WHERE ehrRecordID = '"+unqid+"'" 
    if operation == "Delete" :
        sqlcmd = "DELETE FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'" 
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    print("3333")
    #return render_template('EHRRecordListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("EHRRecordListing"))
    return render_template('ErrorPage.html')


@app.route("/BlindedFileGenerationListing")

def BlindedFileGenerationListing():
    global msgText, msgType
    print("EHRRecordListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT ehrRecordID, effDate, EHRRecords.patientID, EHRRecords.doctorID, EHRRecords.disease, prescriptionFileName FROM EHRRecords INNER JOIN Patients ON Patients.patientID = EHRRecords.patientID WHERE isBlindedFileGenerated = 0 AND patientName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
            
        sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            pat = PatientModel(dbrow3[0], dbrow3[1])
        row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5])
        records.append(row)
    if 'username' in session:
        return render_template('BlindedFileGenerationListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')


@app.route("/BlindedFileGenerationOperation")
def BlindedFileGenerationOperation():
    global msgText, msgType
    unqid = ""
    row = EHRRecordModel(0, "", "", "")
    if True :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
            cursor3 = conn3.cursor()
            sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                doc = DoctorModel(dbrow3[0], dbrow3[1])
            
            sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                pat = PatientModel(dbrow3[0], dbrow3[1])
            row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5], dbrow[6], dbrow[7])
        
    if 'username' in session:
        return render_template('BlindedFileGenerationOperation.html', row = row)
    return render_template('ErrorPage.html')


@app.route("/ProcessBlindedFileGenerationOperation",methods = ['POST'])
def ProcessBlindedFileGenerationOperation():
    global msgText, msgType
    hprescriptionFileName = request.form['hprescriptionFileName']
    print("hprescriptionFileName", hprescriptionFileName)
    bufferSize = 64 * 1024
    password = "ZY7$FSk"
    with open(os.path.join('static/UPLOADED_DATA', hprescriptionFileName), "rb") as fIn:
        with open(os.path.join('static/UPLOADED_DATA', hprescriptionFileName+".blinded"), "wb") as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)
    unqid = request.form['unqid'].strip()

    hasher = hashlib.md5()
    with open(os.path.join('static/UPLOADED_DATA', hprescriptionFileName+".blinded"), "rb") as afile:
        buf = afile.read()
        hasher.update(buf)
    cryptohash = hasher.hexdigest()
    
        
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd = "UPDATE EHRRecords SET isBlindedFileGenerated = 1, fileHashValue= '"+cryptohash+"' WHERE ehrRecordID = '"+unqid+"'" 
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    print("3333")
    #return render_template('EHRRecordListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("BlindedFileGenerationListing"))
    return render_template('ErrorPage.html')


@app.route("/SanitizedFileGenerationListing")

def SanitizedFileGenerationListing():
    global msgText, msgType
    print("SanitizedFileGenerationListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT ehrRecordID, effDate, EHRRecords.patientID, EHRRecords.doctorID, EHRRecords.disease, prescriptionFileName FROM EHRRecords INNER JOIN Patients ON Patients.patientID = EHRRecords.patientID WHERE isBlindedFileGenerated = 1 AND isSanitizedFileGenerated = 0 AND patientName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
            
        sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            pat = PatientModel(dbrow3[0], dbrow3[1])
        row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5])
        records.append(row)
    if 'username' in session:
        return render_template('SanitizedFileGenerationListing.html', records=records, searchData=searchData)
    return render_template('ErrorPage.html')



@app.route("/SanitizedFileGenerationOperation")
def SanitizedFileGenerationOperation():
    global msgText, msgType
    unqid = ""
    row = EHRRecordModel(0, "", "", "")
    if True :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
            cursor3 = conn3.cursor()
            sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
            cursor3.execute(sqlcmd3)
            dbrow3 = cursor3.fetchone()
            if dbrow3:
                doc = DoctorModel(dbrow3[0], dbrow3[1])
            
                sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
                cursor3.execute(sqlcmd3)
                dbrow3 = cursor3.fetchone()
            if dbrow3:
                pat = PatientModel(dbrow3[0], dbrow3[1])
            row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5], dbrow[6], dbrow[7])
        
    if 'username' in session:
        return render_template('SanitizedFileGenerationOperation.html', row = row)
    return render_template('ErrorPage.html')


@app.route("/ProcessSanitizedFileGenerationOperation",methods = ['POST'])
def ProcessSanitizedFileGenerationOperation():
    global msgText, msgType
    hprescriptionFileName = request.form['hprescriptionFileName']
    print("hprescriptionFileName", hprescriptionFileName)
    bufferSize = 64 * 1024
    password = "K9I@#CDW"
    with open(os.path.join('static/UPLOADED_DATA', hprescriptionFileName+".blinded"), "rb") as fIn:
        with open(os.path.join('static/UPLOADED_DATA', hprescriptionFileName+".blinded.sanitized"), "wb") as fOut:
            pyAesCrypt.encryptStream(fIn, fOut, password, bufferSize)
    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd = "UPDATE EHRRecords SET isSanitizedFileGenerated = 1 WHERE ehrRecordID = '"+unqid+"'" 
    if sqlcmd == "" :
        return redirect(url_for('Error')) 
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    print("3333")
    #return render_template('EHRRecordListing.html', processResult="Success!!!. Data Uploaded. ")
    if 'username' in session:
        return redirect(url_for("SanitizedFileGenerationListing"))
    return render_template('ErrorPage.html')



@app.route("/SendToCloudListing")

def SendToCloudListing():
    global msgText, msgType
    print("SendToCloudListing Called")
    searchData = request.args.get('searchData')
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT ehrRecordID, effDate, EHRRecords.patientID, EHRRecords.doctorID, EHRRecords.disease, prescriptionFileName FROM EHRRecords INNER JOIN Patients ON Patients.patientID = EHRRecords.patientID WHERE isBlindedFileGenerated = 1 AND isSanitizedFileGenerated = 1 AND isUploadedCloud = 0 AND patientName like '%"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '"+str(dbrow[3])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])
            
        sqlcmd3 = "SELECT patientID, patientName FROM Patients WHERE patientID = '"+str(dbrow[2])+"'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            pat = PatientModel(dbrow3[0], dbrow3[1])
        row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], dbrow[5])
        records.append(row)

    if 'username' in session:
        return render_template('SendToCloudListing.html', records=records, searchData=searchData, msgText=msgText, msgType=msgType)
    return render_template('ErrorPage.html')




@app.route("/ProcessSendToCloudOperation")
def ProcessSendToCloudOperation():

    global msgText, msgType
    msgText = ""
    msgType = ""
    unqid = request.args.get('unqid').strip()

   
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor1 = conn1.cursor()
    sqlcmd1 = "SELECT ehrRecordID, prescriptionFileName FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'"
    cursor1.execute(sqlcmd1)
    dbrow1 = cursor1.fetchone()
    if dbrow1:
        fileName = dbrow1[1]
        if fileName != '':
            ftp = ftplib.FTP('101.99.74.37', 'Student1','1Osk52#k')
            print("fileName+.blinded.sanitized", fileName+".blinded.sanitized")
            ftp.storbinary('STOR '+fileName+".blinded.sanitized", open('static/UPLOADED_DATA/'+fileName+".blinded.sanitized", 'rb'))   # send the file                                   # close file and FTP
            ftp.quit()
            sqlcmd1 = "UPDATE EHRRecords SET isUploadedCloud = 1 WHERE ehrRecordID = '"+unqid+"'" 
            cursor1.execute(sqlcmd1)
    cursor1.commit()
    conn1.close()
    msgText="Uploaded to Cloud SuccessfEully"
    msgType="Success"
    if 'username' in session:
        return redirect(url_for("SendToCloudListing"))
    return render_template('ErrorPage.html')

@app.route("/Reports")
def ProcessReports():
    global msgText, msgType
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1', autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT COUNT(*) FROM EHRRecords"
    cursor.execute(sqlcmd1)
    noOfEHRRecords = 0
    
    dbrow = cursor.fetchone()
    if dbrow:
        noOfEHRRecords = dbrow[0]
    
    
    sqlcmd1 = "SELECT COUNT(*) FROM EHRRecords WHERE isBlindedFileGenerated = 1"
    cursor.execute(sqlcmd1)
    noOfBlindedFiles = 0
    
    dbrow = cursor.fetchone()
    if dbrow:
        noOfBlindedFiles = dbrow[0]
        
    sqlcmd1 = "SELECT COUNT(*) FROM EHRRecords WHERE isSanitizedFileGenerated = 1"
    cursor.execute(sqlcmd1)
    noOfSanitizedFiles = 0
    
    dbrow = cursor.fetchone()
    if dbrow:
        noOfSanitizedFiles = dbrow[0]
        
        noOfSanitizedFiles
    if 'username' in session:
        return render_template('Reports.html', noOfEHRRecords=noOfEHRRecords, noOfBlindedFiles=noOfBlindedFiles, noOfSanitizedFiles=noOfSanitizedFiles)
    return render_template('ErrorPage.html')

@app.route("/FrmCancel")
def FrmCancel():
    if 'username' in session:
        return render_template('Dashboard.html')
    return render_template('ErrorPage.html')


import os
import hashlib
import json
from Constants import connString

@app.route("/BlockChainGeneration")
def BlockChainGeneration():
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM EHRRecords WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    sqlcmd = "SELECT COUNT(*) FROM EHRRecords WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    if 'username' in session:
        return render_template('BlockChainGeneration.html', blocksCreated=blocksCreated, blocksNotCreated=blocksNotCreated)
    return render_template('ErrorPage.html')


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM EHRRecords WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    prevHash = ""
    print("blocksCreated", blocksCreated)
    if blocksCreated != 0:
        connx = pypyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM EHRRecords WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY ehrRecordID"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        print(2)
        if dbrowx:
            uniqueID = dbrowx[0]
            conny = pypyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT hash FROM EHRRecords WHERE ehrRecordID < '" + str(uniqueID) + "' ORDER BY ehrRecordID DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                print(3)
                prevHash = dbrowy[0]
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM EHRRecords WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY ehrRecordID"
    cursor.execute(sqlcmd)

    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[0])
        '''
        bdata = str(dbrow[1])+str(dbrow[2])+str(dbrow[3])+str(dbrow[4])+str(dbrow[5])+str(dbrow[6])+str(dbrow[7])+str(dbrow[8])+str(dbrow[9])\
                +str(dbrow[10])+str(dbrow[11])+str(dbrow[12])+str(dbrow[13])+str(dbrow[14])+str(dbrow[15])+str(dbrow[18])+str(dbrow[19])+str(dbrow[20])
        '''
        bdata = str(dbrow[1]) + str(dbrow[2]) + str(dbrow[3]) + str(dbrow[4])
        block_serialized = json.dumps(bdata, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()

        conn1 = pypyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE EHRRecords SET isBlockChainGenerated = 1, hash = '" + block_hash + "', prevHash = '" + prevHash + "' WHERE ehrRecordID = '" + unqid + "'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    if 'username' in session:
        return render_template('BlockchainGenerationResult.html')
    return render_template('ErrorPage.html')


@app.route("/BlockChainReport")
def BlockChainReport():
    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()

    sqlcmd1 = "SELECT * FROM EHRRecords WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd1)
    conn2 = pypyodbc.connect(connString, autocommit=True)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break

        conn3 = pypyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1',
            autocommit=True)
        cursor3 = conn3.cursor()
        sqlcmd3 = "SELECT doctorID, doctorName FROM Doctors WHERE doctorID = '" + str(dbrow[3]) + "'"
        cursor3.execute(sqlcmd3)
        dbrow3 = cursor3.fetchone()
        if dbrow3:
            doc = DoctorModel(dbrow3[0], dbrow3[1])

        conn4 = pypyodbc.connect(
            'Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=IndentityBasedIntegrityAuditingV1;Uid=SA;Pwd=Beg@0!=1',
            autocommit=True)
        cursor4 = conn4.cursor()
        sqlcmd4 = "SELECT patientID, patientName FROM Patients WHERE patientID = '" + str(dbrow[2]) + "'"
        cursor4.execute(sqlcmd4)
        dbrow4 = cursor4.fetchone()
        if dbrow4:
            pat = PatientModel(dbrow4[0], dbrow4[1])
        row = EHRRecordModel(dbrow[0], dbrow[1], pat, doc, dbrow[4], isBlindedFileGenerated=dbrow[6], hash=dbrow[12], prevHash=dbrow[13], isBlockChainGenerated=dbrow[14])
        records.append(row)

    if 'username' in session:
        return render_template('BlockChainReport.html', records=records)
    return render_template('ErrorPage.html')
if __name__ == "__main__":
    app.run(port=9091)
