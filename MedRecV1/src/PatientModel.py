class PatientModel:
    # instance attribute
    def __init__(self, patientID, patientName, doctor =None, disease="", contactNbr = "", emailID="", address="", reportFileName=""):
        self.patientID = patientID
        self.patientName = patientName
        self.doctor = doctor
        self.disease = disease
        self.contactNbr = contactNbr
        self.emailID = emailID
        self.address = address
        self.reportFileName = reportFileName