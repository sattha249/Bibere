from flask import Flask, render_template , request , redirect , session , flash
from flask_session import Session
import googlemaps
import geocoder
import mysql.connector
import hashlib
import os
from werkzeug.utils import secure_filename
import urllib.request

user_name = "root"
passwd = "Codercamp1"

API_KEY = 'AIzaSyDzsdViVPdEbOCd53uuMWqMlPI8zPmWs8A'

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/profile'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])
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

def get_age(y):
    x = y.split("-")
    y = int(x[0])
    return (2022-y)

def fetch_information():
    cursor.execute("SELECT id,firstname,lastname,IFNULL(dob,0000-00-00),occupation,favorite,sickness,descriptions,e_mail FROM user_inf WHERE id = {}".format(session["id"]))
    data = cursor.fetchall()
    print(data)
    return data 

def allowed_file(filename):
    return '.' in filename and filename.rsplit(',',1)[1].lower() in ALLOWED_EXTENSIONS

def register(username,hash_pass,mode,email):
    cursor.execute("INSERT INTO user_data (username,hashpass,client) VALUES ('{0}','{1}',{2})".format(username,hash_pass,mode))
    mydb.commit()
    cursor.execute("SELECT id FROM user_data WHERE username = '{0}'".format(username))
    i = cursor.fetchone()
    cursor.execute("INSERT INTO user_inf(id,e_mail) VALUES ({0},'{1}')".format(i[0],email))
    mydb.commit()

def login(username,hash_pass,mode):
    cursor.execute("SELECT username,hashpass,id FROM user_data WHERE username = '{0}' AND client = true".format(username))
    login_data = cursor.fetchall()
    if username == login_data[0][0] and hash_pass == login_data[0][1]:
        session["name"] = username 
        session["id"] = login_data[0][2]

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
            cursor.execute("SELECT username,hashpass,id FROM user_data WHERE username = '{0}' AND client = true".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and hash_pass == login_data[0][1]:
                session["name"] = username 
                session["id"] = login_data[0][2]
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
            cursor.execute("SELECT username,hashpass,id FROM user_data WHERE username = '{}' AND client = false".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and hash_pass == login_data[0][1]:
                session["name"] = username 
                session["id"] = login_data[0][2]
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
                mode = 0
                register (username,hash_pass,mode,email)
                return redirect("login_seller")
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
                mode = 1
                register (username,hash_pass,mode,email)
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
    print (cafe)
    return render_template("cafenearyou.html",location = locations,cafe = cafe)



@app.route('/profile',methods =['get','post'])
def profile():
    if session["name"]:
        cursor.execute("SELECT * FROM user_data WHERE username = '{0}'".format(session["name"]))
        s = cursor.fetchall()
        mode = s[0][3]
        if mode == True:
            return redirect("profile_display_buyer")
        return redirect("profile_display_seller")
    return redirect("login_buyer")


@app.route('/edit_profile_buyer',methods = ['get','post'])
def edit_profile_buyer():
    if request.method =='POST':
        if request.form['action'] =='update':
            firstname = request.form.get('name')
            lastname = request.form.get('surname')
            date = request.form.get('date')
            oc = request.form.get('occupation')
            sick = request.form.get('sickness')
            favorite = request.form.get('favorite')
            desc = request.form.get('desc')
            print(firstname,lastname,date,oc,sick,desc)
            cursor.execute("""UPDATE user_inf SET firstname = '{0}',lastname = '{1}' ,
            dob ='{2}',occupation ='{3}',favorite ='{4}',sickness = '{5}',descriptions ='{6}'
            WHERE id = {7} """.format(firstname,lastname,date,oc,favorite,sick,desc,session["id"]))
            mydb.commit()
        return redirect("profile")    
    data = fetch_information()
    return render_template("edit_profile_buyer.html",f = data[0][1],l = data[0][2],d = data[0][3],
    oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8])
    


@app.route('/profile_display_buyer',methods = ['get','post'])
def profile_display_buyer():
    data = fetch_information()
    print(data)
    return render_template("profile_display_buyer.html",f = data[0][1],l = data[0][2],d = data[0][3],
    oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8])
    
    


@app.route('/logout')
def logout():
    session["name"] = None
    session["id"] = None
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


@app.route('/upload',methods =['Get','POST'])
def upload():
    try:
        print("post")
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename =='':
            flash ('No image selected  for uploading')
            return "no image"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            print ('upload_image filename : ' + filename)
            flash('success')
            return "success"
        else:
            flash('Allowed image types are != png,jpg,jpeg,gif')
            return redirect(request.url)
    except:
        print("get")
        return redirect("profile")


# route ที่ยังไม่ได้ใช้
@app.route('/edit_profile_seller',methods =['get','post'])
def edit_profile_seller():
    return render_template("edit_profile_seller.html")

@app.route('/profile_display_seller',methods = ['get','post'])
def profile_display_seller():
    return render_template('profile_display_seller.html')




if __name__ == "__main__" :
    app.run(debug=True)