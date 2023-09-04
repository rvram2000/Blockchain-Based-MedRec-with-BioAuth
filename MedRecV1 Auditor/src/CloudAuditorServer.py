from flask import Flask, request, render_template, redirect, url_for
import os
import pypyodbc
import hashlib
import json
from EHRRecordModel import EHRRecordModel
import ftplib
import pyAesCrypt
from os import stat, remove

app = Flask(__name__)

emailid = ""

@app.route("/")     
def index():
    return render_template('Login.html')

@app.route('/processLogin', methods=['POST'])
def processLogin():
    global emailid
    emailid= request.form['emailid']
    password= request.form['password']
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=MedRecV1;Uid=SA;Pwd=Beg@0!=1',
                             autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '"+emailid+"' AND password = '"+password+"' AND isCloudAuditor = 1"; 
    print(sqlcmd1)
   
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('Login.html', processResult="Invalid Credentials")
    return render_template('Dashboard.html')


@app.route("/Dashboard")
def Dashboard():
    return render_template('Dashboard.html')

@app.route("/AssetRegister")
def AssetRegister():
    return render_template('AssetRegister.html')

@app.route("/AuditListing")

def AuditListing():
    print("AuditListing Called")
    conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=MedRecV1;Uid=SA;Pwd=Beg@0!=1',
                             autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT ehrRecordID, effDate,  prescriptionFileName FROM EHRRecords WHERE isUploadedCloud = 1 AND isAudited = 0"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        
        
        row = EHRRecordModel(dbrow[0], dbrow[1], prescriptionFileName = dbrow[2])
        records.append(row)
    return render_template('AuditListing.html', records=records)


@app.route("/AuditOperation")
def AuditOperation():
    global msgText, msgType
    operation = request.args.get('operation')
    unqid = ""
    row = EHRRecordModel(0, "", "", "")
    conn3 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=MedRecV1;Uid=SA;Pwd=Beg@0!=1',
                             autocommit=True)
    cursor3 = conn3.cursor()
       
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=MedRecV1;Uid=SA;Pwd=Beg@0!=1',
                             autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT ehrRecordID, effDate, fileHashValue, prescriptionFileName FROM EHRRecords WHERE ehrRecordID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:
            ftp = ftplib.FTP('101.99.74.37', 'Student1','1Osk52#k')
            fileName = dbrow[3]
            print("fileName", fileName)
            ftp.retrbinary('RETR '+fileName+".blinded.sanitized", open('../../MedRecV1 Auditor/src/static/DOWNLOADED_FILES/'+fileName+".blinded.sanitized", 'wb').write, 1024*1024)
            print("FTP DONE")  # get the file
            ftp.quit()  # close file and FTP
            password = "WmZq4t7w!z%C&F)J"
            bufferSize = 64 * 1024
            try:
                with open(os.path.join('../../MedRecV1 Auditor/src/static/DOWNLOADED_FILES', fileName + ".blinded.sanitized"), "rb") as fIn:
                    with open(os.path.join('../../MedRecV1 Auditor/src/static/DOWNLOADED_FILES', fileName + ".blinded"), "wb") as fOut:
                        encFileSize = stat(os.path.join('../../MedRecV1 Auditor/src/static/DOWNLOADED_FILES', fileName + ".blinded.sanitized")).st_size
                        print("encFileSize", encFileSize)
                        pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize, encFileSize)
                hasher = hashlib.md5()
                with open(os.path.join('../../MedRecV1 Auditor/src/static/DOWNLOADED_FILES', fileName + ".blinded"), "rb") as afile:
                    buf = afile.read()
                    hasher.update(buf)
                currentHashValue = hasher.hexdigest()
                print("currentHashValue", currentHashValue)
                print(dbrow[2], currentHashValue)
                isProblem = False
                if dbrow[2] != currentHashValue:
                    isProblem = True
                print(dbrow[2], currentHashValue)
                row = EHRRecordModel(dbrow[0],  dbrow[1], fileHashValue=dbrow[2], prescriptionFileName=dbrow[3] )
            
                return render_template('AuditOperation.html', row = row, operation=operation, currentHashValue=currentHashValue,isProblem=isProblem)
            except ValueError:
                row = EHRRecordModel(dbrow[0],  dbrow[1], fileHashValue=dbrow[2], prescriptionFileName=dbrow[3] )
                return render_template('AuditOperation.html', row = row, operation=operation, currentHashValue=hex(int(dbrow[2],16)*2),isProblem=True)
    return redirect(url_for("AuditListing"))

@app.route("/ProcessAuditOperation",methods = ['POST'])
def ProcessAuditOperation():



    unqid = request.form['unqid'].strip()
    isProblem = request.form['isProblem'].strip()
    print()
    if isProblem == "True":
        isProblem = 1
    else:
        isProblem = 0
    conn1 = pypyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Port=1433;Integrated_Security=true;Database=MedRecV1;Uid=SA;Pwd=Beg@0!=1',
                             autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd = "UPDATE EHRRecords SET isAudited = 1, isProblem = '"+str(isProblem)+"' WHERE ehrRecordID = '"+unqid+"'" 

    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('EHRRecordListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("AuditListing"))

if __name__ == "__main__":
    app.run(port=9092)

