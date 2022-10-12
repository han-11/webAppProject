from crypt import methods
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
            session['user'] = 'customer'
            return redirect(url_for('booking_info', passenger_id=session['passenger_id']))
        else:
            return redirect(url_for('register'))

    return render_template('login.html')


@ app.route('/register', methods=['GET', 'POST'])
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


@ app.route('/arrival&departure', methods=['POST'])
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


@ app.route('/booking/<string:passenger_id>', methods=['GET', 'POST'])
def booking_info(passenger_id):
    try:
        if session['logged_in'] == True:
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
                                    ORDER BY f.FlightDate;''', (passenger_id, ))
            booking_details = cur.fetchall()
            column_names = [item[0] for item in cur.description]

            cur = getCursor()
            cur.execute(
                "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
            airports = cur.fetchall()
            date_object = datetime.strptime(CURRENTTIME, '%Y-%m-%d').date()
            return render_template('app_info_page.html', passenger_id=session['passenger_id'], passenger_info=passenger_info, col_names=col_names,
                                   column_names=column_names, booking_details=booking_details, airports=airports, currentTime=date_object)
    except:
        return "<h1> Please Sign In or Register to Make Booking.</h1>"


@ app.route('/booking/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        passenger_id = request.form.get('passengerID')
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


@ app.route('/booking/cancel/<string:passenger_id>/<string:flight_id>', methods=['GET', 'POST'])
def cancel(passenger_id, flight_id):

    cur = getCursor()
    cur.execute('''DELETE FROM passengerFlight
                    WHERE FlightID = %s AND PassengerID = %s; ''', (flight_id, passenger_id))
    flash(f" Your Flight {flight_id} Successfully Cancelled!")
    return render_template('app_info_page.html', msg_sent=True)


@ app.route('/booking/flights', methods=['POST'])
def flight_list():
    if request.method == "POST":
        airport_code = request.form.get("selected_airport")[2:5]
        print(airport_code)
        date = request.form.get("flight_date")
        print(date)
        cur = getCursor()
        cur.execute(''' SELECT FlightID, FlightNum, result.AirportName as Departure, a.AirportName as Arrival, 
                FlightDate, DepTime, ArrTime, Duration, Seating, AvailableSeats, FlightStatus, StatusDesc
                from 
                (SELECT a.AirportName, r.ArrCode, r.DepCode, r.FlightNum, f.FlightID, f.FlightDate, f.DepTime, f.ArrTime, f.Duration,
                ac.Seating, sf.BookedSeats, ac.Seating-sf.BookedSeats as AvailableSeats, f.FlightStatus, s.StatusDesc
                FROM airport as a
                JOIN route as r on r.DepCode = a.AirportCode
                JOIN flight as f on f.FlightNum = r.FlightNum
                JOIN aircraft as ac on ac.RegMark = f.Aircraft
                JOIN status as s on  s.FlightStatus = f.FlightStatus
                JOIN
                (SELECT FlightID, COUNT(PassengerID) AS BookedSeats
                FROM airline.passengerFlight
                GROUP BY FlightID) AS sf on sf.FlightID = f.FlightID
                where a.AirportCode = %s
                AND f.FlightDate BETWEEN %s
                AND DATE_ADD(%s , INTERVAL 7 DAY)) AS result
                JOIN airport as a on a.AirportCode = result.ArrCode ; ''', (airport_code, date, date))
        departure_flights = cur.fetchall()
        print(departure_flights)
        column_names = [item[0] for item in cur.description]
        return render_template('booking.html', departures=departure_flights, column_names=column_names)


@ app.route('/booking/confirm/<string:flight_id>', methods=['GET', 'POST'])
def book_flight(flight_id):
    passenger_id = session['passenger_id']
    cur = getCursor()
    cur.execute('''INSERT INTO passengerFlight VALUES (%s, %s);''',
                (flight_id, passenger_id, ))

    flash("Successfully Booked!")
    return render_template('app_info_page.html', msg_sent=True)


@ app.route('/logout')
def log_out():
    session.pop('logged_in', None)
    session.pop('passenger_id', None)
    return redirect(url_for('home'))


@ app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    cur = getCursor()
    cur.execute('''SELECT FirstName, StaffID
                FROM staff;''')
    staffs = cur.fetchall()
    return render_template('admin_login.html', staffs=staffs)


@ app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_form():
    if request.method == 'POST':
        name = request.form.get("staff_id")
        print(name)
        staffid = name
        cur = getCursor()
        cur.execute(
            '''SELECT * FROM staff WHERE StaffID = %s ;''', (staffid, ))
        staff = cur.fetchone()
        print(staff)

        if staff:
            session['logged_in'] = True
            session['user'] = 'admin'
            session['staff_id'] = staff[0]
            session['staff_name'] = staff[1]
            session['is_manager'] = staff[-1]
            print(session['is_manager'])
            return redirect(url_for('admin_home'))
        else:
            flash("Invalid Username or Password")
    return redirect(url_for('admin_login'))


@ app.route('/admin/home', methods=['GET', 'POST'])
def admin_home():
    if session['logged_in'] == True:
        if session['is_manager'] == 1:
            print("is manager")
            return render_template('admin_home.html', is_manager=True)
        else:
            print("is not manager")
            return render_template('admin_home.html', is_manager=False)
    else:
        return redirect(url_for('admin_login'))


@ app.route('/admin/passengers', methods=['GET', 'POST'])
def admin_passengers():
    cur = getCursor()
    cur.execute('''SELECT * FROM passenger ORDER BY LastName, FirstName;''')
    passengers = cur.fetchall()
    column_names = [item[0] for item in cur.description]

    return render_template('admin_passengers.html', passengers=passengers, column_names=column_names)


@ app.route('/admin/add_passenger', methods=['GET', 'POST'])
def add_passenger():
    if request.method == "POST":
        data = request.form
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        email = data.get("email")
        phone = data.get("phone")
        passport = data.get("passport")
        dob = data.get("dob")
        loyalty_tier = data.get("loyalty_tier")
        cur = getCursor()
        cur.execute('''INSERT INTO passenger(FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier)
                        VALUES (%s,%s,%s,%s,%s,%s,%s);''', (firstname, lastname, email, phone, passport, dob, loyalty_tier))
        flash("Passenger Added Successfully!")
    return render_template('admin_passengers.html', msg_sent=True)


@ app.route('/admin/passengerinfo/<string:passenger_id>', methods=['GET', 'POST'])
def passenger_profile(passenger_id):
    if session['logged_in'] == True:
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
                                    ORDER BY f.FlightDate;''', (passenger_id, ))
        booking_details = cur.fetchall()
        print(booking_details)
        column_names = [item[0] for item in cur.description]

        cur = getCursor()
        cur.execute(
            "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
        airports = cur.fetchall()
        date_object = datetime.strptime(CURRENTTIME, '%Y-%m-%d').date()
        return render_template('app_info_page.html', passenger_id=passenger_id, passenger_info=passenger_info, col_names=col_names,
                               column_names=column_names, booking_details=booking_details, airports=airports, currentTime=date_object)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        last_name = request.form['last_name']
        # search by last name
        cur = getCursor()
        cur.execute(
            '''SELECT * FROM passenger WHERE LastName = %s ORDER BY  FirstName;''', (last_name,))
        passengers = cur.fetchall()
        column_names = [item[0] for item in cur.description]

        if len(last_name) == 0:
            cur = getCursor()
            cur.execute(
                '''SELECT * FROM passenger ORDER BY LastName, FirstName;''')
            passengers = cur.fetchall()
            column_names = [item[0] for item in cur.description]
        return render_template('admin_passengers.html', passengers=passengers, column_names=column_names)
    return render_template('search.html', passengers=passengers, column_names=column_names)


@ app.route('/admin/flight_list', methods=['GET', 'POST'])
def admin_flight_list():
    cur = getCursor()
    cur.execute(''' 
                Select DISTINCT(aa.FlightID), aa.FlightNum, aa.WeekNum, aa.FlightDate, aa.DepTime, aa.ArrTime, da.DepartureAirport, 
                aa.ArrivalAirport, aa.MasterRoute, aa.RegMark, aa.Seating, seating.BookedSeats, aa.seating-seating.BookedSeats as SeatsRemain
                FROM
                (SELECT f.FlightID, f.FlightNum, f.WeekNum, r.DepCode, r.ArrCode, a.AirportName as ArrivalAirport, r.MasterRoute,
                f.FlightDate, f.DepTime, f.ArrTime, f.FlightStatus, f.Aircraft, ac.RegMark, ac.Seating
                FROM airline.flight AS f 
                JOIN route as r on r.FlightNum = f.FlightNum
                JOIN aircraft as ac on ac.RegMark = f.Aircraft
                JOIN airport as a on a.AirportCode = r.ArrCode )
                AS aa JOIN 
                ( SELECT f.FlightNum, r.DepCode, ap.AirportName as DepartureAirport
                FROM flight as f
                JOIN route as r on r.FlightNum = f.FlightNum
                JOIN airport as ap on ap.AirportCode = r.DepCode 
                ) AS da on aa.FlightNum = da.FlightNum
                JOIN 
                (SELECT FlightID, COUNT(PassengerID) AS BookedSeats
                FROM airline.passengerFlight
                GROUP BY FlightID) as seating on aa.FlightID = seating.FlightID
                WHERE FlightDate BETWEEN %s
                AND DATE_ADD(%s, INTERVAL 7 DAY)
                ORDER BY FlightDate, DepTime, DepartureAirport; ''', (CURRENTTIME, CURRENTTIME))
    all_flights = cur.fetchall()
    column_names = [item[0] for item in cur.description]

    return render_template('admin_flights.html',  column_names=column_names, all_flights=all_flights,)


@ app.route('/admin_logout')
def admin_logout():
    session.pop('logged_in', None)
    session.pop('staff_id', None)
    session.pop('staff_name', None)
    session.pop('is_manager', None)
    return redirect(url_for('admin_login_form'))


if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
