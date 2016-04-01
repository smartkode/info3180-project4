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
@app.route('/api/user/register ', methods=['GET', 'POST'])
def signup():
    logout_user()
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            fname = request.form['firstname']
            lname = request.form['lastname']
            email = request.form['email']
            pw_hash = generate_password_hash(request.form['password'])
            new_user = Users(fname, lname, email, pw_hash)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup complete")
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

#---Authenticate and login user
@app.route('/api/user/login ', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            uname = request.form['username']
            pword = request.form['password']
            user = Users.query.filter_by(email=uname).first()
            if user is None:
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

#---Display home page
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

#---Returns json list of images
@app.route('/api/thumbnail/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        url = request.form['url']
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

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
            if "sprite" not in img["src"]:
                links.append(urlparse.urljoin(url, img["src"]))
                print urlparse.urljoin(url, img["src"])

        response = jsonify({'error': '1', 'data':'', 'message':'Unable to extract thumbnails'})

        if len(links)>0:
            response = jsonify({'error': 'null', 'data': {'thumbnails': links }, 'message':'success'})
        return response
    return render_template('url.html')

#---Creates a new wishlist
@app.route('/api/user/wishlist', methods=['GET', 'POST'])
@login_required
def newlist():
    form = WishListForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = request.form['title']
            owner = g.user.id
            new_list = WishList(title,owner)
            db.session.add(new_list)
            db.session.commit()
            flash("Wishlist created successfully")
            return render_template('create_wlist.html', form=form)
    return render_template('create_wlist.html', form=form)

#---Adds a wish
@app.route('/api/user/<int:id>/wishlist', methods=['POST'])
@login_required
def wishlist(id):
    list_id = id
    form = WishForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = request.form['title']
            descr = request.form['description']
            url = request.form['url']
            new_wish = Wish(g.user.id,title,descr,url,list_id)
            db.session.add(new_wish)
            db.session.commit()
            return redirect(url_for('view_wishes'))
    return render_template('wishlist.html', form=form, f=list_id)

#---View created wishes
@app.route('/api/user/<int:id>/wishlist')  
@login_required
def view_wishes(id):
    from flask import g
    userid = g.user.id    
    t = WishList.query.filter_by(owner=id).all()
    lst = []
    for g in t:
        wishlist = Wish.query.filter_by(owner=userid,list_=g.id).all()
        lst.append(wishlist)
    return render_template('wishes.html',lst=lst)

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