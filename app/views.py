"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

from app import app
from flask import render_template, request, redirect, url_for, jsonify, g, session, flash
from app import db

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Users, Wish, WishList
from app.forms import LoginForm, SignUpForm, WishForm, WishListForm#, EditForm

from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db
from app import lm


from flask import Flask, abort, make_response
import requests
from bs4 import BeautifulSoup
import urlparse
import urllib2

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
@app.route('/api/user/register', methods=['POST'])
def register():
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    name = request.form['name']
    if name and email and password:
        if Users.query.filter_by(email = email).first() is None:
            new_user = Users(name, email, password)
            db.session.add(new_user)
            db.session.commit()
            user = Users.query.filter_by(email = email).first()
            token = user.generate_auth_token(600)
            return jsonify({'error':'null', 'data':{'token': token.decode('ascii'), 'expires': 600, 'user':{'id': user.id, 'email': user.email, 'name': user.name}, 'message':'success'}})
        if Users.query.filter_by(email = email).first() is not None:
            user = Users.query.filter_by(email = email).first()
            return jsonify({'error': '1', 'data': {'email': user.email}, 'message':'user already exists'})
    

#---Authenticate and login user
@app.route('/api/user/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if email and password:
        user = Users.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            g.user = user
            token = user.generate_auth_token(600)
            return jsonify({'error':'null', 'data':{'token': token.decode('ascii'), 'expires': 600, 'user':{'id': user.id, 'email': user.email, 'name': user.name}, 'message':'success'}})
        return jsonify({'error': '1', 'data':{}, 'message':'Bad user name or password'})
        

#---Display home page
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

#---Returns json list of images
@app.route('/api/thumbnail/process', methods=['POST'])
def process():
    url = request.form['url']
    headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0',\
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':'en-US,en;q=0.5',\
    'Accept-Encoding':'none','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Connection': 'keep-alive'}

    request_ = urllib2.Request(url, headers=headers)
    data = urllib2.urlopen(request_)
    soup = BeautifulSoup(data, 'html.parser')

    links = []
    og_image = (soup.find('meta', property='og:image') or
                        soup.find('meta', attrs={'name': 'og:image'}))
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

#---Adds a wish
@app.route('/api/user/<int:id>/wishlist', methods=['POST', 'GET'])
# @login_required
def wishlist(id):
    if request.method == 'POST':
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
    user = Users.query.filter_by(id=id).first()
    if user:
        wishlist = WishList.query.filter_by(owner=id).all()
        wlst = []
        for wish_ in wishlist:
            wlst.append({'title':wish_.title, 'description':wish_.description, 'url':wish_.url, 'thumbnail':wish_.thumbnail})
        resp = ({'error':'null', 'data':{'wishes': wlst}, 'message':'success'})
        return jsonify(resp)
    return jsonify({'error':'1', 'data':'', 'message':'no such wishlist exists'})


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

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