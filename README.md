It manages customer bookings, flights, routes, airports and aircraft.

 Using Python and HTML language, this website consists of two main parts: a public area for customers to look up flight details and book flights, and an administration area for staff to add and edit flight details, bookings and passenger information.

Customer Portal contains: 

1. Landing Page. On this page, users can check arrivals and departures information from 2 days before to 5 days aafter the current day.Customers must login to make booking and check their own profiles. If it's a new customer, the login system will jump to register page allowing customer to sign up.
 
  The home route returns home.html as landing page, once opened, there are two routes login_in and arrival_departure included on this page, if there is no reault returned from sql query, the page will direct to register page instead.
  
2.  Once logged in, cutomer will see their passenger id on the top of web page, a log out button allows cutomer to log out and terminate this session easily.  There is a drop down list of available departure airports and date picker on the top, customer can choose airport and date to make new booking. The second part is passenger's personal information including their By clicking the update button, customer can update their personal details in a modal.
  
  info_page.html is heavy coded, there are three fuctions on this page. The function booking_info returns customers passenger deatails and booking information from sql query.
  
  
  3.
