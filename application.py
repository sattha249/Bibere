from flask import Flask, render_template , request , redirect , session 
from flask_session import Session
import googlemaps
import geocoder
import mysql.connector
import hashlib
import os
from os.path import join,dirname,realpath
from werkzeug.utils import secure_filename
import qrcode
import cv2
from flask_dropzone import Dropzone
import random

#local
# user_name = "root"
# passwd = "Codercamp1"


#heroku
user_name = "bbd3d205e5481c"
passwd = "abbd99cf"

API_KEY = 'AIzaSyDzsdViVPdEbOCd53uuMWqMlPI8zPmWs8A'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'U63LKnnHGJ'
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = join(os.getcwd(), 'static/QRcode/')
app.config['DROPZONE_MAX_FILE_SIZE'] = 5
app.config['DROPZONE_MAX_FILES'] = 1
app.config['DROPZONE_REDIRECT_VIEW'] = "decode"
path = join(os.getcwd(), 'static/profile/')
pathQR = join(os.getcwd(), 'static/QRcode/')
pathProduct = join(os.getcwd(), 'static/product/')
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])
Session(app)
dropzone = Dropzone(app)

recommend_tea = ['Oolong tea','Black tea','Green tea','White tea','Rose tea']
recommend_coffee = ['Americano','Espresso','Latte','Cappuccino','Mocha']


# mydb = mysql.connector.connect(
#     host="localhost",
#     user=user_name,
#     password = passwd ,
#     database="cuppa"
# )
# cursor = mydb.cursor(buffered=True)


#heroku
# mydb = mysql.connector.connect(
#     host="us-cdbr-east-05.cleardb.net",
#     user=user_name,
#     password = passwd ,
#     database="heroku_042e13b0752ec02"
# )
# cursor = mydb.cursor(buffered=True)

# jaws
mydb = mysql.connector.connect(
    host="i0rgccmrx3at3wv3.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
    user="andqgs9kpf5dblxp",
    password = "j9rw1kgggz50c452" ,
    database="o835zbwa3c4q8985"
)
cursor = mydb.cursor(buffered=True)

 


def miles_to_meters(miles):
    try:
        return miles * 1_609.344
    except:
        return 0


def get_age(y):
    a = str(y)
    b = a.split('-')
    return (2022 - int(b[0]))


def allowed_file(filename):
    return '.' in filename and filename.rsplit(',',1)[1].lower() in ALLOWED_EXTENSIONS

def getmode():
    try:
        cursor.execute("SELECT * FROM user_data WHERE username = '{0}'".format(session["name"]))
        s = cursor.fetchall()
        mode = s[0][3]
        return mode
    except:
        return redirect("login_buyer")

def fetch_information():
    cursor.execute("SELECT id,firstname,lastname,dob,occupation,favorite,sickness,descriptions,e_mail,profile,address,points FROM user_inf WHERE id = {}".format(session["id"]))
    data = cursor.fetchall()
    data.append(get_age(data[0][3]))
    print(data)
    return data


def fetch_order():
    mode = getmode()
    if mode == True:
        cursor.execute("""SELECT product_inf.product_name,
        product_inf.tea,
        user_inf.firstname,
        user_inf.address,
        (product_inf.price - pay) as paid 
        FROM product_inf 
        inner join order_inf on product_inf.product_id = order_inf.product_id 
        inner join user_inf on user_inf.id = order_inf.seller_id 
        WHERE order_inf.customer_id = {0};""".format(session['id']))
        
        data = cursor.fetchall()
    else :
        cursor.execute("""SELECT user_inf.firstname , product_inf.product_name,
        order_date,status,payment,(product_inf.price - pay) as paid 
        from user_inf inner join order_inf on user_inf.id = order_inf.customer_id 
        inner join product_inf on product_inf.product_id = order_inf.product_id 
        where order_inf.seller_id = {0};""".format(session['id']))
        data = cursor.fetchall()
    for i in data:
        print(i)
    return data 

def fetch_product():
    cursor.execute("SELECT product_name,tea,descriptions,price,point,picture,product_id FROM product_inf WHERE seller = {}".format(session['id']))
    bev = cursor.fetchall()
    return bev

def get_bev_score(data):
    bev = 0
    if data >=1200:
        bev = 6
    elif data >=1000:
        bev = 5
    elif data >=800:
        bev = 4
    elif data >=600:
        bev = 3
    elif data >=400:
        bev = 2
    elif data >=200:
        bev = 1
    print ("bev = ", bev)
    return bev

def get_visit_score():
    data = 0
    try:
        cursor.execute("select COUNT(*) from order_inf where customer_id = {0} GROUP BY seller_id,order_date;".format(session['id']))
        data = cursor.fetchall()
        data = len(data)
        print (data)
    except:
        pass
    visit = 0
    if data >=12:
        visit = 6
    elif data >=10:
        visit = 5
    elif data >=8:
        visit = 4
    elif data >=6:
        visit = 3
    elif data >=4:
        visit = 2
    elif data >=1:
        visit = 1
    print ("visit = ", visit)
    return visit

def fetch_history():
    mode = getmode()
    if mode == True:
        try:
            cursor.execute("""SELECT user_inf.firstname,user_inf.address,order_inf.order_date 
            FROM user_inf INNER JOIN order_inf ON order_inf.seller_id = user_inf.id 
            WHERE order_inf.customer_id = {0} GROUP BY user_inf.firstname,order_inf.order_date 
            ORDER BY order_inf.order_date; """.format(session['id']))
            history = cursor.fetchall()
        except:
            history = 0
    return history

def fetch_point():
    mode = getmode()
    if mode == True:
        cursor.execute("""SELECT product_inf.product_name,user_inf.firstname,product_inf.point 
        FROM product_inf inner join order_inf on product_inf.product_id = order_inf.product_id 
        inner join user_inf on user_inf.id = order_inf.seller_id 
        WHERE order_inf.customer_id = {0} ORDER BY order_inf.order_date;""".format(session['id']))
        point_details = cursor.fetchall()
    return point_details

def fetch_stat():
    cursor.execute("select count(customer_id) from order_inf where seller_id = {0}".format(session['id']))
    sell= cursor.fetchall()
    sell = list(sell[0])
    cursor.execute(" select count(customer_id) from order_inf where seller_id = {0} group by customer_id, order_date ".format(session['id']))
    visit = cursor.fetchall()
    visit = len(visit)
    sell.append(visit)
    return sell
   


def give_point(collect):
    print('collect = ' ,collect)
    point = []
    for i in collect:
        point.append(int(i))
    return point
    

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
def login_buyer():
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
                return redirect("/")
        except:
            return "<h3>Wrong username or password<h3>"
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
                return redirect("/")
        except:
            return "<h3>Wrong username or password<h3>"
        
     return render_template("login_seller.html") 



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
            return "password must more than 8 characters" 
    return render_template("sell_register.html") 



@app.route('/cafenearyou',methods =['get','post'])
def barNearYou():   
    #  get my location
    myloc = geocoder.ip('me')
    lat = myloc.latlng[0]
    lng = myloc.latlng[1]
    print(myloc.latlng)

    # siamscape
    # lat = 13.745490
    # lng = 100.531117
    # locations = {'lat': lat , 'lng':lng}

    #   my home
    # lat = 13.753263121876094 
    # lng = 100.74236460509789
    locations = {'lat': lat , 'lng':lng}

    #get nearby cafe
    map_client = googlemaps.Client(API_KEY)
    
    location = (lat, lng)
    search_string = 'cafe','bakery'
    distance = miles_to_meters(3)
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
        #ส่วนนี้ใช้แก้ปัญหาเรื่อง Json parse error
        if 'Hob & Coff' not in i['name'] :
            cafe.append([i['name'],i['geometry']['location']['lat'],i['geometry']['location']['lng']])
    print (business_list[0])
    print (cafe)
    return render_template("cafenearyou.html",location = locations,cafe = cafe)






@app.route('/profile',methods =['get','post'])
def profile():
    if session["name"]:
        mode = getmode()
        if mode == True:
            return redirect("profile_display_buyer")
        return redirect("profile_display_seller")
    return redirect("login_buyer")



@app.route('/profile_display_buyer',methods = ['get','post'])
def profile_display_buyer():
    # try:
        data = fetch_information()
        print(data)
        bev = get_bev_score(data[0][11])
        visit = get_visit_score()
        return render_template("profile_display_buyer.html",
        f = data[0][1],
        l = data[0][2],
        d = data[0][3],
        oc = data[0][4],
        fav = data[0][5],
        s = data[0][6],
        desc = data[0][7],
        m = data[0][8],
        picture = data[0][9],
        point = data[0][11],
        age = data[1],
        bev = bev,
        visit = visit)
    # except:
    #     return redirect('login_buyer')

@app.route('/profile_display_seller',methods = ['get','post'])
def profile_display_seller():
    try:
        data = fetch_information()
        print(data)
        sell = fetch_stat()
        return render_template("profile_display_seller.html",visit = sell[1],
        sell = sell[0],
        name= data[0][1],
        desc = data[0][7],
        mail = data[0][8],
        picture = data[0][9],
        address = data[0][10],
        user = session['name'])
    except:
        return redirect('login_seller')



@app.route('/edit',methods = ['get','post'])
def edit():
    if session["name"]:
        mode = getmode()
        if mode == True:
            return redirect("edit_profile_buyer")
        return redirect("edit_profile_seller")
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
    return render_template("edit_profile_buyer.html",id= data[0][0],
    f = data[0][1],
    l = data[0][2],
    d = data[0][3],
    oc = data[0][4],
    fav = data[0][5],
    s = data[0][6],
    desc = data[0][7],
    m = data[0][8],
    picture = data[0][9],
    age = data[1])

@app.route('/edit_profile_seller',methods =['get','post'])
def edit_profile_seller():
    if request.method =='POST':
        if request.form['action'] =='update':
            name = request.form.get('seller-name')
            address = request.form.get('seller-address')
            desc = request.form.get('desc')
            print(name,address,desc)
            cursor.execute("""UPDATE user_inf SET firstname = '{0}',address ='{1}',descriptions ='{2}'
            WHERE id = {3} """.format(name,address,desc,session["id"]))
            mydb.commit()
        return redirect("profile")    
    data = fetch_information()
    return render_template("edit_profile_seller.html",
        name= data[0][1],
        desc = data[0][7],
        mail = data[0][8],
        picture = data[0][9],
        address = data[0][10],
        user = session['name'])



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
            cursor.execute("SELECT profile FROM user_inf WHERE id = {0}".format(session['id']))
            last_file = cursor.fetchone()
            if last_file[0] != "default.png":
                try:
                    os.remove(str(os.path.join(path,last_file[0])))
                    print ('photo deleted')
                except:
                    print ('photo not found')
            filename = secure_filename(file.filename)
            file.save(os.path.join(path,filename))
            picture = filename
            cursor.execute("UPDATE user_inf SET profile  = '{0}' WHERE id = {1}".format(picture,session['id']))
            mydb.commit()
            return redirect(request.url)
    return redirect("edit")

        

@app.route('/profile_display_buyer_order',methods = ['get','post'])
def profile_display_buyer_order():
    data = fetch_information()
    order = fetch_order()
    return render_template("profile_display_buyer_order.html",
    order = order,
    f = data[0][1],
    l = data[0][2],
    d = data[0][3],
    address = data[0][10],
    picture = data[0][9],
    age = data[1])

@app.route('/profile_display_seller_order',methods = ['get','post'])
def profile_display_seller_order():
    order = fetch_order()
    data = fetch_information()
    return render_template("profile_display_seller_order.html",
    order = order,
    name= data[0][1],
    picture = data[0][9])


@app.route('/profile_display_buyer_cafeHis',methods = ['get','post'])
def profile_display_buyer_cafeHis():
    data = fetch_information()
    history = fetch_history()
    return render_template("profile_display_buyer_cafeHis.html",
    history = history,
    f = data[0][1],
    d = data[0][3],
    picture = data[0][9],
    age = data[1])

@app.route('/profile_display_buyer_favorite_details',methods = ['get','post'])
def profile_display_buyer_favorite_details():
    data = fetch_information()
    return render_template("profile_display_buyer_favorite_details.html",
    f = data[0][1],
    l = data[0][2],
    d = data[0][3],
    picture = data[0][9],
    age = data[1])

@app.route('/profile_display_buyer_favorite',methods = ['get','post'])
def profile_display_buyer_favorite():
    data = fetch_information()
    return render_template("profile_display_buyer_favorite.html",
    f = data[0][1],
    l = data[0][2],
    d = data[0][3],
    picture = data[0][9],
    age = data[1])

@app.route('/profile_display_seller_product',methods = ['get','post'])
def profile_display_seller_product():
    data = fetch_information()
    product = fetch_product()
    print(product)
    return render_template("profile_display_seller_product.html",
    product = product,
    name= data[0][1],
    picture = data[0][9])

@app.route('/profile_display_seller_add_product',methods = ['get','post'])
def profile_display_seller_add_product():
    if request.method == 'POST':
        prod_name = request.form.get('prod_name')
        bev_type = request.form.get('type')
        description = request.form.get('desc')
        price = request.form.get('price')
        point = request.form.get('point')
        menu = request.form.get('menu1')
        file = request.files['file']
        print(prod_name,bev_type,description,price,point,menu,file)

        if menu == None:
            cursor.execute("SELECT product_name FROM product_inf WHERE seller = {} AND product_name = '{}' ".format(session['id'],prod_name))
            detail = cursor.fetchall()
            if detail != []:
                for i in detail:
                    if i[0].upper() == prod_name.upper():
                        return "Already have this beverage in your menu"
                    else :
                        print(detail[0])
            if file:
                filename = secure_filename(file.filename)
                picture = filename
                cursor.execute("INSERT INTO product_inf(product_name,tea,descriptions,price,point,seller) VALUES ('{0}',{1},'{2}',{3},{4},{5})".format(prod_name,bev_type,description,price,point,session['id']))
                mydb.commit()
                cursor.execute("UPDATE product_inf SET picture  = '{0}' WHERE product_name = '{1}'".format(picture,prod_name))
                mydb.commit()
                file.save(os.path.join(pathProduct,filename))
        else:
            cursor.execute("SELECT picture FROM product_inf WHERE product_name = '{0}'".format(menu))
            last_file = cursor.fetchone()
            if last_file[0] != "default.png":
                try:
                    os.remove(str(os.path.join(pathProduct,last_file[0])))
                    print ('photo deleted')
                except:
                    print ('photo not found')
            cursor.execute("DELETE FROM product_inf WHERE product_name = '{0}' AND seller = {1}".format(menu,session['id']))
            mydb.commit()
            print ("delete data complete")
    data = fetch_information()
    product = fetch_product()
    return render_template('profile_display_seller_add_product.html',
    bev = product,
    name= data[0][1],
    picture = data[0][9])
    


@app.route('/profile_display_seller_product_details',methods = ['get','post'])
def profile_display_seller_product_details():
    data = fetch_information()
    return render_template("profile_display_seller_product_details.html",
    name= data[0][1],
    desc = data[0][7],
    mail = data[0][8],
    picture = data[0][9],
    address = data[0][10],
    user = session['name'])

@app.route('/seller_point',methods = ['get','post']) 
def seller_point():
    
    if request.method == 'POST':
        menu = [request.form.get("menu1"),request.form.get("menu2"),
        request.form.get("menu3"),request.form.get("menu4"),
        request.form.get("menu5"),request.form.get("menu6"),
        request.form.get("menu7"),request.form.get("menu8"),
        request.form.get("menu9"),request.form.get("menu10")]

        discount = request.form.get("level1")

        collect = []
        for i in menu:
            print(i)
            if i == None:
                continue
            else:
                collect.append(i)
        
        hash = random.getrandbits(128)
        hash = ("%032x" % hash)
        point = []
        point = give_point(collect)
        point.append(session['id'])
        point.append(hash)
        point.append(discount)
        print("point = ", point)
        #check file
        counter = session['id']
        file_name = "qr{0}.png"
        file_name = file_name.format(counter)
        hash_name = hashlib.md5(str(file_name).encode('utf-8'))
        file_name = hash_name.hexdigest()+".png"

        qrcode_img = qrcode.make(point)
        qrcode_img.save(os.path.join(pathQR,file_name))
        print(os.path.join(pathQR,file_name))
        # print(collect)
        # print(level)  
        return render_template('qr_seller.html',qr = file_name)
    data = fetch_information()
    product = fetch_product()
    return render_template('seller_point.html',
    bev = product,
    name= data[0][1],
    picture = data[0][9]) 


@app.route('/home',methods = ['get','post'])
def home():
    return render_template('home.html')   

@app.route('/about_us',methods = ['get','post'])
def about_us():
    return render_template('about_us.html')

@app.route('/profile_display_buyer_point',methods = ['get','post'])
def profile_display_buyer_point():
    data = fetch_information()
    point_details = fetch_point()
    return render_template('profile_display_buyer_point.html',point_details = point_details,
    f = data[0][1],
    d = data[0][3],
    picture = data[0][9],
    age = data[1])

@app.route('/profile_display_buyer_point_redemption',methods = ['get','post'])
def profile_display_buyer_point_redemption():
    data = fetch_information()
    return render_template('profile_display_buyer_point_redemption.html',f = data[0][1],
    d = data[0][3],
    picture = data[0][9],
    point = data[0][11],
    age = data[1])


@app.route('/buyer_get_points',methods = ['get','post'])
def buyer_get_points():
    if request.method == "POST":
        global decoded_info
        f =request.files.get("file")
        filename, extension = f.filename.split(".")
        generated_filename = f".{extension}"
        file_location = os.path.join(app.config['UPLOAD_FOLDER'],generated_filename)
        f.save(file_location)
        img = cv2.imread(file_location)
        det = cv2.QRCodeDetector()
        val, pts , st_code = det.detectAndDecode(img)
        os.remove(file_location)
        decoded_info = val
        print("decoded = ",decoded_info)
    return render_template('buyer_get_points.html')

@app.route('/decode',methods = ['get','post'])
def decode():
    a = decoded_info.strip('][').split(', ')
    info = [eval(x) for x in a]
    discount = (info[-1])
    dis = 0
    redeem = 0
    info.pop()
    bill = (info[-1])
    info.pop()
    seller = (info[-1])
    info.pop()
    j = 1
    quantity = len(info)
    print("info = " ,info)
    if discount == '1':
        print ("discount 10 bath")
        dis = 10
        redeem = 100
    elif discount == '2':
        print ("discount = 20 bath")
        dis = 20
        redeem = 200
    elif discount == '3':
        print ("discount = 30 bath")
        dis = 30
        redeem = 300
    elif discount == '4':
        print ("discount = 40 bath")
        dis = 40
        redeem = 400
    else:
        print ("no discount")
    pay = dis / quantity
    cursor.execute("SELECT points from user_inf where id = {0}".format(session['id']))
    p = cursor.fetchone()
    user_point = p[0]
    if user_point >= redeem:
        cursor.execute("UPDATE user_inf set points = points - {0} WHERE id = {1}".format(redeem,session['id']))
        mydb.commit()
        for i in info:
            cursor.execute("select price from product_inf where product_id = {0}".format(i))
            price = cursor.fetchone()
            print (price)
            print("insert into order_inf (seller_id,customer_id,product_id,bill,pay) VALUES({0},{1},{2},'{3}',{4})".format(seller,session['id'],i,bill + str(j),pay))
            try:
                cursor.execute("insert into order_inf (seller_id,customer_id,product_id,bill,pay) VALUES({0},{1},{2},'{3}',{4})".format(seller,session['id'],i,bill+str(j),pay))
                mydb.commit()
                cursor.execute("UPDATE user_inf SET points = points + (select point from product_inf WHERE product_id ={0}) WHERE id = {1}".format(i,session['id']))
                mydb.commit()
                print ("completed")
            except:
                print ("sql error did you use old QR code ?")
                return render_template('test_decode.html',data ="Qr code is already used")
            finally:
                j +=1
    else:
        return render_template('test_decode.html',data ="Not Enough point !!!!")
    
    return render_template('test_decode.html',data = "Congratulations! Go to see your points")

@app.route('/matchmybeverage',methods = ['get','post'])
def matchmybeverage():
    if request.method == "POST":
        cursor.execute("SELECT * FROM product_inf ORDER BY RAND() LIMIT 3")
        product = cursor.fetchall()
        print (product)    
        return render_template('matchmybeverage.html',product = product)
    return render_template('matchmybeverage.html')



@app.route('/product',methods = ['post'])
def product():
    if request.method == "POST":
        a = request.form['action']
        cursor.execute("SELECT * FROM product_inf WHERE product_name = '{0}'".format(a))
        detail = cursor.fetchall()
        print(detail)
        # data = fetch_information()
        cursor.execute("SELECT firstname,profile,address FROM user_inf WHERE id = {}".format(detail[0][5]))
        data = cursor.fetchall()
        print(data)
        return render_template('product.html',detail = detail,
        f = data[0][0],
        address = data[0][2],
        picture = data[0][1],)

if __name__ == "__main__" :
    app.run(debug=True,host = "0.0.0.0", port=int(os.environ.get("PORT", 5000)))    

