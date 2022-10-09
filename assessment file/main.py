from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
import connect
import uuid


db_connection = None
app = Flask(__name__)

CURRENTTIME = "2022-10-28"


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

        return render_template('register.html', msg_sent=True)
        # return "<h1>Successfully Registered! Please Sign In to Make Booking.</h1>"

    return render_template('register.html', msg_sent=False)


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
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport, CURRENTTIME, CURRENTTIME))

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
                        AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport, CURRENTTIME, CURRENTTIME))
        departures = cur.fetchall()

        return render_template('arrDep.html', arrivals=arrivals, column_names=column_names, departures=departures)

    return render_template('arrDep.html')


@app.route('/booking', methods=['GET', 'POST'])
def flight_booking():
    if request.method == "POST":
        email_address = request.form.get("userid")
        cur = getCursor()
        cur.execute('''SELECT * from passenger
                        WHERE EmailAddress = %s;''', (email_address,))
        passenger = cur.fetchall()
        passenger_id = passenger[0][0]
        return redirect(url_for('display_flight', user_id=passenger_id))

    return render_template('booking.html')

# and request.form.get("book_flight"):


@app.route('/booking/<user_id>', methods=['GET', 'POST'])
def display_flight(user_id):
    cur = getCursor()
    cur.execute(''' SELECT p.PassengerID, p.FirstName, p.LastName, f.FlightID,
                    f.FlightNum, f.FlightDate, f.DepTime, f.ArrTime
                    from passenger as p
                    JOIN  passengerFlight as pf on pf.PassengerID=p.PassengerID 
                    JOIN flight as f on f.FlightID = pf.FlightID 
                    WHERE p.PassengerID = %s
                    AND f.FlightDate > %s
                    ORDER BY f.FlightDate;''', (user_id, CURRENTTIME))
    booking_details = cur.fetchall()
    column_names = [item[0] for item in cur.description]

    cur = getCursor()
    cur.execute('''SELECT * from passenger
                    WHERE PassengerID = %s;''', (user_id,))
    passenger_info = cur.fetchall()
    print(passenger_info)
    col_names = [item[0] for item in cur.description]
    print(col_names)
    return render_template('booking.html', column_names=column_names, booking_details=booking_details, col_names=col_names, passenger_info=passenger_info)


@app.route('/booking/update', methods=['GET', 'POST'])
def update():

    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        passport = request.form.get("passport")
        dob = request.form.get("dob")
        passenger_id = request.form.get("passenger_id")
        # cur = getCursor()
        # cur.execute('''SELECT * from passenger
        #                 WHERE PassengerID = %s;''', (user_id))

        query = '''UPDATE passenger SET FirstName = %s, LastName = %s, EmailAddress = %s, 
                    PhoneNumber = %s, PassportNumber = %s, DateOfBirth = %s
                    where PassengerID = %s;'''
        # passenger_info = cur.fetchall()
        # print(passenger_info)
        # col_names = [item[0] for item in cur.description]
        # print(col_names)
        return redirect(url_for('display_flight', user_id=passenger_id))


@app.route('/booking/<flight_id>', methods=['GET', 'POST'])
def cancel_flight(flight_id):
    if request.method == "POST":
        flightID = request.form.get(flightID)
        print(flightID)


@app.route('/booking/makebooking', methods=['GET', 'POST'])
def book_flight(flight_id):
    pass


if __name__ == "__main__":
    app.run(debug=True)
