from app import db
from flask import session, g
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Required, Length, Email, EqualTo, URL
from app.models import Users, WishList
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.fields.html5 import URLField
from flask.ext.login import current_user

def email(form, field):
    user = Users.query.filter_by(email = field.data.lower()).first()
    if user:
    	field.errors.append("That email is already taken")

def ucheck(form, field):
    user = Users.query.filter_by(email = field.data.lower()).first()
    if not user:
    	field.errors.append("Invalid username")

def pword(form, field):
    user = Users.query.filter_by(email = form.username.data.lower()).first()
    if user and not check_password_hash(user.password, field.data):
    	field.errors.append("Invalid password")

def dup(form, field):
    wishlist = WishList.query.filter_by(owner = g.user.id).all()
    for wish in wishlist:
        if form.url.data == wish.url:
            field.errors.append("This item is already on your Wishlist")
    # ? = owner

class SignUpForm(Form):
    name = TextField('Firstname', validators=[Required(), Length(min=2, max=64)])
    email = TextField('Email', validators=[Required(), Email(), EqualTo('confirm_email', message="Email must match"), email])
    confirm_email = TextField('Confirm Email', validators=[Required(), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('confirm_password', message="Passwords must match")]) #---maybe add regex for safe passwords
    confirm_password = PasswordField('Re-enter Password', validators=[Required()])
    submit = SubmitField('Submit')

class LoginForm(Form):
	username = TextField('Username', validators=[Required(), ucheck])
	password = PasswordField('Password', validators=[Required(), pword])
	login = SubmitField('Login')
	

class WishForm(Form):
    title = TextField('Title', validators=[Required()])  # add per user validation
    description = TextAreaField('Description', validators=[Required()]) # add per user validation
    url = URLField('URL', validators=[URL(),dup]) # add per user validation
    thumbnail = URLField('Thumbnail', validators=[URL()])
    add = SubmitField('Add to Wishlist')

class WishListForm(Form):
	title = TextField('Title', validators=[Required()])  # add per user validation
	create = SubmitField('Create')
    
class UrlForm(Form):
    url = URLField('URL', validators=[URL()])
    submit = SubmitField('Select Thumbnail')
# class EditForm(Form):
# 	title = TextField('Title', validators=[Required()])
# 	description = TextAreaField('Description', validators=[Required()])
# 	url = URLField('URL', validators=[url()])
# 	add = SubmitField('Add')

	
# def UserCheck(form, field):
# 	def NameCheck(form, field):
# 		unames = db.session.execute('SELECT email FROM Users')
# 		names = []
# 		for namelist in unames:
# 			names.append(namelist[0])
# 			for name in names:
# 				if field.data == name:
# 					return True
# 	if not NameCheck(form,field):
# 		field.errors.append("Invalid username")

# def pwordcheck(form, field):
# 	pwh = db.session.execute('SELECT password FROM Users WHERE email = \'%s\'' % form.username.data)
# 	g = []
# 	for p in pwh:
# 		g.append(p[0]) 
# 	if len(g)>0 and not check_password_hash(g[0],field.data):
# 		field.errors.append("Invalid password")
