from flask import Flask, redirect, render_template, url_for, flash, session, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import matplotlib
matplotlib.use("Agg") 
from matplotlib import pyplot as plt
import seaborn as sns


cur_dir = os.path.abspath(os.path.dirname(__file__))

hsapp = Flask(__name__)
hsapp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nestcare.sqlite3'
hsapp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
hsapp.secret_key = "JAI_SHRI_RAM_JAI_SHRI_KRISHNA"
hsapp.config['UPLOAD_EXTENSIONS'] =['pdf']
hsapp.config['UPLOAD_PATH'] = os.path.join(cur_dir, 'static', "pdf")


db = SQLAlchemy()

db.init_app(hsapp)
hsapp.app_context().push()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable = False, unique = True)
    email = db.Column(db.String(80), unique = True, nullable = False)  
    password = db.Column(db.String(80), nullable = False) 
    location = db.Column(db.String(80), nullable = True)
    pincode = db.Column(db.Integer, nullable = True)
    mobile_number = db.Column(db.Integer, nullable = True)
    role = db.Column(db.String(80), nullable = False) 
    is_approved  = db.Column(db.Boolean,  default = False)
    is_flagged = db.Column(db.Boolean, default = False)
    prof_profile = db.Column(db.String(80), nullable = True) 
    prof_experience= db.Column(db.String(80), nullable = True) 
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'),nullable=True) 
    service = db.relationship('Services', back_populates="professionals")
    cust_request = db.relationship('ServiceRequest', back_populates='customer', foreign_keys='ServiceRequest.customer_id')
    prof_request = db.relationship('ServiceRequest', back_populates='professional', foreign_keys='ServiceRequest.professional_id')


class Services(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=True)
    base_price = db.Column(db.Integer, nullable=True)
    time_required = db.Column(db.String(80), nullable=True)
    professionals = db.relationship('User', back_populates="service")
    service_requests = db.relationship('ServiceRequest', back_populates = "service", cascade="all, delete")


class ServiceRequest(db.Model):
    __tablename__="serviceRequest"
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    description = db.Column(db.Text, nullable = True)
    status = db.Column(db.String(80), nullable=True) 
    date_created = db.Column(db.Date, nullable=False, default=datetime.now().date())
    date_closed = db.Column(db.Date, nullable=True)
    service = db.relationship('Services', back_populates='service_requests')
    customer = db.relationship('User', back_populates='cust_request', foreign_keys=[customer_id])
    professional = db.relationship('User', back_populates='prof_request', foreign_keys=[professional_id])




def admin_create():
    admin_exists = User.query.filter_by(email = "admin@gmail.com").first()
    if not admin_exists:
        admin = User(name = "Admin", email = "admin@gmail.com", password = generate_password_hash("0000"), role = "admin", is_approved = True)
        db.session.add(admin)
        db.session.commit()
        print("Admin created")




@hsapp.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@hsapp.route("/nc_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        admin = User.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            session['admin'] = admin.id
            flash("Login successful", "success")
            return redirect('/admin')
        else:
            flash("Invalid email or password", "danger")
    return render_template("admin_login.html")




@hsapp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            if user.role == "professional":
                if user.is_approved == False:
                    flash("Your account is not approved by admin", "danger")
                    return redirect('/login')
                if user.is_flagged == True:
                    flash("You have been flagged by admin", "danger")
                    return redirect('/login')
                services = Services.query.all()
                if user.service_id not in [service.id for service in services]:
                    flash("Your service is not available anymore. Please register again.", "danger")
                    return redirect('/login')
                session['professional'] = user.id
                flash("Login successful", "success")
                return redirect('/professional')
            elif user.role == "customer":
                if user.is_flagged == True:
                    flash("You have been flagged by admin", "danger")
                    return redirect('/login')
                session['customer'] = user.id
                flash("Login successful", "success")
                return redirect('/customer')
        else:
            flash("Invalid email or password", "danger")
            return redirect('/login')
    return render_template("login.html")



@hsapp.route("/register_customer", methods=["GET", "POST"])
def register_customer():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        location = request.form["location"]
        pincode = request.form["pincode"]
        mobile_number = request.form["mobile_number"]
        users  = User.query.filter_by(email=email).first()
        if users:
            flash("Account with this Email already exists.", "danger")
            return redirect("/register_professional")
        users_name = User.query.filter_by(name=name).first()
        if users_name:
            flash("Account with this Name already exists.", "danger")
            return redirect("/register_professional")
        user = User(name=name, email=email, password=generate_password_hash(password), is_approved = True ,location=location, pincode=pincode, mobile_number=mobile_number, role="customer")
        db.session.add(user)
        db.session.commit()
        flash("Registration successful", "success")
        return redirect("/login")
    return render_template("register_customer.html")


@hsapp.route("/register_professional", methods=["GET", "POST"])
def register_professional():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        location = request.form["location"]
        pincode = request.form["pincode"]
        mobile_number = request.form["mobile_number"]
        prof_profile = request.files["prof_profile"]
        prof_experience = request.form["prof_experience"]
        service = request.form["service"]
        users  = User.query.filter_by(email=email).first()
        if users:
            flash("Account with this Email already exists.", "danger")
            return redirect("/register_professional")
        users_name = User.query.filter_by(name=name).first()
        if users_name:
            flash("Account with this Name already exists.", "danger")
            return redirect("/register_professional")        
        service_id = Services.query.filter_by(name=service).first().id
        prof_filename = secure_filename(prof_profile.filename)
        if prof_filename != "":
            file_ext = prof_filename.split(".")[1]
            print(file_ext)
            renamed_prof_filename = str(email.split("@")[0]) + "." + file_ext
            if file_ext not in hsapp.config['UPLOAD_EXTENSIONS']:
                flash("Invalid file extension", "danger")
                return redirect("/register_professional")
            prof_profile.save(os.path.join(hsapp.config['UPLOAD_PATH'], renamed_prof_filename))
        user = User(name = name, email = email, password = generate_password_hash(password), is_approved = False, location = location, pincode = pincode, mobile_number = mobile_number, 
                                role = "professional", prof_profile = renamed_prof_filename, prof_experience = prof_experience, service_id = service_id)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful", "success")
        return redirect("/login")
    services = Services.query.all()
    return render_template("register_professional.html", services = services)



@hsapp.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    users = User.query.all()
    services = Services.query.all()
    service_requests = ServiceRequest.query.all()
    unapproved_professionals = User.query.filter_by(role="professional", is_approved=False).all()
    return render_template("admin_dashboard.html", users = users, services = services, service_requests = service_requests, unapproved_professionals = unapproved_professionals)



@hsapp.route("/admin/approve_professional/<int:user_id>", methods=["GET", "POST"])
def approve_professional(user_id):
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash("Professional approved successfully", "success")
    return redirect("/admin")




@hsapp.route("/admin/flag_user/<int:user_id>", methods=["GET", "POST"])
def flag_user(user_id):
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("You cannot flag yourself", "danger")
        return redirect("/admin")
    user.is_flagged = True
    db.session.commit()
    flash("User flagged successfully", "success")
    return redirect("/admin")



@hsapp.route("/admin/unflag_user/<int:user_id>", methods=["GET", "POST"])
def unflag_user(user_id):
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    user = User.query.get_or_404(user_id)
    user.is_flagged = False
    db.session.commit()
    flash("User unflagged successfully", "success")
    return redirect("/admin")



@hsapp.route("/<user_type>/logout")
def logout(user_type):
    if user_type not in ["admin", "customer", "professional"]:
        flash("Invalid user type", "danger")
        return redirect("/")
    session.pop(user_type, None)
    flash("Logged out successfully", "success")
    if user_type == "admin":
        return redirect("/nc_login")
    elif user_type == "customer":
        return redirect("/login")
    elif user_type == "professional":
        return redirect("/login")
    return redirect("/login")



@hsapp.route("/admin/create_service", methods=["GET", "POST"])
def create_service():
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        base_price = request.form["base_price"]
        time_required = request.form["time_required"]
        service = Services(name=name, description=description, base_price=base_price, time_required=time_required)
        db.session.add(service)
        db.session.commit()
        flash("Service created successfully", "success")
        return redirect("/admin")



@hsapp.route("/admin/edit_service/<int:service_id>", methods=["GET", "POST"])
def edit_service(service_id):
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    service = Services.query.get_or_404(service_id)
    if request.method == "POST":
        service.name = request.form["name"]
        service.description = request.form["description"]
        service.base_price = request.form["base_price"]
        service.time_required = request.form["time_required"]
        db.session.commit()
        flash("Service updated successfully", "success")
        return redirect("/admin")
    return render_template("edit_service.html", service=service)




@hsapp.route("/admin/delete_service/<int:service_id>", methods=["GET", "POST"])
def delete_service(service_id):
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/nc_login")
    service = Services.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash("Service deleted successfully", "success")
    return redirect("/admin")


@hsapp.route("/customer", methods=["GET", "POST"])
def customer_dashboard():
    if "customer" not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    services = (Services.query.join(Services.professionals).filter(User.role == "professional", User.is_approved == True, User.is_flagged == False).distinct().all())
    service_requests = ServiceRequest.query.filter_by(customer_id=session['customer']).all()
    professionals_by_service = {
        service.id: User.query.filter_by(service_id=service.id, role="professional", is_approved=True).all()
        for service in services
    }
    return render_template("customer_dashboard.html", services=services, service_requests=service_requests, professionals_by_service=professionals_by_service)




@hsapp.route("/customer/create_service_request/<int:service_id>", methods=["GET", "POST"])
def create_service_request(service_id):
    if "customer" not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    if request.method == "POST":
        description = request.form["description"]
        status = "Pending"
        professional = request.form['professional_name']
        professional_id = User.query.filter_by(name=professional).first().id
        service_request = ServiceRequest(service_id=service_id, professional_id=professional_id, customer_id=session['customer'], description=description, status=status)
        db.session.add(service_request)
        db.session.commit()
        flash("Service request created successfully", "success")
        return redirect("/customer")



@hsapp.route("/customer/edit_service_request/<int:service_request_id>", methods=["GET", "POST"])
def edit_service_request(service_request_id):
    if "customer" not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    if request.method == "POST":
        service_request.description = request.form["description"]
        db.session.commit()
        flash("Service request updated successfully", "success")
        return redirect("/customer")
    

@hsapp.route("/customer/delete_service_request/<int:service_request_id>", methods=["GET", "POST"])
def delete_service_request(service_request_id):
    if "customer" not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    db.session.delete(service_request)
    db.session.commit()
    flash("Service request deleted successfully", "success")
    return redirect("/customer")




@hsapp.route("/customer/close_service_request/<int:service_request_id>", methods=["GET", "POST"])
def close_service_request(service_request_id):
    if "customer" not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    service_request.status = "Closed"
    service_request.date_closed = datetime.now().date()
    db.session.commit()
    flash("Service request closed successfully", "success")
    return redirect("/customer")





@hsapp.route("/professional", methods=["GET", "POST"])
def professional_dashboard():
    if "professional" not in session:
        flash("Please login as professional first", "danger")
        return redirect("/login")
    pending_requests = ServiceRequest.query.join(ServiceRequest.customer).filter(ServiceRequest.professional_id == session['professional'], ServiceRequest.status == "Pending", User.is_flagged == False).all()
    completed_requests = ServiceRequest.query.join(ServiceRequest.customer).filter(ServiceRequest.professional_id == session['professional'], ServiceRequest.status == "Closed", User.is_flagged == False).all()
    active_requests = ServiceRequest.query.join(ServiceRequest.customer).filter(ServiceRequest.professional_id == session['professional'], ServiceRequest.status == "Accepted", User.is_flagged == False).all()
    rejected_requests = ServiceRequest.query.join(ServiceRequest.customer).filter(ServiceRequest.professional_id == session['professional'], ServiceRequest.status == "Rejected", User.is_flagged == False).all()
    return render_template("professional_dashboard.html", pending_requests = pending_requests, completed_requests = completed_requests, active_requests = active_requests, rejected_requests = rejected_requests)



@hsapp.route("/professional/accept_request/<int:service_request_id>", methods=["GET", "POST"])
def accept_service_request(service_request_id):
    if "professional" not in session:
        flash("Please login as professional first", "danger")
        return redirect("/login")
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    service_request.status = "Accepted"
    db.session.commit()
    flash("Service request accepted successfully", "success")
    return redirect("/professional")




@hsapp.route("/professional/reject_request/<int:service_request_id>", methods=["GET", "POST"])
def reject_service_request(service_request_id):
    if "professional" not in session:
        flash("Please login as professional first", "danger")
        return redirect("/login")
    service_request = ServiceRequest.query.get_or_404(service_request_id)
    service_request.status = "Rejected"
    db.session.commit()
    flash("Service request rejected successfully", "success")
    return redirect("/professional")


@hsapp.route("/customer/search", methods=["GET", "POST"])
def search():
    if 'customer' not in session:
        flash("Please login as customer first", "danger")
        return redirect("/login")
    search_query = request.args.get('search_query')
    professionals = User.query.filter(User.role == "professional", User.is_approved == True, User.is_flagged == False).all()
    if search_query:
        services = Services.query.join(User).filter(Services.name.ilike('%'+search_query+'%') | User.location.ilike('%'+search_query+'%') | User.pincode.ilike('%'+search_query+'%')).all()
        return render_template("customer_search.html", services=services, professionals=professionals)
    services = Services.query.join(User).filter(User.is_approved == True, User.is_flagged == False).all()
    return render_template("customer_search.html", services=services, professionals=professionals)    






@hsapp.route("/admin/summary", methods=["GET", "POST"])
def admin_summary():
    if "admin" not in session:
        flash("Please login as admin first", "danger")
        return redirect("/login")
    pending_requests = ServiceRequest.query.filter(ServiceRequest.status == "Pending").count() or 0
    completed_requests = ServiceRequest.query.filter(ServiceRequest.status == "Closed").count() or 0
    active_requests = ServiceRequest.query.filter(ServiceRequest.status == "Accepted").count() or 0
    rejected_requests = ServiceRequest.query.filter(ServiceRequest.status == "Rejected").count() or 0
    professionals_count = User.query.filter(User.role == "professional").count() or 0
    customers_count = User.query.filter(User.role == "customer").count() or 0
    img_1 = os.path.join(cur_dir, 'static', 'images', 'img_1.png')
    img_2 = os.path.join(cur_dir, 'static', 'images', 'img_2.png')
    roles = ["Professional", "Customer"]
    counts = [professionals_count, customers_count]
    plt.figure(figsize=(6,4))
    sns.barplot(x=roles, y=counts)
    plt.title("Number of users by role")
    plt.xlabel("User Role")
    plt.ylabel("Count")
    plt.savefig(img_1, format='png')
    plt.close()
    status = ['Accepted', 'Rejected', 'Closed', 'Pending']
    counts = [active_requests, rejected_requests, completed_requests, pending_requests]
    new_counts = [max(0, count) for count in counts] 
    colors = ['#FF69B4', '#00FFFF', '#FFA500', '#800080']
    if sum(new_counts)>0:
        try:
            plt.figure(figsize=(6,4))
            plt.pie(new_counts, labels=status, colors=colors, autopct='%1.1f%%')
            plt.title("Request Status Distribution")
            plt.savefig(img_2, format='png')
            plt.close()
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            flash("An error occurred while generating the pie chart.", "danger")
    else:
        flash("No data available for request status distribution.", "danger")
        if os.path.exists(img_2):
            os.remove(img_2)

    return render_template("summary.html", pending_requests=pending_requests, completed_requests=completed_requests, active_requests=active_requests, rejected_requests=rejected_requests, professionals_count=professionals_count, customers_count=customers_count)









if __name__ == "__main__":
    db.create_all()
    admin_create()
    hsapp.run(debug=True)