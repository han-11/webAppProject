from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import mysql.connector
import connect
import uuid
CURRENTTIME = "2022-10-28"

db_connection = None
app = Flask(__name__)
app.secret_key = "secret"


def getCursor():

    global db_connection
    global connection
    if db_connection == None:
        connection = mysql.connector.connect(user=connect.dbuser, password=connect.dbpass, host=connect.dbhost,
                                             database=connect.dbname, autocommit=True)
        db_connection = connection.cursor()
        return db_connection

    else:
        return db_connection


@app.route('/')
def home():
    cur = getCursor()
    cur.execute(
        "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
    airports = cur.fetchall()
    return render_template('home.html', airports=airports)


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        email = request.form.get('userid')
        cur = getCursor()
        cur.execute(
            "select * from passenger where EmailAddress = %s; ", (email,))
        passenger = cur.fetchall()

        if passenger:
            passenger_id = passenger[0][0]
            session['logged_in'] = True
            session['passenger_id'] = passenger_id
            return redirect(url_for('display_info'))
        else:
            return redirect(url_for('register'))

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
        cur = getCursor()
        cur.execute('''INSERT INTO passenger(FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth)
                        VALUES (%s,%s,%s,%s,%s,%s);''', (firstname, lastname, email, phone, passport, dob))

        return render_template('register.html', msg_sent=True)
        # return "<h1>Successfully Registered! Please Sign In to Make Booking.</h1>"

    return render_template('register.html', msg_sent=False)


@app.route('/arrival&departure', methods=['POST'])
def arrival_departure():
    if request.method == 'POST':
        airport_code = request.form.get("selected_airport")[2:5]
        cur = getCursor()
        cur.execute('''SELECT f.FlightID, r.FlightNum, r.DepCode,  a.AirportName,
                        f.FlightDate, f.DepTime, f.DepEstAct, f.FlightStatus
                        FROM airline.airport as a
                        JOIN airline.route as r on r.DepCode = a.AirportCode
                        JOIN airline.flight as f on f.FlightNum = r.FlightNum
                        where r.ArrCode = %s
                        AND f.FlightDate BETWEEN DATE_SUB(%s, INTERVAL 2 DAY)
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport_code, CURRENTTIME, CURRENTTIME))

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
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport_code, CURRENTTIME, CURRENTTIME))
        departures = cur.fetchall()

        return render_template('arrDep.html', arrivals=arrivals, column_names=column_names, departures=departures)

    return render_template('arrDep.html')


# @app.route('/booking/<user_id>', methods=['GET', 'POST'])
# def flight_booking(user_id):
#     if request.method == "POST":

#         return redirect(url_for('display_info', user_id=passenger_id))

#     return render_template('booking.html')

# and request.form.get("book_flight"):


@app.route('/booking', methods=['GET', 'POST'])
def display_info():
    passenger_id = session['passenger_id']
    cur = getCursor()
    cur.execute('''SELECT * from passenger
                            WHERE PassengerID = %s;''', (passenger_id,))
    passenger_info = cur.fetchall()
    col_names = [item[0] for item in cur.description]

    cur = getCursor()
    cur.execute(''' SELECT p.PassengerID, p.FirstName, p.LastName, f.FlightID,
                            f.FlightNum, f.FlightDate, f.DepTime, f.ArrTime
                            from passenger as p
                            JOIN  passengerFlight as pf on pf.PassengerID=p.PassengerID
                            JOIN flight as f on f.FlightID = pf.FlightID
                            WHERE p.PassengerID = %s
                            AND f.FlightDate > %s
                            ORDER BY f.FlightDate;''', (passenger_id, CURRENTTIME))
    booking_details = cur.fetchall()
    column_names = [item[0] for item in cur.description]

    cur = getCursor()
    cur.execute(
        "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
    airports = cur.fetchall()

    return render_template('app_info_page.html', passenger_id=session['passenger_id'], passenger_info=passenger_info, col_names=col_names,
                           column_names=column_names, booking_details=booking_details, airports=airports)


@ app.route('/booking/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        passenger_id = session['passenger_id']
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        passport = request.form.get("passport")
        dob = request.form.get("dob")
        print(passenger_id, firstname, lastname, email, phone, passport, dob)
        cur = getCursor()
        cur.execute('''UPDATE passenger SET FirstName = %s, LastName = %s, EmailAddress = %s,
                    PhoneNumber = %s, PassportNumber = %s, DateOfBirth = %s
                    where PassengerID = %s;''', (firstname, lastname, email, phone, passport, dob, passenger_id))
        flash("Successfully Updated!")
        return render_template('app_info_page.html', msg_sent=True)

    return render_template('app_info_page.html', msg_sent=False)


@ app.route('/booking/cancelbooking', methods=['GET', 'POST'])
def cancel_flight():
    if request.method == "POST":

        pass


@ app.route('/booking/flights', methods=['POST'])
def book_flight():
    if request.method == "POST":
        airport_code = request.form.get("selected_airport")[2:5]
        date = request.form.get("date")
        cur = getCursor()
        cur.execute('''SELECT a.AirportName, r.FlightNum, f.FlightID,
                    f.FlightDate, f.DepTime, f.ArrTime, f.Duration, ac.Seating, f.FlightStatus, s.StatusDesc
                    FROM airport as a
                    JOIN route as r on r.DepCode = a.AirportCode
                    JOIN flight as f on f.FlightNum = r.FlightNum
                    JOIN aircraft as ac on ac.RegMark = f.Aircraft
                    JOIN status as s on  s.FlightStatus = f.FlightStatus
                    where a.AirportCode = %s
                    AND f.FlightDate BETWEEN %s
                    AND DATE_ADD(%s, INTERVAL 7 DAY); ''', (airport_code, date, date))
        departures = cur.fetchall()
        column_names = [item[0] for item in cur.description]
        return render_template('booking.html', departures=departures, column_names=column_names)


@ app.route('/booking/confirm', methods=['POST'])
def confirm():
    if request.method == "POST":
        passenger_id = session['passenger_id']
        flight_id = request.form.get("flight_id")
        cur = getCursor()
        cur.execute('''INSERT INTO passengerFlight (PassengerID, FlightID)
                    VALUES (%s, %s);''', (passenger_id, flight_id))
        flash("Successfully Booked!")
        return render_template('info_page.html', msg_sent=True)

    return render_template('info_page.html', msg_sent=False)


@app.route('/booking/cancel', methods=['POST'])
def cancel():
    pass


@app.route('/logout')
def log_out():
    session.pop('logged_in', None)
    session.pop('passenger_id', None)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
