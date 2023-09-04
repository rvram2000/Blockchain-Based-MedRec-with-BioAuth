class DoctorModel:
    # instance attribute
    def __init__(self, doctorID, doctorName, specialization ="", contactNbr="", emailID="", address=""):
        self.doctorID = doctorID
        self.doctorName = doctorName
        self.specialization = specialization
        self.contactNbr = contactNbr
        self.emailID = emailID
        self.address = address
