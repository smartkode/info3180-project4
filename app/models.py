from app import app
from app import db
from sqlalchemy.schema import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

secret_key = app.config['SECRET_KEY']

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(100))

    def __init__(self, name, email, password):
        self.name = name
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

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({u'id': self.id })

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            #Valid Token, but expired
            return None
        except BadSignature:
            #Invalid Token
            return None
        user_id = data['id']
        return user_id


    def __repr__(self):
        return 'User {}'.format(self.email)

class WishList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String, index=True)
    description = db.Column(db.String)
    url = db.Column(db.String)
    thumbnail = db.Column(db.String)

    def __init__(self, owner, title, description, url, thumbnail):
        self.owner = owner
        self.title = title
        self.description = description
        self.url = url
        self.thumbnail = thumbnail

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