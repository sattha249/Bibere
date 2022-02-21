from flask import Flask, render_template

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
    app.run(debug = True)