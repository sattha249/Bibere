from flask import Flask, render_template
import mysql.connector
import hashlib

user_name = "root"
passwd = "Codercamp1"
passwdd = "Codercamp2"

mydb = mysql.connector.connect(
    host="localhost",
    user=user_name,
    password = passwd ,
    database="bibere"
)
cursor = mydb.cursor()
"""Code to add hash password"""
hash_pass = hashlib.md5(str(passwdd).encode('utf-8'))
hash_pass = hash_pass.hexdigest()
cursor.execute("INSERT INTO user_data (Username,hashpass,client) VALUES  ('sattha','{}',True)".format(hash_pass))
mydb.commit()

"""Code example to get hash from sql and check password"""
cursor.execute("SELECT hashpass FROM user_data WHERE id = 2")
c = cursor.fetchone()
print(c[0])
if (c[0] == hash_pass):
    print("true")
else:
    print("false")


"""flask"""
app = Flask(__name__)

@app.route('/')
def index():
    return "หน้านี้แสดง log-in (default เป็น client)"

@app.route('/profile/<name>')
def profile(name):
    return "หน้านี้แสดง profile ของ {}".format(name)

@app.route('/barNearYou')
def barNearYou():
    return "Bar near you"


if __name__ == "__main__" :
    app.run(debug = False)