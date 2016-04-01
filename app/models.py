from app import db
from sqlalchemy.schema import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True)
    lastname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(100))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        

    # @property
    def is_authenticated(self):
        return True

    # @property
    def is_active(self):
        return True

    # @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3


    def __repr__(self):
        return 'User {}'.format(self.email)

class WishList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True)
    owner = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __init__(self, title, owner):
        self.title = title
        self.owner = owner

    def __repr__(self):
        return "Wishlist {}".format(self.title)


class Wish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(64), index=True)
    description = db.Column(db.String, index=True)
    url = db.Column(db.String, index=True)
    list_ = db.Column(db.Integer, ForeignKey('wish_list.id'), nullable=False)

    def __init__(self, owner, title, description, url, list_):
        self.title = title
        self.description = description
        self.url = url
        self.owner = owner
        self.list_ = list_

    def __repr__(self):
        return 'Wish {}'.format(self.title)