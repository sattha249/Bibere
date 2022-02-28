from flask import Flask, render_template , request , redirect , session
from flask_session import Session
import googlemaps
from flask_googlemaps import GoogleMaps , Map
import mysql.connector
import hashlib

user_name = "root"
passwd = "Codercamp1"

API_KEY = 'AIzaSyApBCOaynrtpHX8TwnDS6zvMdDBoKEshMk'
map_client = googlemaps.Client(API_KEY)
work_place_address= '1 Market st, San Francisco, CA'
map_client.geocode(work_place_address)

app = Flask(__name__)
GoogleMaps(app, key="AIzaSyApBCOaynrtpHX8TwnDS6zvMdDBoKEshMk")
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
    """



#Code example to get hash from sql and check password
cursor.execute("SELECT hashpass FROM user_data WHERE id = 2")
c = cursor.fetchone()


#flask

@app.route('/',methods = ["get","post"])
def index():
    #session["name"] = None
    if not session.get("name"):
        return redirect("login_buyer")
    return "<h3>Log-in successfully</h3>"
    

@app.route('/login_buyer',methods = ["get","post"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "":
           return ("invalid name")
        elif request.form.get("password") == None:
           return ("invalid level")
        
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
        if request.form.get("username") == "":
           return ("invalid name")
        elif request.form.get("password") == None:
           return ("invalid level")
        
        username = request.form.get("username")
        password = request.form.get("password")
        hash_pass = hashlib.md5(str(password).encode('utf-8'))
        hash_pass = hash_pass.hexdigest()
        try:
            cursor.execute("SELECT username,hashpass FROM user_data WHERE username = '{}' AND client = false".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and hash_pass == login_data[0][1]:
                return "<h3>Log in to seller mode</h3>"
        except:
            return "<h3>Wrong username or password<h3>"
     return render_template("login_seller.html") 



@app.route('/sell_register',methods =['get','post'])
def sell_register():
    if request.method == "POST":
        
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
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
                return "<h3>Register buyer successfully<h3>" 
            except:
                return "<h3>Username already in use<h3>"
    
    return render_template("buy_register.html") 

@app.route('/barNearYou',methods =['get','post'])
def barNearYou():
    return "Bar near you"

@app.route('/map',methods =['get','post'])
def profile_edit():
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('example.html', mymap=mymap, sndmap=sndmap)

if __name__ == "__main__" :
    app.run(debug = True)