"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

from app import app
from flask import render_template, request, redirect, url_for, jsonify, g, session, flash, _request_ctx_stack
from werkzeug.local import LocalProxy
from app import db

import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Users, Wish, WishList
from app.forms import LoginForm, SignUpForm, WishForm, WishListForm, SendEmailForm#, UrlForm, EditForm

from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db 
from app import lm, mail

from flask_mail import Message
from flask import Flask, abort, make_response
import requests
from bs4 import BeautifulSoup
import urlparse
import urllib2
import sys

import smtplib, base64, jwt

from werkzeug.local import LocalProxy
from flask.ext.cors import cross_origin
from functools import wraps


secret = app.config["SECRET_KEY"]
###
# Routing for your application.
###

@app.before_request
def before_request():
    g.user = current_user
    
@lm.user_loader
def load_user(id):
    return Users.query.get(int(id))

#---Creates new users
@app.route('/api/user/register', methods=['GET','POST'])
def register():
    if request.method == 'POST' and 'User-Agent' not in request.headers:
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        name = request.form['name']
        if name and email and password:
            if Users.query.filter_by(email = email).first() is None:
                new_user = Users(name, email, password)
                db.session.add(new_user)
                db.session.commit()
                user = Users.query.filter_by(email = email).first()
                token = user.generate_auth_token(600)  #---visit tutorial on generating this
                return jsonify({'error':'null', 'data':{'token': token.decode('ascii'), 'expires': 600, 'user':{'id': user.id, 'email': user.email, 'name': user.name}, 'message':'success'}})
            if Users.query.filter_by(email = email).first() is not None:
                user = Users.query.filter_by(email = email).first()
                return jsonify({'error': '1', 'data': {'email': user.email}, 'message':'user already exists'})
    form = SignUpForm()
    if request.method == 'POST' and 'User-Agent' in request.headers:
        if form.validate_on_submit():
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            name = request.form['name']
            new_user = Users(name, email, password)
            db.session.add(new_user)
            db.session.commit()
            # user = Users.query.filter_by(email = email).first()
            # token = user.generate_auth_token(600)  #---visit tutorial on generating this
            return redirect(url_for('login'))
    return render_template(
        'signup.html',
        title='User Signup',
        year=datetime.datetime.now().year,
        form=form,
        user=g.user
    )

#---Authenticate and login user
@app.route('/api/user/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'User-Agent' not in request.headers:
        email = request.form['email']
        password = request.form['password']
        if email and password:
            user = Users.query.filter_by(email=email).first()
            if user and user.verify_password(password):
                g.user = user
                token = user.generate_auth_token(600)
                return jsonify({'error':'null', 'data':{'token': token.decode('ascii'), 'expires': 600, 'user':{'id': user.id, 'email': user.email, 'name': user.name}, 'message':'success'}})
            return jsonify({'error': '1', 'data':{}, 'message':'Bad user name or password'})
        else:
            return "hello there"
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST' and 'User-Agent' in request.headers:
        print "posted some stuff here"
        if form.validate_on_submit():
            print "posted some stuff here"
            uname = request.form['username']
            pword = request.form['password']
            user = Users.query.filter_by(email=uname).first()
            if user is None:
                return redirect(url_for('login'))
            login_user(user)
            return redirect(request.args.get("next") or url_for('wishlist',id=g.user.id))

    return render_template(
        'login.html',
        title='User Login',
        year=datetime.datetime.now().year,
        form=form,
        user=g.user
    )










#-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\
#---Testing code for jwt authentication

# def create_token(user):
#     payload = {
#         'sub': user.id,
#         'iat': datetime.datetime.utcnow(),
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
#     }
#     token = jwt.encode(payload, secret, algorithm='HS256')
#     return token.decode('unicode_escape')

# def parse_token(req):
#     token = req.headers.get('Authorization').split()[1]
#     return jwt.decode(token, SECRET_KEY, algorithms='HS256')

# @app.route('/api/login', methods=['GET','POST'])
# def login_2():
#     if request.method == 'POST':
#         try:
#             data = request.get_json()
#             print "works here"
#             # print data
#             return jsonify({"data": data})
#         except:
#             try:
#                 email= request.form['email']
#                 print jsonify(email)
#             except Exception as e:
#                 print e
#                 return "error"
        
        # return "{}".format(data)
        # email = data['email']
        # password = data['password']
        # user = Users.query.filter_by(email=email).first()
        # if user == None:
        #     response = make_response(jsonify({"message" : "invalid username/password"}))
        #     response.status_code = 401
        #     return response
        # if check_password_hash(user.password, password):
        #     token = create_token(user)
        #     return {"token" : token}
        # else:
        #     response = make_response(jsonify({"message" : "invalid username/password"}))
        #     response.status_code = 401
        #     return response
    # return render_template('jwt.html')

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not request.headers.get('Authorization'):
#             response = jsonify(message='Missing authorization header')
#             response.status_code = 401
#             return response

#         try:
#             payload = parse_token(request)
#         except DecodeError:
#             response = jsonify(message='Token is invalid')
#             response.status_code = 401
#             return response
#         except ExpiredSignature:
#             response = jsonify(message='Token has expired')
#             response.status_code = 401
#             return response

#         g.user_id = payload['sub']

#         return f(*args, **kwargs)

#     return decorated_function

# def authenticate(error):
#   resp = jsonify(error)

#   resp.status_code = 401

#   return resp


# def requires_auth(f):
#   @wraps(f)
#   def decorated(*args, **kwargs):
#     auth = request.headers.get('Authorization', None)
#     if not auth:
#       return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

#     parts = auth.split()

#     if parts[0].lower() != 'bearer':
#       return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
#     elif len(parts) == 1:
#       return {'code': 'invalid_header', 'description': 'Token not found'}
#     elif len(parts) > 2:
#       return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

#     token = parts[1]
#     try:
#          payload = jwt.decode(token, secret)
  
#     except jwt.ExpiredSignature:
#         return authenticate({'code': 'token_expired', 'description': 'token is expired'})
#     except jwt.DecodeError:
#         return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})
    
#     _request_ctx_stack.top.current_user = user = payload
#     return f(*args, **kwargs)

#   return decorated
#-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\






#---Display home page
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template(
        'home.html',
        title='Home',
        year=datetime.datetime.now().year,
        user=g.user
    )

#---Returns json list of images
@app.route('/api/thumbnail/process', methods=['GET','POST'])
def process():
    if request.method == 'POST' and 'User-Agent' not in request.headers:
        url = request.form['url']
        headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0',\
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.5',\
        'Accept-Encoding':'none','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Connection': 'keep-alive'}

        request_ = urllib2.Request(url, headers=headers)
        data = urllib2.urlopen(request_)
        soup = BeautifulSoup(data, 'html.parser')

        links = []
        og_image = (soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'}))  
        if og_image and og_image['content']:
            links.append(og_image['content'])
            print og_image['content']

        thumbnail_spec = soup.find('link', rel='image_src')
        if thumbnail_spec and thumbnail_spec['href']:
            links.append(thumbnail_spec['href'])
            print thumbnail_spec['href']

        for img in soup.find_all("img", class_="a-dynamic-image", src=True):
            if "sprite" not in img["src"] and "data:image/jpeg" not in img["src"]:
                links.append(urlparse.urljoin(url, img["src"]))
                print urlparse.urljoin(url, img["src"])

        response = jsonify({'error': '1', 'data':'', 'message':'Unable to extract thumbnails'})

        if len(links)>0:
            response = jsonify({'error': 'null', 'data': {'thumbnails': links }, 'message':'success'})
        return response
    if request.method == 'POST' and 'User-Agent' in request.headers:
        return "yo"
    return render_template(
        'url.html',
        title='Process',
        year=datetime.datetime.now().year
    )

def process_(url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0',\
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.5',\
    'Accept-Encoding':'none','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Connection': 'keep-alive'}
    
    request_ = urllib2.Request(url, headers=headers)
    data = urllib2.urlopen(request_)
    soup = BeautifulSoup(data, 'html.parser')

    links = []  
    og_image = (soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        links.append(og_image['content'])
        print og_image['content']

    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        links.append(thumbnail_spec['href'])
        print thumbnail_spec['href']

    for img in soup.find_all("img", class_="a-dynamic-image", src=True):
        if "sprite" not in img["src"] and "data:image/jpeg" not in img["src"]:
            links.append(urlparse.urljoin(url, img["src"]))
            print urlparse.urljoin(url, img["src"])

    images = []
    if len(links)>0:
        for t in range(0, len(links)):
            l = '<div  class=\'btn grab\'><img id=\'tick' + str(t) +  '\' height=\'100px\' width=\'100px\' src=' + links[t] + '></img></div>'
            images.append(l)

    set_ = ""
    for i in images:
        set_ += i
    return set_
    # return images

#---Adds a wish
@app.route('/api/user/<int:id>/wishlist', methods=['POST', 'GET'])
@login_required
def wishlist(id):
    f = id
    wishlist = WishList.query.filter_by(owner=id).all()
    if request.method == 'POST' and 'User-Agent' not in request.headers:
        url = request.form['url']
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']
        thumbnail = request.form['thumbnail']
        user = Users.query.filter_by(id=id).first()
        if user:
            new_wish = WishList(id, title, description, url, thumbnail)
            db.session.add(new_wish)
            db.session.commit()
            wlst = []
            wishlist = WishList.query.filter_by(owner=id).all()
            for wish_ in wishlist:
                wlst.append({'title':wish_.title, 'description':wish_.description, 'url':wish_.url, 'thumbnail':wish_.thumbnail})
            resp = ({'error':'null', 'data':{'wishes': wlst}, 'message':'success'})
            return jsonify(resp)
        return jsonify({'error':'1', 'data':'', 'message':'no such wishlist exists'})
    
    if request.method == 'GET' and 'User-Agent' not in request.headers:
        user = Users.query.filter_by(id=id).first()
        if user:
            wishlist = WishList.query.filter_by(owner=id).all()
            wlst = []
            for wish_ in wishlist:
                wlst.append({'title':wish_.title, 'description':wish_.description, 'url':wish_.url, 'thumbnail':wish_.thumbnail})
            resp = ({'error':'null', 'data':{'wishes': wlst}, 'message':'success'})
            return jsonify(resp)
        return jsonify({'error':'1', 'data':'', 'message':'no such wishlist exists'})
    
    form = WishForm()
    e_form = SendEmailForm()
    if request.method == 'POST' and 'User-Agent' in request.headers:
        if len(request.form) == 1:
            # print "hello world  "
            try:
                url = request.form['url']
                choice = process_(url)
                return "{}".format(choice)
            except Exception as e:
                try:
                    wish = request.form['wish']
                    db.session.execute("DELETE FROM wish_list WHERE thumbnail=\'"+ wish + "\'")
                    db.session.commit()
                except Exception as d:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
        
            return render_template(
                    'wishlist.html',
                    title='Wishlist',
                    year=datetime.datetime.now().year,
                    f=f,
                    form=form,
                    user=g.user
                )

        if len(request.form) == 3:
            # print "2"
            addr = request.form['email']
            toaddr = addr.replace(" ","").split(",")
            fromname = g.user.name
            fromaddr = g.user.email
            subject = g.user.name + "'s Wishlist"
            msg = "Hey! Check out my Wishlist at " + request.url
            
            messagetosend = Message(subject=subject, sender=fromaddr, recipients=toaddr, body=msg)
            mail.send(messagetosend)
            
            return render_template(
                'wishlist.html',
                title='Wishlist',
                year=datetime.datetime.now().year,
                f=f,
                wishlist=wishlist,
                form=form,
                e_form = e_form,
                user=g.user
            )

        if form.validate_on_submit():
            title = request.form['title']
            descr = request.form['description']
            url = request.form['url']
            thumb = request.form['thumbnail']
            user = Users.query.filter_by(id=id).first()
            if user:
                new_wish = WishList(id, title, descr, url, thumb)
                db.session.add(new_wish)
                db.session.commit()
                wishlist_ = WishList.query.filter_by(owner=id).all()
                return render_template(
                    'wishlist.html',
                    title='Wishlist',
                    year=datetime.datetime.now().year,
                    f=f,
                    form=form,
                    wishlist=wishlist_,
                    e_form = e_form,
                    user=g.user
                )
    
    return render_template(
        'wishlist.html',
        title='Wishlist',
        year=datetime.datetime.now().year,
        f=f,
        wishlist=wishlist,
        form=form,
        e_form = e_form,
        user=g.user
    )

@app.route('/api/user/wishlist/rank', methods=['GET', 'POST'])
def rank():
    rank = request.form['rank']
    if rank == "plus":
        db.session.execute("UPDATE wish_list SET rank=(rank+1) WHERE owner=\'"+ g.user.id + "\'")
        db.commit()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about')
def about():
    """Render the website's about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.datetime.now().year,
        message='Your application description page.',
        user=g.user
    )


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

# @app.before_request

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=8888)


#-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\-/-\



