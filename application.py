from flask import Flask, render_template , request , redirect , session
from flask_session import Session
import mysql.connector
import hashlib

user_name = "root"
passwd = "Codercamp1"

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mydb = mysql.connector.connect(
    host="localhost",
    user=user_name,
    password = passwd ,
    database="bibere"
)
cursor = mydb.cursor(buffered=True)
"""Code to add hash password"""
hash_pass = hashlib.md5(str(passwd).encode('utf-8'))
hash_pass = hash_pass.hexdigest()
try :
    cursor.execute("INSERT INTO user_data (Username,hashpass,client) VALUES  ('sat','{}',True)".format(hash_pass))
    mydb.commit()
except: 
    print("cannot connect")



"""Code example to get hash from sql and check password"""
cursor.execute("SELECT hashpass FROM user_data WHERE id = 2")
c = cursor.fetchone()


"""flask"""

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

        try:
            cursor.execute("SELECT username,hashpass FROM user_data WHERE username = '{}'".format(username))
            login_data = cursor.fetchall()
            if username == login_data[0][0] and password == login_data[0][1]:
                session["name"] = username 
        except:
            return "<h3>Wrong username or password<h3>"
        return redirect("/")
    return render_template("login_buyer.html") 
        
       
    
@app.route('/login_seller',methods =['get','post'])
def login_seller():
    return render_template("login_seller.html") 

@app.route('/sell_register',methods =['get','post'])
def sell_register():
    return render_template("sell_register.html") 

@app.route('/buy_register',methods =['get','post'])
def buy_register():
    return render_template("buy_register.html") 

@app.route('/barNearYou',methods =['get','post'])
def barNearYou():
    return "Bar near you"


if __name__ == "__main__" :
    app.run(debug = False)