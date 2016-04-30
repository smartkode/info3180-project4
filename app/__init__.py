from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
import os
from flask_mail import Mail


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///postgres'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fbtbetciuxdeyf:rGyaL_SqUh6LzsVew96JRXeIjh@ec2-54-83-61-45.compute-1.amazonaws.com:5432/d68irbpleakdl7'
app.config['SECRET_KEY'] = 'GGSB216737128edsgudsgdf^3!%#$$%^&89WEG{UDF}'

# app.config['UPLOAD_FOLDER'] = '/home/rascal/Desktop/test/app/static/img'
# app.config['UPLOAD_FOLDER'] = "/app/static/img"

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# MAIL_PORT : default 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT']= 587
app.config['MAIL_USERNAME'] = 'cmclaren89@gmail.com'
app.config['MAIL_PASSWORD'] = 'uwdaqbgqxdmhbdzo'
# app.config['MAIL_DEFAULT_SENDER'] = 'cmclaren89@gmail.com'
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

from app import views, models



