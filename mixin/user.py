from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, email, hoten):
        self.id = id
        self.username = username
        self.email = email
        self.hoten = hoten