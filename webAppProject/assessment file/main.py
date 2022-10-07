from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
import connect
import uuid

dbconn = None
app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)


def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn


def genID():
    return str(uuid.uuid4().fields[1])


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form['userid']

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        firstname = data["firstname"].title()
        lastname = data["lastname"].title()
        email = data["email"]
        phone = data["phone"]
        passport = data["passport"]
        dob = data["dob"]

        return render_template('register.html', msg_sent=True)

    return render_template('register.html', msg_sent=False)


@app.route('/booking', methods=['GET', 'POST'])
def flight_booking():
    return render_template('booking.html')


@app.route('/arrival&departure', methods=['GET', 'POST'])
def arrival_departure():
    return render_template('arrDep.html')
