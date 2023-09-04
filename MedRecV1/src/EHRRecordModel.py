class EHRRecordModel:
    # instance attribute
    def __init__(self, ehrRecordID, effDate, patient=None, doctor =None, disease="", prescriptionFileName = "", isBlindedFileGenerated=0, isSanitizedFileGenerated=0, isUploadedCloud=0, hash="", prevHash="", isBlockChainGenerated=0):
        self.ehrRecordID = ehrRecordID
        self.effDate = effDate
        self.patient = patient
        self.doctor = doctor
        self.disease = disease
        self.prescriptionFileName = prescriptionFileName
        self.isBlindedFileGenerated = isBlindedFileGenerated
        self.isSanitizedFileGenerated = isSanitizedFileGenerated
        self.isUploadedCloud = isUploadedCloud
        self.hash=hash
        self.prevHash=prevHash
        self.isBlockChainGenerated = isBlockChainGenerated