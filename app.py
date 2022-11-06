from flask import Flask, url_for
from flask import render_template
from flask import request, redirect,Response
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
#import jwt
import datetime as dt
from functools import wraps
import sys
import requests
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
#from celery import Celery
#from flask_celery import make_celery
import io
import csv
import pandas as pd
from werkzeug.utils import secure_filename
import os
import geopy.distance
from geopy.geocoders import Nominatim
#import pdfkit
#from weasyprint import HTML
#import uuid
#from flask_caching import Cache
from random import randint 
from time import sleep
from flask import Flask, session
from flask_session import Session
app = Flask(__name__)
app.secret_key="anystringhere"
app.config['SECRET_KEY']= 'prakharsecrkjdsajljkadsfjkljlkdsxjflkjlasdjfxlkajfsdkl;kjldaskjljo;etis12key'
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///datab.sqlite3"
app.config['CELERY_BROKER_URL']= "redis://localhost:6379/1"
app.config['CELERY_RESULT_BACKEND']= "redis://localhost:6379/2"
app.config['UPLOAD_FOLDER'] = './upload'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']=465
app.config['MAIL_SERVER']= 'localhost'
app.config['MAIL_PORT']=1025
app.config['MAIL_USE_SSL']= False
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD']=''
Sender_Email = ""
Password = ""
servername='localhost'
serverport=1025
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
'''
celery = make_celery(app)
cache = Cache()
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
cache.init_app(app)
mail = Mail(app)
'''

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class User(UserMixin, db.Model):
    __tablename__= 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column( db.String, unique=True, nullable = False)
    password = db.Column( db.String, nullable = False)
    email = db.Column( db.String, unique=True, nullable = False)
    name = db.Column(db.String, nullable = False)
    address = db.Column(db.String)
class Inventory(db.Model):
    __tablename__= 'inventory'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column( db.String)
    category = db.Column( db.String)
    expirydate = db.Column( db.String)
    description = db.Column(db.String)
    imagename = db.Column(db.String)
    userid = db.Column(db.Integer)
class Shop(db.Model):
    __tablename__= 'shop'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column( db.String)
    category = db.Column( db.String)
    expirydate = db.Column( db.String)
    description = db.Column(db.String)
    imagename = db.Column(db.String)
    ownerid = db.Column(db.Integer)
    productid = db.Column(db.Integer)
    price = db.Column(db.Integer)
    ownername = db.Column(db.String)
    address = db.Column(db.String)
SECRET_KEY = os.urandom(32)
app.config['UPLOAD_FOLDER'] = './static/imagedata'
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(), Length(min=2, max=60)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])



# homepage

@app.route('/')
@login_required
def login1():
    #return 'welcome ' +current_user.name
    
    cards = db.session.query(Inventory).filter(Inventory.userid==current_user.id).all()
    abouttoexpire=[]
    for i in cards:
        a = i.expirydate
        year = int(a[0:4])
        month = int(a[5:7])
        day = int(a[8:10])
        hour = 0
        minute = 0
        sec = 0
        dat = datetime(year,month,day,hour,minute,sec)
        second = ( dat - datetime.now()).total_seconds()
        print(second)
        if second < 864000:
            abouttoexpire.append(i)
        

    recentlyadded = db.session.query(Inventory).filter(Inventory.userid==current_user.id).all()
    if len(recentlyadded)>4:
        recentlyadded = recentlyadded[-1:-5:-1]
    locator = Nominatim(user_agent="abcdef")
    l1 = locator.geocode(current_user.address)
    finalcard=[]
    
    shopcards = db.session.query(Shop).all()
    for i in shopcards:
        l2 = locator.geocode(i.address)
        dist = float(geopy.distance.distance((l1.latitude, l1.longitude), (l2.latitude, l2.longitude)).km)
        shopcard2=[]
        shopcard2.append(dist)
        shopcard2.append(i.id)
        finalcard.append(shopcard2)
        finalcard.sort()
        shopcards=[]
    print(finalcard)
    for i in finalcard:
        shopcards.append(db.session.query(Shop).filter(Shop.id==i[1]).first())


    return render_template('index.html', name = current_user.name, cards = cards, shopcards = shopcards, recentlyadded = recentlyadded, abouttoexpire= abouttoexpire, current_user = current_user)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="GET":
        return render_template('login_register.html')
    if request.method =="POST":
        form = request.form
        remember= request.form.getlist('remember')
        if len(remember)>0:
            rem = True
        else:
            rem=False

        print(form['username'])
    
        user = User.query.filter_by(username=form['username']).first()
        if user:
            if check_password_hash(user.password, form['password']):
                login_user(user,remember = rem)

                #return redirect('/dashboard')
                return redirect(url_for('login1'))
            
    return render_template('login_register.html', form=form)
    
    
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method =="GET":
        return render_template('login_register.html')
    if request.method =="POST":
        form = request.form
        
        user = db.session.query(User).filter(User.username==form['username']).first()
        # to check if user exists or not in User table
        
        if user == None:

            hashed_password = generate_password_hash(form['password'], method='sha256')
            new_user = User(username=form['username'], email=form['email'], password=hashed_password , name = form['fullname'])
            db.session.add(new_user)
            db.session.commit()
            #mailsignup.delay(form.email.data,form.username.data)
            return redirect(url_for('login1'))
            return redirect('/done')
        else:
            return 'Sorry the username already exist'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/item-added", methods=["GET","POST"])
@login_required
def idemadded():
    username = current_user.username
    if request.method == "GET":
    
        # to fetch all the decks of a particular user
        
        return redirect(url_for('login1'))
    
    if request.method=='POST':
        productname = request.form['productname']
        expirydate = request.form['date']
        description = request.form['description']
        category = request.form.get('catergory')
        data = db.session.query(Inventory).all()
        a = str(data[-1].id)
        a = int(a)+1
        print(productname,expirydate,description,category)
        
        
        print(request.files)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.split(".")[-1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(a)+"."+ext))
            data = Inventory(name= productname, expirydate = expirydate, description = description, category = category, imagename = str(a)+"."+ext, userid = current_user.id)
            db.session.add(data)
            db.session.commit()
            return redirect("/")
        return None
            

        return redirect("/")

@app.route("/delete/inventory/<id>", methods=["GET"])
@login_required
def deletefrominventory(id):
    username = current_user.username
    if request.method == "GET":
        
        db.session.query(Inventory).filter(Inventory.id==id).delete()
        db.session.commit()
        return redirect("/")

@app.route("/item-donated", methods=["GET","POST"])
@login_required
def idemdonated():
    username = current_user.username
    if request.method == "GET":
    
        # to fetch all the decks of a particular user
        
        return redirect(url_for('login1'))
    
    if request.method=='POST':
        name = request.form['name']
        expirydate = request.form['expirydate']
        description = request.form['description']
        category = request.form.get('catergory')
        price = request.form['price']
        ownername = current_user.name
        ownerid = current_user.id
        address = request.form['address']
        data = db.session.query(Shop).all()
        a = str(data[-1].id)
        a = int(a)+1
        
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.split(".")[-1]
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],"shop"+ str(a)+"."+ext))
            data = Shop(name= name, expirydate = expirydate, description = description, category = category, imagename = "shop"+str(a)+"."+ext, ownerid = current_user.id, ownername = current_user.name , address = address , price = price, productid = -1)
            db.session.add(data)
            db.session.commit()
            return redirect("/")
        return None
@app.route("/inventory-item-donated/<id>", methods=["GET","POST"])
@login_required
def inventoryitemdonated(id):
    username = current_user.username
    if request.method == "GET":
    
        # to fetch all the decks of a particular user
        
        return redirect(url_for('login1'))
    
    if request.method=='POST':

        data= db.session.query(Inventory).filter(Inventory.id==id).first()
        name = data.name
        expirydate = data.expirydate
        description = data.description
        category = data.category
        price = request.form['price']
        ownername = current_user.name
        ownerid = current_user.id
        address = current_user.address
        imagename = data.imagename
        productid = id
        data = Shop(name= name, expirydate = expirydate, description = description, category = category, imagename = imagename, ownerid = ownerid, ownername = ownername , address = address , price = price, productid = productid)
        db.session.add(data)
        db.session.commit()

        return redirect("/")
@app.route("/updatedata", methods=["GET","POST"])
@login_required
def updatedata():
    id = current_user.id
    if request.method == "GET":
    
        # to fetch all the decks of a particular user
        
        return redirect(url_for('login1'))
    
    if request.method=='POST':
        if request.form.get('update') == 'value':
            name = request.form["name"]
            address = request.form["address"]
            email = request.form["email"]
            username = request.form["username"]
            db.session.query(User).filter(User.id==id).update({User.username :username, User.name : name, User.email :email, User.address : address}, synchronize_session = False)
            db.session.commit()

            return redirect("/")
@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    data = db.session.query(Inventory).all()
    a = str(data[-1].id)
    print(a)
    return 'welcome'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'


if __name__=='__main__':
    app.run(host = '0.0.0.0',debug = True,port = 8080)   
    
