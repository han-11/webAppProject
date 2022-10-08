from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
import connect
import uuid


db_connection = None
app = Flask(__name__)

CURRENTTIME = "2022-10-28"


def getCursor():
    global dbconn
    global db_connection
    global connection
    if db_connection == None:
        connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn

    else:
        return db_connection


@app.route('/')
def home():

    cur = getCursor()
    cur.execute(
        "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
    airports = cur.fetchall()
    print(airports)
    return render_template('home.html', airports=airports)


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        email = request.form.get('userid')
        cur = getCursor()
        cur.execute(
            "select * from passenger where EmailAddress IN (%s); ", [(email)])
        select_result = cur.fetchall()
        if select_result == []:
            return redirect(url_for('register'))
        else:
            return redirect(url_for('flight_booking'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        data = request.form
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        email = data.get("email")
        phone = data.get("phone")
        passport = data.get("passport")
        dob = data.get("dob")
        print(data)
        cur = getCursor()
        cur.execute('''INSERT INTO passenger(FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth)
                        VALUES (%s,%s,%s,%s,%s,%s);''', (firstname, lastname, email, phone, passport, dob))

        return redirect(url_for('log_in'))

    return render_template('register.html', msg_sent=False)


@app.route('/booking', methods=['GET', 'POST'])
def flight_booking():

    return render_template('booking.html')


@app.route('/arrival&departure', methods=['POST'])
def arrival_departure():
    if request.method == "POST":
        airport = request.form.get("selected_airport")[2:5]
        cur = getCursor()
        cur.execute('''SELECT f.FlightID, r.FlightNum, r.DepCode,  a.AirportName, 
                        f.FlightDate, f.DepTime, f.DepEstAct, f.FlightStatus
                        FROM airline.airport as a 
                        JOIN airline.route as r on r.DepCode = a.AirportCode
                        JOIN airline.flight as f on f.FlightNum = r.FlightNum
                        where r.ArrCode = %s
                        AND f.FlightDate BETWEEN DATE_SUB(%s, INTERVAL 2 DAY) 
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport, '2022-10-28', '2022-10-28'))

        arrivals = cur.fetchall()
        column_names = [item[0] for item in cur.description]
        cur = getCursor()
        cur.execute('''SELECT f.FlightID, r.FlightNum, r.ArrCode,  a.AirportName,  
                        f.FlightDate, f.ArrTime, f.ArrEstAct, f.FlightStatus
                        FROM airport as a 
                        JOIN route as r on r.ArrCode = a.AirportCode
                        JOIN flight as f on f.FlightNum = r.FlightNum
                        where r.DepCode = %s
                        AND f.FlightDate BETWEEN DATE_SUB(%s, INTERVAL 2 DAY) 
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport, '2022-10-28', '2022-10-28'))
        departures = cur.fetchall()

        return render_template('arrDep.html', arrivals=arrivals, column_names=column_names, departures=departures)

    return render_template('arrDep.html')


if __name__ == "__main__":
    app.run(debug=True)
