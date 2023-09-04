class EHRRecordModel:
    # instance attribute
    def __init__(self, ehrRecordID, effDate, patient=None, doctor =None, disease="", prescriptionFileName = "", isBlindedFileGenerated=0, isSanitizedFileGenerated=0, isAudited=0, fileHashValue=""):
        self.ehrRecordID = ehrRecordID
        self.effDate = effDate
        self.patient = patient
        self.doctor = doctor
        self.disease = disease
        self.prescriptionFileName = prescriptionFileName
        self.isBlindedFileGenerated = isBlindedFileGenerated
        self.isSanitizedFileGenerated = isSanitizedFileGenerated
        self.isAudited = isAudited
        self.fileHashValue = fileHashValue