It manages customer bookings, flights, routes, airports and aircraft.

 Using Python and HTML language, this website consists of two main parts: a public area for customers to look up flight details and book flights, and an administration area for staff to add and edit flight details, bookings and passenger information.

Customer Portal contains: 

1. Landing Page. On this page, users can check arrivals and departures information from 2 days before to 5 days aafter the current day.Customers must login to make booking and check their own profiles. If it's a new customer, the login system will jump to register page allowing customer to sign up.
 
  The home route returns home.html as landing page, once opened, there are two routes login_in and arrival_departure included on this page, if there is no reault returned from sql query, the page will direct to register page instead.
  
2.  Once logged in, cutomer will see their passenger id on the top of web page, a log out button allows cutomer to log out and terminate this session easily.  There is a drop down list of available departure airports and date picker on the top, customer can choose airport and date to make new booking. The second part is passenger's personal information including their By clicking the update button, customer can update their personal details in a modal.
  
  info_page.html is heavy coded, there are three fuctions on this page. The function booking_info returns customers passenger deatails and booking information from sql query.
  
  
  3.



Assumption:

1. Assuming admin and user can use the same path to manage customer's profile, such as update customer profile, cancel flight, or make new booking for customer. However, it turns out that I used the session['passenger_id'] to pass the passenger_id value during customer session, which makes it's difficult to share same function and route between customer and admin. 
I decided to use "GET" path during both sessions instead of "POST" , so that both admin and user can update and cancel flight use same html and route. However, since book flight can only reachable during customer session.


2. For the function that allows admin to filter flight list in admin portal, assumption is that I can combine both date range and departure airport query as one query, however I have some issue with using where and condition in mysql query, so I have to seperate the two filter funtion as flight_search and flight_date_search seperately.


3. There is a duplicate function.  passenger_profile(passenger_id):

but cancel and update customer info are shared bwtween customer session and admin session


4. After clicked flight id in flights list by admin, assumption was to set a new webpage for the information of each flight. But I managed to integreted  flights list and flight info in one html file, by implementing the {% if flight_info %} method.


6. add flight option, datetime string  duration calculation, sunstract two datetime strings

