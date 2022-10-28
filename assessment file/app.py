#     Name: Hanbing Wang Heather
#      Student ID: 1153195

from crypt import methods
from os import curdir
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import mysql.connector
from mysqlx import DataError, IntegrityError
import connect

# Set current time as "2022-10-28"
CURRENTTIME = "2022-10-28"


app = Flask(__name__)
# secret key for session
app.secret_key = "secret"
db_connection = None

# function for sql connection


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


# home route, renturn landing page, allow user to login and check arrival and departure flights
@app.route('/')
def home():
    cur = getCursor()
    cur.execute('''SELECT DISTINCT AirportCode, AirportName FROM airport
                    JOIN route on route.DepCode = airport.AirportCode;''')
    airports = cur.fetchall()
# query to get all airports from database
    return render_template('home.html', airports=airports)

# use customer id to check if the customer is in the database, if not, return register page


@app.route('/login', methods=['POST'])
def log_in():
    if request.method == 'POST':
        email = request.form.get('userid')
        cur = getCursor()
        cur.execute(
            "select * from passenger where EmailAddress = %s; ", (email,))
        passenger = cur.fetchall()
# check if the customer is in the database
        if passenger:
            passenger_id = passenger[0][0]
            session['logged_in'] = True
            session['passenger_id'] = passenger_id
            session['user'] = 'customer'
# allow customer to make bookings after login
            return redirect(url_for('booking_info', passenger_id=session['passenger_id']))
# direct user to register page if the customer is not in the database
        else:

            return redirect(url_for('register'))
    else:
        flash('Please enter your email address')
        return redirect(url_for('home'))


#  register page, allow user to register as a new customer


@ app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        try:
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
    # if user submit the form, return message says registration is successful and direct user to login page
            return render_template('register.html', msg_sent=True)
        except mysql.connector.errors.DataError:
            flash('There are some errors in your input, please check again')
            return redirect(url_for('register'))

    return render_template('register.html', msg_sent=False)


# Shows appropriate arrivals and departures information for a selected airport from 2 days before the current day to 5 days after the current day.
@ app.route('/arrival&departure', methods=['GET', 'POST'])
def arrival_departure():
    # get the airport code from the form on the home page
    airport_code = request.form.get("selected_airport")
    cur = getCursor()
    cur.execute('''SELECT f.FlightID, r.FlightNum, r.DepCode,  a.AirportName,
                    f.FlightDate, f.DepTime, f.DepEstAct, f.FlightStatus
                    FROM airport as a
                    JOIN route as r on r.DepCode = a.AirportCode
                    JOIN flight as f on f.FlightNum = r.FlightNum
                    where r.ArrCode = %s
                    AND f.FlightDate BETWEEN DATE_SUB(%s, INTERVAL 2 DAY)
                    AND DATE_ADD(%s, INTERVAL 5 DAY) ;''', (airport_code, CURRENTTIME, CURRENTTIME))
# query result for arrival flights
    arrivals = cur.fetchall()
# column names for columns in the table
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
# query result for departure flights
    departures = cur.fetchall()
    return render_template('arrDep.html', arrivals=arrivals, column_names=column_names, departures=departures)

# webpage to show customer's personal details, booking list,  allow customer to make booking and cancel booking


@ app.route('/booking', methods=['GET', 'POST'])
def booking_info():

    if session['logged_in'] == True:
        passenger_id = session['passenger_id']
        cur = getCursor()
        cur.execute('''SELECT * from passenger
                                WHERE PassengerID = %s;''', (passenger_id,))
        passenger_info = cur.fetchall()
        col_names = [item[0] for item in cur.description]
# if customer has made booking, show the booking list
        cur = getCursor()
        cur.execute(''' SELECT p.PassengerID, p.FirstName, p.LastName,f.FlightID, f.FlightNum, f.FlightDate, airportname.Departures, 
                    airportname.Arrivals, f.DepTime, f.ArrTime
                    from passenger as p
                    JOIN  passengerFlight as pf on pf.PassengerID=p.PassengerID
                    JOIN flight as f on f.FlightID = pf.FlightID
                    JOIN route as r on r.FlightNum = f.FLightNum
                    JOIN 
                    (SELECT 
                    j.FlightNum, j.Departures, a.AirportName AS Arrivals 
                    from
                    ( SELECT r.FlightNum, a.AirportName AS Departures, r.ArrCode
                    FROM route as r
                    JOIN airport as a ON r.DepCode = a.AirportCode ) as j
                    JOIN airport as a on j.ArrCode = a.AirportCode ) as airportname
                    on airportname.FlightNum = f.FlightNum
                    WHERE p.PassengerID = %s
                    ORDER BY f.FlightDate;''', (passenger_id, ))
        booking_details = cur.fetchall()
        column_names = [item[0] for item in cur.description]
        cur = getCursor()
        cur.execute(
            "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
        airports = cur.fetchall()
        date_object = datetime.strptime(CURRENTTIME, '%Y-%m-%d').date()
        return render_template('customer_info_page.html', passenger_id=session['passenger_id'], passenger_info=passenger_info, col_names=col_names,
                               column_names=column_names, booking_details=booking_details, airports=airports, currentTime=date_object)


# function to allow customer to edit their personal details
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
        loyalty = request.form.get("loyalty")
        print(loyalty)
        cur = getCursor()
        cur.execute('''UPDATE passenger SET FirstName = %s, LastName = %s, EmailAddress = %s,
                    PhoneNumber = %s, PassportNumber = %s, DateOfBirth = %s, LoyaltyTier = %s
                    where PassengerID = %s;''', (firstname, lastname, email, phone, passport, dob, loyalty, passenger_id))
        print(cur.statement)
#  flask message to show the update is successful
        flash("Successfully Updated!")
        return render_template('customer_info_page.html', msg_sent=True)

    return render_template('customer_info_page.html', msg_sent=False)


# function to allow customer to cancel their booking which after the current date
@ app.route('/booking/cancel/<string:passenger_id>/<string:flight_id>', methods=['GET', 'POST'])
def cancel(passenger_id, flight_id):
    cur = getCursor()
    cur.execute('''DELETE FROM passengerFlight
                    WHERE FlightID = %s AND PassengerID = %s; ''', (flight_id, passenger_id))
    flash(f" Your Flight {flight_id} Successfully Cancelled!")
    return render_template('customer_info_page.html', msg_sent=True)


# function to allow customer to make booking
@ app.route('/booking/flights/<string:passenger_id>', methods=['POST'])
def flight_list(passenger_id):
    if request.method == "POST":
        airport_name = request.form.get("selected_airport")
        # get the selected date from the form
        date = request.form.get("flight_date")
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
                FROM passengerFlight
                GROUP BY FlightID) AS sf on sf.FlightID = f.FlightID
                where a.AirportName = %s
                AND f.FlightDate BETWEEN %s
                AND DATE_ADD(%s , INTERVAL 7 DAY)) AS result
                JOIN airport as a on a.AirportCode = result.ArrCode ; ''', (airport_name, date, date))
# get all the departue flights from the selected airport and for the date between the selected date and 7 days after
        departure_flights = cur.fetchall()
        column_names = [item[0] for item in cur.description]
        return render_template('booking.html', departures=departure_flights, column_names=column_names, passenger_id=passenger_id)


# let the user to confirm the flight information to book
@ app.route('/booking/confirm/<string:passenger_id>/<string:flight_id>', methods=['GET', 'POST'])
def book_flight(passenger_id, flight_id):
    # send message to the user to confirm the flight booked successfully
    try:
        cur = getCursor()
        cur.execute('''INSERT INTO passengerFlight VALUES (%s, %s);''',
                    (flight_id, passenger_id, ))
        flash(f"Successfully Booked Flight {flight_id}!")
        return render_template('customer_info_page.html', msg_sent=True, passenger_id=passenger_id)
        # send a message if customer has already booked the flight
    except mysql.connector.errors.IntegrityError:
        flash(
            f"You have already booked Flight {flight_id}! Please choose another flight.")
        return render_template('customer_info_page.html', msg_sent=True)


# function to allow customer to logout and terminate the session
@ app.route('/logout')
def log_out():
    session.pop('logged_in', None)
    session.pop('passenger_id', None)
    return redirect(url_for('home'))


# admin home page to be reached by the admin typing on the end of the home page
# display login function for admin, allow admin choose their name from a list, no password required
@ app.route('/admin', methods=['GET'])
def admin_login():
    cur = getCursor()
    cur.execute('''SELECT FirstName, StaffID
                FROM staff;''')
    staffs = cur.fetchall()
    return render_template('admin_login.html', staffs=staffs)


# check staff level and get staff identity
@ app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_form():
    if request.method == 'POST':
        name = request.form.get("staff_id")

        staffid = name
        cur = getCursor()
        cur.execute(
            '''SELECT * FROM staff WHERE StaffID = %s ;''', (staffid, ))
        staff = cur.fetchone()

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


# staff level is shown on the page, manager has more access than the staff
# two portals for passenger and flight list
@ app.route('/admin/home', methods=['GET', 'POST'])
def admin_home():
    if session['logged_in'] == True:
        if session['is_manager'] == 1:
            return render_template('admin_home.html', is_manager=True)
        else:
            return render_template('admin_home.html', is_manager=False)
    else:
        return redirect(url_for('admin_login'))


#  show passenger list for the admin to check
@ app.route('/admin/passengers', methods=['GET', 'POST'])
def admin_passengers():
    cur = getCursor()
    cur.execute('''SELECT * FROM passenger ORDER BY LastName, FirstName;''')
    passengers = cur.fetchall()
    column_names = [item[0] for item in cur.description]

    return render_template('admin_passengers.html', passengers=passengers, column_names=column_names)


#  function to allow admin to add new passenger
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


# function to allow admin to edit passenger information by clicking on passenger id
# this function shared the same html page with customer portal
@ app.route('/admin/passengerinfo/<string:passenger_id>', methods=['GET', 'POST'])
def passenger_profile(passenger_id):
    if session['logged_in'] == True:
        cur = getCursor()
        cur.execute('''SELECT * from passenger
                                    WHERE PassengerID = %s;''', (passenger_id,))
        passenger_info = cur.fetchall()
        col_names = [item[0] for item in cur.description]

        cur = getCursor()
        cur.execute(''' SELECT p.PassengerID, p.FirstName, p.LastName,f.FlightID, f.FlightNum, f.FlightDate, airportname.Departures, 
                        airportname.Arrivals,  f.DepTime, f.ArrTime
                        from passenger as p
                        JOIN  passengerFlight as pf on pf.PassengerID=p.PassengerID
                        JOIN flight as f on f.FlightID = pf.FlightID
                        JOIN route as r on r.FlightNum = f.FLightNum
                        JOIN 
                        (SELECT 
                        j.FlightNum, j.Departures, a.AirportName AS Arrivals 
                        from
                        ( SELECT r.FlightNum, a.AirportName AS Departures, r.ArrCode
                        FROM route as r
                        JOIN airport as a ON r.DepCode = a.AirportCode ) as j
                        JOIN airport as a on j.ArrCode = a.AirportCode ) as airportname
                        on airportname.FlightNum = f.FlightNum
                        WHERE p.PassengerID = %s
                        ORDER BY f.FlightDate;''', (passenger_id, ))
        booking_details = cur.fetchall()
        column_names = [item[0] for item in cur.description]

        cur = getCursor()
        cur.execute(
            "SELECT DISTINCT  AirportCode, AirportName FROM airport JOIN route on route.DepCode = airport.AirportCode;")
        airports = cur.fetchall()
        date_object = datetime.strptime(CURRENTTIME, '%Y-%m-%d').date()
        return render_template('customer_info_page.html', passenger_id=passenger_id, passenger_info=passenger_info, col_names=col_names,
                               column_names=column_names, booking_details=booking_details, airports=airports, currentTime=date_object)


# allow admin to search passenger by lastname
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        last_name = request.form['last_name']
        # search by last name
        cur = getCursor()
        cur.execute(
            '''SELECT * FROM passenger WHERE LastName LIKE %s
                ORDER BY LastName, FirstName;''', ("%" + last_name + "%", ))
        print(cur.statement)
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


# display flight list, sorted by flight date, time and departure airport
@ app.route('/admin/flight_list', methods=['GET', 'POST'])
def admin_flight_list():
    cur = getCursor()
    cur.execute(''' Select DISTINCT(aa.FlightID), aa.FlightNum, aa.WeekNum, aa.FlightDate, aa.DepTime AS DepartureTime, aa.ArrTime AS ArrivalTime, aa.DepEstAct AS EstimatedDeparture, aa.ArrEstAct AS EstimatedArival, da.DepartureAirport,
                aa.ArrivalAirport, aa.MasterRoute, aa.RegMark,seating.BookedSeats, aa.seating-seating.BookedSeats as SeatsRemain, aa.Seating, aa.FlightStatus
                FROM
                (SELECT f.FlightID, f.FlightNum, f.WeekNum, r.DepCode, r.ArrCode, a.AirportName as ArrivalAirport, r.MasterRoute,
                f.FlightDate, f.DepTime, f.ArrTime,f.DepEstACT, f.ArrEstAct, f.FlightStatus, f.Aircraft, ac.RegMark, ac.Seating
                FROM flight AS f
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
                FROM passengerFlight
                GROUP BY FlightID) as seating on aa.FlightID = seating.FlightID
                WHERE FlightDate BETWEEN %s
                AND DATE_ADD(%s, INTERVAL 7 DAY)
                ORDER BY FlightDate, DepTime, DepartureAirport; ''', (CURRENTTIME, CURRENTTIME))
#  By default, the flight list shows flights to and from all airports up to 7 days from current time.
    column_names = [item[0] for item in cur.description]
    numrows = int(cur.rowcount)
    all_flights = cur.fetchall()
    flight_dates = [flight[3]for flight in all_flights]
    date_from = min(flight_dates)
    date_to = max(flight_dates)

    cur.execute('''SELECT DISTINCT (AirportName) FROM airport
                    JOIN route as r on r.DepCode = airport.AirportCode;''')
    all_airports = cur.fetchall()
    airport_names = [airport[0] for airport in all_airports]

    cur.execute('''SELECT DISTINCT(FlightStatus) FROM flight;''')
    all_flight_status = cur.fetchall()
    all_status = sorted([item[0] for item in all_flight_status])

    cur.execute('''SELECT DISTINCT(Aircraft) FROM flight;''')
    all_regmarks = cur.fetchall()
    regmarks = sorted([reg[0] for reg in all_regmarks])
    return render_template('admin_flights.html',  column_names=column_names, all_flights=all_flights,
                           airport_names=airport_names, all_status=all_status, regmarks=regmarks,
                           date_from=date_from, date_to=date_to)


# filter function for seatch flight by departure airport
@ app.route('/admin/flight_search', methods=['GET', 'POST'])
def flight_search():
    if request.method == 'POST':
        departure = request.form.get('departure')
        if departure == '':
            return redirect(url_for('admin_flight_list'))
        else:
            cur = getCursor()
            cur.execute(''' SELECT * FROM
                (Select DISTINCT(aa.FlightID), aa.FlightNum, aa.WeekNum, aa.FlightDate,aa.DepTime AS DepartureTime, aa.ArrTime AS ArrivalTime, 
                aa.DepEstAct AS EstimatedDeparture, aa.ArrEstAct AS EstimatedArival,  da.DepartureAirport,
                aa.ArrivalAirport, aa.MasterRoute, aa.RegMark, seating.BookedSeats, aa.seating-seating.BookedSeats as SeatsRemain,
                aa.Seating, aa.FlightStatus
                FROM
                (SELECT f.FlightID, f.FlightNum, f.WeekNum, r.DepCode, r.ArrCode, a.AirportName as ArrivalAirport, r.MasterRoute,
                f.FlightDate, f.DepTime, f.ArrTime, f.DepEstACT, f.ArrEstAct, f.FlightStatus, f.Aircraft, ac.RegMark, ac.Seating
                FROM flight AS f
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
                FROM passengerFlight
                GROUP BY FlightID) as seating on aa.FlightID = seating.FlightID
                WHERE FlightDate BETWEEN %s
                AND DATE_ADD(%s, INTERVAL 7 DAY)
                ORDER BY FlightDate, DepTime, DepartureAirport) AS all_flights
                WHERE DepartureAirport =  %s
                ; ''', (CURRENTTIME, CURRENTTIME, departure, ))

            searched_flights = cur.fetchall()
            column_names = [item[0] for item in cur.description]

            cur.execute('''SELECT DISTINCT (AirportName) FROM airport
                    JOIN route as r on r.DepCode = airport.AirportCode;''')
            all_airports = cur.fetchall()
            airport_names = [airport[0] for airport in all_airports]
            print(airport_names)

            cur.execute('''SELECT DISTINCT(FlightStatus) FROM flight;''')
            all_flight_status = cur.fetchall()
            all_status = sorted([item[0] for item in all_flight_status])
            print(all_status)

            cur.execute('''SELECT DISTINCT(Aircraft) FROM flight;''')
            all_regmarks = cur.fetchall()
            regmarks = sorted([reg[0] for reg in all_regmarks])

            return render_template('admin_flights.html',  column_names=column_names, all_flights=searched_flights,
                                   airport_names=airport_names, all_status=all_status, regmarks=regmarks,)


# filter function to search flight by flight date
@ app.route('/admin/flight_date_search', methods=['GET', 'POST'])
def flight_date_search():

    if request.method == 'POST':
        search_word = request.form.get('search_word')
        if search_word == '':
            return redirect(url_for('admin_flight_list'))
        else:
            from_date = request.form.get('from_date')
            to_date = request.form.get('to_date')
            cur = getCursor()
            cur.execute(''' SELECT * FROM
                (Select DISTINCT(aa.FlightID), aa.FlightNum, aa.WeekNum, aa.FlightDate,aa.DepTime AS DepartureTime, aa.ArrTime AS ArrivalTime, 
                aa.DepEstAct AS EstimatedDeparture, aa.ArrEstAct AS EstimatedArival,  da.DepartureAirport,
                aa.ArrivalAirport, aa.MasterRoute, aa.RegMark, seating.BookedSeats, aa.seating-seating.BookedSeats as SeatsRemain,
                aa.Seating, aa.FlightStatus
                FROM
                (SELECT f.FlightID, f.FlightNum, f.WeekNum, r.DepCode, r.ArrCode, a.AirportName as ArrivalAirport, r.MasterRoute,
                f.FlightDate, f.DepTime, f.ArrTime, f.DepEstACT, f.ArrEstAct, f.FlightStatus, f.Aircraft, ac.RegMark, ac.Seating
                FROM flight AS f
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
                FROM passengerFlight
                GROUP BY FlightID) as seating on aa.FlightID = seating.FlightID
                WHERE FlightDate BETWEEN %s
                AND DATE_ADD(%s, INTERVAL 7 DAY)
                ORDER BY FlightDate, DepTime, DepartureAirport) AS all_flights
                WHERE FlightDate between %s and %s
                ; ''', (CURRENTTIME, CURRENTTIME, from_date, to_date))

            searched_flights = cur.fetchall()
            column_names = [item[0] for item in cur.description]

    return render_template('admin_flights.html',  column_names=column_names, all_flights=searched_flights, )


# show all passengers for selected flight, the list is numbered in order
# admin can click passenger's id to check passenger's profile, including all flights he/she has booked, edit passenger's details, and make booking for him/her
@ app.route('/admin/flight_info/<string:flight_id>', methods=['GET', 'POST'])
def flight_info(flight_id):
    cur = getCursor()
    cur.execute("SET @row_number:=0;")
    cur.execute('''SELECT (@row_number:=@row_number+1) AS Number,FlightID,
                PassengerID, FirstName, LastName ,  FlightDate, SeatCapacity FROM
                (SELECT f.FlightID, f.FlightDate, a.Seating AS SeatCapacity,
                p.PassengerID, p.FirstName, p.LastName
                FROM flight as f
                JOIN aircraft as a on f.Aircraft = a. RegMark
                JOIN passengerFlight as pf on pf.FlightID = f.FlightID
                JOIN passenger as p on p.PassengerID = pf.PassengerID
                WHERE f.FlightID = %s
                ORDER BY LastName, FirstName) as flightinfo;''', (flight_id, ))
    flight_info = cur.fetchall()
    columns = [item[0] for item in cur.description]
    return render_template('admin_flights.html', flight_id=flight_id, columns=columns, flight_info=flight_info)


# allow manager to add new flight individually
@ app.route('/admin/add_flight', methods=['GET', 'POST'])
def add_flight():
    if request.method == 'POST':
        flight_num = request.form.get('flight_num')
        week_num = request.form.get('week_num')
        flight_date = request.form.get('flight_date')
        deptime = request.form.get('deptime')
        deptime_object = datetime.strptime(deptime, '%H:%M:%S')
        arrtime = request.form.get('arrtime')
        arrtime_object = datetime.strptime(arrtime, '%H:%M:%S')
        duration = arrtime_object - deptime_object
        aircraft = request.form.get('regmark')
        cur = getCursor()
        cur.execute('''SET FOREIGN_KEY_CHECKS = 0;''')
        cur.execute('''INSERT INTO flight
                    (FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration,
                    DepEstAct, ArrEstAct, FlightStatus, Aircraft)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);''',
                    (flight_num, week_num, flight_date, deptime_object,
                        arrtime_object, duration, deptime_object, arrtime_object, 'On time', aircraft))
        cur.execute('''SET FOREIGN_KEY_CHECKS = 1;''')
        flash("New Flight Added")
    return redirect(url_for('display_all_flights'))


#  allow manager to copy all flights which copied from latest week
@ app.route('/admin/add_all_flights', methods=['GET', 'POST'])
def add_all_flights():
    if request.method == 'POST':
        cur = getCursor()
        cur.execute('''SET FOREIGN_KEY_CHECKS = 0;''')
        cur.execute('''INSERT INTO flight
                        (FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration,
                        DepEstAct, ArrEstAct, FlightStatus, Aircraft)
                        SELECT FlightNum, WeekNum+1, date_add(FlightDate, interval 7 day),
                        DepTime, ArrTime, Duration, DepTime, ArrTime, 'On time', Aircraft
                        FROM flight
                        WHERE WeekNum = (SELECT MAX(WeekNum) FROM flight);''')
        cur.execute('''SET FOREIGN_KEY_CHECKS = 1;''')
        flash("Successfully added all flights from last week")
        return redirect(url_for('display_all_flights'))
    return redirect(url_for('admin_flight_list'))


# display all existing flights after the manager added flights
@ app.route('/admin/all_flights', methods=['GET', 'POST'])
def display_all_flights():
    cur = getCursor()
    cur.execute(
        '''Select * from flight ORDER BY WeekNum DESC, FlightDate ASC ; ''')
    flights = cur.fetchall()
    print(flights)
    column_names = [item[0] for item in cur.description]
    return render_template('all_flights.html', column_names=column_names, flights=flights, )


# allow staff to edit flight details, while staff can only edit flight status and estimated/arrival time
@ app.route('/admin/edit_flight/<string:flight_id>', methods=['GET', 'POST'])
def edit_flight(flight_id):
    if request.method == 'POST':
        aircraft = request.form.get('regmark')
        flight_date = request.form.get('flight_date')
        flight_num = request.form.get('flight_num')
        week_num = request.form.get('week_num')
        deptime = request.form.get('deptime')
        deptime_object = datetime.strptime(deptime, '%H:%M:%S')
        arrtime = request.form.get('arrtime')
        arrtime_object = datetime.strptime(arrtime, '%H:%M:%S')
        duration = arrtime_object - deptime_object
        depest = request.form.get('estdep')
        depest_object = datetime.strptime(depest, '%H:%M:%S')
        arrest = request.form.get('estarr')
        arrest_object = datetime.strptime(arrest, '%H:%M:%S')
        status = request.form.get('status')
        print(status)
        cur = getCursor()
        cur.execute('''UPDATE flight
                    SET FlightNum = %s, WeekNum = %s, FlightDate = %s, DepTime = %s, ArrTime = %s, Duration = %s,
                    DepEstAct = %s, ArrEstAct = %s, FlightStatus = %s, Aircraft = %s
                    WHERE FlightID = %s;''',
                    (flight_num, week_num, flight_date, deptime_object,
                        arrtime_object, duration, depest_object, arrest_object, status, aircraft, flight_id))

        return redirect(url_for('admin_flight_list', msg_sent=True))


# function to allow admin to logout
@ app.route('/admin_logout')
def admin_logout():
    session.pop('logged_in', None)
    session.pop('staff_id', None)
    session.pop('staff_name', None)
    session.pop('is_manager', None)
    return redirect(url_for('admin_login_form'))


# fuction to run the app automatically after each change saved, and debug function is on
if __name__ == "__main__":
    app.secret_key = "secret"
    app.run(debug=True)
