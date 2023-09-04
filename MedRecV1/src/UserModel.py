class UserModel:
    # instance attribute
    def __init__(self, userID, emailid, password ="", isCloudAuditor=False):
        self.userID = userID
        self.emailid = emailid
        self.password = password
        self.isCloudAuditor = isCloudAuditor
