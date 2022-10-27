This project is an airline management system, required by the assessment of Mocomp636, It manages customer bookings, flights, routes, airports and aircraft.

 Using Python and HTML language, this website consists of two main parts: a public area for customers to look up flight details and book flights, and an administration area for staff to add and edit flight details, bookings and passenger information.

Customer Portal contains: 

1. Landing Page. On this page, users can check arrivals and departures information from 2 days before to 5 days aafter the current day.Customers must login to make booking and check their own profiles. If it's a new customer, the login system will jump to register page allowing customer to sign up.
 
  The home route returns home.html as landing page, once opened, there are two routes login_in and arrival_departure included on this page, if there is no reault returned from sql query, the page will direct to register page instead.
  
2.  Once logged in, cutomer will see their passenger id on the top of web page, a log out button allows cutomer to log out and terminate this session easily.  There is a drop down list of available departure airports and date picker on the top, customer can choose airport and date to make new booking. The second part is passenger's personal information including their By clicking the update button, customer can update their personal details in a modal.
 
 customer_info_page.html is heavy coded, there are three fuctions on this page. The function booking_info returns customers passenger deatails and booking information from sql query.
  
  
 Admin Portal's functions are :
 
1. The admin page allows staff log in to manage passenger's and flight's schedule. This is page can only get access by "GET" method.
   Once logged in, staff's level will be shown on the left corner. 

2. Once the staff logged in, there will be two portals diaplayed on admin/home page, the two portals are passenger portal and flights portal.

3. The passenger portal displays all the customers information of the airline company, there is a search bar above of the passenger list, admin can search passengers by their last name. Admin can also add new passenger into system on this page, by clicking "Add Passenger" button, there will be a flask form to collect new passenger's information and pass it back to app.py.

4. The flight portal displays all the fligts on the admin/flight page, there is a search function which can search flights by choosing departure airport.

5. Admin can check the passengers list, seating capacity, and other details of each flight by clicking the flight id.
 
6. By clicking each passenger's id, admin will be able to check passenger's information, this function will share the same route with the customer's session. Using "GET" method, the passenger and flight id can be passed by the link, using information in the link, admin can edit passenger's detail, cancel passenger's booking, and make booking for the selected passenger.

7.  Admin can edit flight information on the flight list, manager can edit all the details of a flight while manager can edit all details of a flight.

8. If the staff level is manager, there will be a button displayed on the page allows manager to add new flights. By clicking the button, manager can either new individual flight or copy all the flights from latest week.



Assumption:

1. Assuming admin and user can use the same path to manage customer's profile, such as update customer profile, cancel flight, or make new booking for customer. However, it turns out that I used the session['passenger_id'] to pass the passenger_id value during customer session, which makes it's difficult to share same function and route between customer and admin. 


2. For the function that allows admin to filter flight list in admin portal, assumption is that I can combine both date range and departure airport query as one query, however I have some issue with using where and condition in mysql query, so I have to seperate the two filter funtion as flight_search and flight_date_search seperately.


3.After clicked flight id in flights list by admin, assumption was to set a new webpage for the information of each flight. But I managed to integreted  flights list and flight info in one html file, by implementing the {% if flight_info %} method. 

4. By using the GET method, passing passenger id and flight id in route, I managed to using the route to edit passenger's information , check passenger's details, and making flights for the passenger.

5. Instead of create html files for the function of adding passenger, editing passenger's details, adding flights, and editing flight's information, I managed to integrate a bootstrap modal plugin to the webpage for flask form submission. 








