from flask import Flask, render_template , request , redirect , session , flash
from flask_session import Session
import googlemaps
import geocoder
import mysql.connector
import hashlib
import os
from os.path import join,dirname,realpath
from werkzeug.utils import secure_filename
import urllib.request


user_name = "root"
passwd = "Codercamp1"

API_KEY = 'AIzaSyDzsdViVPdEbOCd53uuMWqMlPI8zPmWs8A'

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = join(dirname(realpath(__file__)), 'static/profile/')
path = join(dirname(realpath(__file__)), 'static/profile/')
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


def get_age(y):
    a = str(y)
    b = a.split('-')
    print (2022 - int(b[0]))
    return (2022 - int(b[0]))


def allowed_file(filename):
    return '.' in filename and filename.rsplit(',',1)[1].lower() in ALLOWED_EXTENSIONS

def fetch_information():
    cursor.execute("SELECT id,firstname,lastname,dob,occupation,favorite,sickness,descriptions,e_mail,profile FROM user_inf WHERE id = {}".format(session["id"]))
    data = cursor.fetchall()
    data.append(get_age(data[0][3]))
    print(data)
    return data 


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
    # session["name"] = None
    # session["id"] = None
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
        try:
            cursor.execute("SELECT * FROM user_data WHERE username = '{0}'".format(session["name"]))
            s = cursor.fetchall()
            mode = s[0][3]
        except:
            return redirect("login_buyer")
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
    return render_template("edit_profile_buyer.html",id= data[0][0],f = data[0][1],l = data[0][2],d = data[0][3],
    oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8],picture = data[0][9],user = session['name'],age = data[1])
    


@app.route('/profile_display_buyer',methods = ['get','post'])
def profile_display_buyer():
    try:
        data = fetch_information()
        print(data)
        return render_template("profile_display_buyer.html",f = data[0][1],l = data[0][2],d = data[0][3],
        oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8],picture = data[0][9],age = data[1])
    except:
        return redirect('login_buyer')
    
    

@app.route('/logout')
def logout():
    session["name"] = None
    session["id"] = None
    return redirect("/")




@app.route('/upload',methods =['Get','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(path,filename))
            picture = filename
            print (picture)
            cursor.execute("UPDATE user_inf SET profile  = '{0}' WHERE id = {1}".format(picture,session['id']))
            mydb.commit()
            return redirect(request.url)
    return redirect("edit_profile_buyer")



@app.route('/edit_profile_seller',methods =['get','post'])
def edit_profile_seller():
    if request.method =='POST':
        if request.form['action'] =='update':
            name = request.form.get('seller-name')
            address = request.form.get('seller-address')
            desc = request.form.get('desc')
            print(name,address,desc)
            cursor.execute("""UPDATE user_inf SET firstname = '{0}',favorite ='{1}',descriptions ='{2}'
            WHERE id = {3} """.format(name,address,desc,session["id"]))
            mydb.commit()
        return redirect("profile")    
    data = fetch_information()
    return render_template("edit_profile_seller.html",name= data[0][1],address = data[0][5],desc = data[0][7],mail = data[0][8],picture = data[0][9],user = session['name'])

@app.route('/profile_display_seller',methods = ['get','post'])
def profile_display_seller():
    try:
        data = fetch_information()
        print(data)
        return render_template("profile_display_seller.html",name= data[0][1],address = data[0][5],desc = data[0][7],mail = data[0][8],picture = data[0][9],user = session['name'])
    except:
        return redirect('login_seller')
    
# route ที่ยังไม่ได้ใช้
@app.route('/profile_display_buyer_order',methods = ['get','post'])
def profile_display_buyer_order():
    data = fetch_information()
    return render_template("profile_display_buyer_order.html",f = data[0][1],l = data[0][2],d = data[0][3],
    oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8],age = data[1])

@app.route('/profile_display_seller_order',methods = ['get','post'])
def profile_display_seller_order():
    data = fetch_information()
    return render_template("profile_display_seller_order.html",f = data[0][1],l = data[0][2],d = data[0][3],
    oc = data[0][4] ,fav = data[0][5],s = data[0][6],desc = data[0][7],m = data[0][8],age = data[1])

@app.route('/profile_display_buyer_cafeHis',methods = ['get','post'])
def profile_display_buyer_cafeHis():
    return render_template("profile_display_buyer_cafeHis.html")

@app.route('/profile_display_buyer_favorite_details',methods = ['get','post'])
def profile_display_buyer_favorite_details():
    return render_template("profile_display_buyer_favorite_details.html")

@app.route('/profile_display_buyer_favorite',methods = ['get','post'])
def profile_display_buyer_favorite():
    return render_template("profile_display_buyer_favorite.html")


@app.route('/profile_display_buyer_teaHis',methods = ['get','post'])
def profile_display_buyer_teaHis():
    return render_template("profile_display_buyer_teaHis.html")

@app.route('/profile_display_seller_product',methods = ['get','post'])
def profile_display_seller_product():
    return render_template("profile_display_seller_product.html")

@app.route('/profile_display_seller_product_details',methods = ['get','post'])
def profile_display_seller_product_details():
    return render_template("profile_display_seller_product_details.html")




if __name__ == "__main__" :
    app.run(debug=True)