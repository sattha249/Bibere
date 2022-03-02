from flask import Flask, render_template , request , redirect , session , url_for
from flask_session import Session
import googlemaps
import geocoder
import mysql.connector
import hashlib
import json

user_name = "root"
passwd = "Codercamp1"

API_KEY = 'AIzaSyDzsdViVPdEbOCd53uuMWqMlPI8zPmWs8A'

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mydb = mysql.connector.connect(
    host="localhost",
    user=user_name,
    password = passwd ,
    database="cuppa"
)
cursor = mydb.cursor(buffered=True)

"""
 #Code to add hash password
hash_pass = hashlib.md5(str(passwd).encode('utf-8'))
hash_pass = hash_pass.hexdigest()
try :
    cursor.execute("INSERT INTO user_data (Username,hashpass,client) VALUES  ('satts','?',False)".format(hash_pass))
    mydb.commit()
except: 
    print("cannot connect")
    
#Code example to get hash from sql and check password
cursor.execute("SELECT hashpass FROM user_data WHERE id = 2")
c = cursor.fetchone()
"""
def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0
latitude = 0
longtitude = 0


#flask

@app.route('/',methods = ["get","post"])
def index():
    if not session.get("name"):
        return redirect("login_buyer")
    return redirect("profile")
    

@app.route('/login_buyer',methods = ["get","post"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hash_pass = hashlib.md5(str(password).encode('utf-8'))
        hash_pass = hash_pass.hexdigest()
        try:
            cursor.execute("SELECT username,hashpass FROM user_data WHERE username = '{}' AND client = true".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and hash_pass == login_data[0][1]:
                session["name"] = username 
                
        except:
            return "<h3>Wrong username or password<h3>"
        return redirect("/")
    return render_template("login_buyer.html") 
        
       
    
@app.route('/login_seller',methods =['get','post'])
def login_seller():
     if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hash_pass = hashlib.md5(str(password).encode('utf-8'))
        hash_pass = hash_pass.hexdigest()
        try:
            cursor.execute("SELECT username,hashpass FROM user_data WHERE username = '{}' AND client = false".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and hash_pass == login_data[0][1]:
                session["name"] = username 
                
        except:
            return "<h3>Wrong username or password<h3>"
        return redirect("/")
     return render_template("login_seller.html") 



@app.route('/sell_register',methods =['get','post'])
def sell_register():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        if len(password) >= 8:
            hash_pass = hashlib.md5(str(password).encode('utf-8'))
            hash_pass = hash_pass.hexdigest()
            
            try:
                cursor.execute("INSERT INTO user_data (username,hashpass,client,e_mail) VALUES ('{0}','{1}',false,'{2}')".format(username,hash_pass,email))
                mydb.commit()
                return "<h3>Register seller successfully<h3>" 
            except:
                return "<h3>Username already in use<h3>"
        else:
            return "password must more than 8 charactor" 
    return render_template("sell_register.html") 

@app.route('/buy_register',methods =['get','post'])
def buy_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        email = request.form.get("email")
        if confirm == password:
            hash_pass = hashlib.md5(str(password).encode('utf-8'))
            hash_pass = hash_pass.hexdigest()
            
            try:
                cursor.execute("INSERT INTO user_data (username,hashpass,client,e_mail) VALUES ('{0}','{1}',true,'{2}')".format(username,hash_pass,email))
                mydb.commit()
                return redirect ("login_buyer")
            except:
                return "<h3>Username already in use<h3>"
    
    return render_template("buy_register.html") 

@app.route('/cafenearyou',methods =['get','post'])
def barNearYou():
    
     #get my location
    myloc = geocoder.ip('me')
    lat = myloc.latlng[0]
    lng = myloc.latlng[1]
    print(myloc.latlng)
        # my home
    # lat = 13.753263121876094 
    # lng = 100.74236460509789


    locations = {'lat': lat , 'lng':lng}

    #get nearby cafe
    map_client = googlemaps.Client(API_KEY)
    # my home
    #location = (13.753263121876094, 100.74236460509789)
    location = (lat, lng)
    search_string = 'cafe'
    distance = miles_to_meters(15)
    business_list = []

    response = map_client.places_nearby(
        location = location,
        keyword = search_string,
        name = 'cafe',
        radius=distance
    )

    business_list.extend(response.get('results'))
    cafe = []
    for i in business_list:
        cafe.append([i['name'],i['geometry']['location']['lat'],i['geometry']['location']['lng']])
    
    return render_template("cafenearyou.html",location = locations,cafe = cafe)

@app.route('/profile',methods =['get','post'])
def profile_buyer():
    cursor.execute("SELECT * FROM user_data WHERE username = '{0}'".format(session["name"]))
    s = cursor.fetchall()
    mode = s[0][3]
    print (mode)
    if mode == True:
        return render_template("profile_buyer.html")
    return "test"
    
    
@app.route('/logout')
def logout():
    session["name"] = None
    return redirect("/")

@app.route('/map',methods =['get','post'])
def map():
   
     #get my location
    myloc = geocoder.ip('me')
    lat = myloc.latlng[0]
    lng = myloc.latlng[1]
    print(myloc.latlng)
        # my home
    # lat = 13.753263121876094 
    # lng = 100.74236460509789


    locations = {'lat': lat , 'lng':lng}

    #get nearby cafe
    map_client = googlemaps.Client(API_KEY)
    # my home
    #location = (13.753263121876094, 100.74236460509789)
    location = (lat, lng)
    search_string = 'cafe'
    distance = miles_to_meters(15)
    business_list = []

    response = map_client.places_nearby(
        location = location,
        keyword = search_string,
        name = 'cafe',
        radius=distance
    )

    business_list.extend(response.get('results'))
    cafe = []
    for i in business_list:
        cafe.append([i['name'],i['geometry']['location']['lat'],i['geometry']['location']['lng']])
    
    return render_template("map.html",location = locations,cafe = cafe)

if __name__ == "__main__" :
    app.run(debug=True)