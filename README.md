**Deployed Link:**
https://nestcare.onrender.com/

**Video Presentation Link:**
https://drive.google.com/file/d/1qGD0kn6K66XJvRw11fW_qkb69wYyzDzQ/view?usp=drive_link

**Admin Login Credentials:**
Email: admin@gmail.com
Password: 0000

**All Customer and Professional Passwords have been set to: 0000**
**Login for every Customer and Professional is based on the name.**
**Ex: For Customer_1:**
  **Email: customer_1@gmail.com**
  **Password: 0000**


**Description:**

The Household Services Application is a multi-user platform designed to connect customers
with service professionals while allowing administrators to manage users and services
effectively. This app utilizes modern technologies like Flask, SQLAlchemy, and Bootstrap to
provide a seamless and responsive experience.
**The primary features of the platform include:**
  1. User Authentication: Separate login and dashboard functionality for Admins, Customers, and Workers.
  2. Service Management: Admins can create, update, and delete services.
  3. Request Handling: Customers can create service requests, which professionals can accept or reject.
  4. Search Functionality: Users can search for services by name or location.
  5. Ratings and Reviews: Customers can review completed services, enhancing trust and transparency.

**Technologies Used**
  1. Flask: Framework for backend logic and routing.
  2. Flask-SQLAlchemy: Extension for managing database connections and ORM.
  3. Flask-Login: User session management for login/logout functionalities.
  4. Bootstrap: Responsive frontend framework for styling and layout.
  5. SQLite: Lightweight database for storing user, service, and request information.
  6. Werkzeug: Utilities for URL routing and security.

**Database Schema Design**
Users Table:
● id: Primary Key
● name: User's name (Unique)
● email: User's email (Unique)
● password: Hashed password
● role: User role (admin, customer, professional)
● service_id: Foreign Key linked to Services

Services Table:
● id: Primary Key
● name: Name of the service
● description: Service details
● base_price: Service price
● time_required: Time needed for service

ServiceRequest Table:
● id: Primary Key
● service_id: Foreign Key linked to Services
● customer_id: Foreign Key linked to Users
● professional_id: Foreign Key linked to Users
● status: Request status (e.g., requested, closed)
