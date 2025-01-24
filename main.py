import os
import uuid
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# AWS Configuration
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
dynamodb = boto3.resource('dynamodb')

# DynamoDB Table Definitions
USERS_TABLE = dynamodb.Table('HireHub_Users')
COMPANIES_TABLE = dynamodb.Table('HireHub_Companies')
JOBS_TABLE = dynamodb.Table('HireHub_Jobs')
JOB_APPLICATIONS_TABLE = dynamodb.Table('HireHub_JobApplications')

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Login Routes
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/create")
def create():
    return render_template("setup.html")

# User Registration
@app.route("/registeruser", methods=["POST"])
def registeruser():
    username = request.form.get("username")
    email = request.form.get("email")
    phone = request.form.get("phnumber")
    password = request.form.get("pass")
    conpass = request.form.get("conpass")
    user_type = request.form.get("user_type")

    # Validation checks
    if password != conpass:
        return render_template("signup.html", status="Passwords do not match")

    # Check existing user (use get_item instead of query)
    response = USERS_TABLE.get_item(Key={'username': username, 'email': email})

    if 'Item' in response:  # If user already exists
        return render_template("signup.html", status="Username already exists")

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create user item
    user_item = {
        'username': username,
        'email': email,
        'phone': phone,
        'password': hashed_password,
        'user_type': user_type
    }

    USERS_TABLE.put_item(Item=user_item)
    return render_template("login.html", status="Registration successful")


# User Login
@app.route("/userlogin", methods=['POST'])
def userlogin():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    user_type = request.form.get("userType")

    # Retrieve user using BOTH `username` (Partition Key) and `email` (Sort Key)
    response = USERS_TABLE.get_item(Key={'username': username, 'email': email})

    # Check if user exists
    user = response.get('Item')
    if not user:
        return render_template("login.html", status="User not found")

    # Verify password
    if not check_password_hash(user.get('password', ''), password):
        return render_template("login.html", status="Invalid password, please try again.")

    # Verify user type
    if user.get('user_type') != user_type:
        return render_template("login.html", status="Incorrect user type.")

    # Store session details
    session['username'] = user['username']
    session['email'] = user['email']
    session['user_type'] = user['user_type']

    return render_template("login.html", status=f"Welcome back, {user_type}!")


# Profile Route
@app.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch user data
    user_response = USERS_TABLE.query(
        KeyConditionExpression=Key('username').eq(session['username'])
    )
    user_data = user_response['Items'][0] if user_response['Count'] > 0 else None

    # Fetch applied jobs
    applications_response = JOB_APPLICATIONS_TABLE.query(
        IndexName='username-index',
        KeyConditionExpression=Key('username').eq(session['username'])
    )
    applied_jobs = applications_response.get('Items', [])

    return render_template('profile.html', data=user_data, applied_jobs=applied_jobs)

@app.route("/createcompany", methods=['POST'])
def createcompany():
    # Get form data
    company_name = request.form.get("company_name")
    description = request.form.get("description")
    website = request.form.get("website")
    location = request.form.get("location")
    image = request.form.get("image")  # Image URL as text
    username = session.get('username')  # Get the logged-in user

    # Validate required fields
    if not (company_name and description and website and location and username):
        return render_template("setup.html", status="All fields are required.")

    # Generate a unique company ID
    company_id = str(uuid.uuid4())

    # Create company data object
    company_item = {
        "company_id": company_id,
        "username": username,
        "company_name": company_name,
        "description": description,
        "website": website,
        "location": location,
        "company_logo": image,
        "created_at": datetime.utcnow().isoformat()
    }

    # Insert or update the company data
    COMPANIES_TABLE.put_item(Item=company_item)

    return redirect('/companies')


@app.route("/viewdetails")
def viewdet():
    job_id = request.args.get("id")
    
    # Fetch job details
    response = JOBS_TABLE.query(
        KeyConditionExpression=Key('job_id').eq(job_id)
    )
    
    data = response['Items'][0] if response['Count'] > 0 else None
    return render_template("apply.html", x=data)

# Companies Routes
@app.route("/companies", methods=["GET"])
def companies_route():
    # ✅ Check if user is logged in
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    # ✅ Get the logged-in username
    username = session['username']

    # ✅ Query companies for the logged-in user
    companies_response = COMPANIES_TABLE.query(
        KeyConditionExpression=Key('username').eq(username)
    )

    # ✅ Get the list of companies or an empty list if none exist
    user_companies = companies_response.get('Items', [])

    return render_template("companies.html", data=user_companies,username=session['username'])


# Job Routes
@app.route("/jobs")
def jobsha():
    jobs_response = JOBS_TABLE.query(
        KeyConditionExpression=Key('username').eq(session['username'])
    )
    jobs = jobs_response['Items']
    return render_template("jobs.html", data=jobs)

@app.route("/x")
def x():
    # Fetch all jobs
    jobs_response = JOBS_TABLE.scan()
    jobs = jobs_response.get('Items', [])
    return render_template("x.html", data=jobs)

@app.route("/postjobs", methods=['POST'])
def postjobs():
    job_id = str(uuid.uuid4())
    job_item = {
        'job_id': job_id,
        'username': session['username'],
        'title': request.form.get("title"),
        'location': request.form.get("location"),
        'description': request.form.get("description"),
        'job_type': request.form.get("jobType"),
        'salary': request.form.get("salary"),
        'company': request.form.get("company"),
        'logo':request.form.get("logo"),
        'created_at': datetime.utcnow().isoformat()
    }

    JOBS_TABLE.put_item(Item=job_item)
    return render_template("jobs.html", status="Job posted successfully")

# Job Applications
@app.route("/appliedjob", methods=['POST'])
def appliedjob():
    application_id = str(uuid.uuid4())
    user_response = USERS_TABLE.query(
        KeyConditionExpression=Key('username').eq(session['username'])
    )
    user = user_response['Items'][0]

    application_item = {
        'application_id': application_id,
        'jobpostedname': request.form.get('jobpostedname'),
        'username': session['username'],
        'job_title': request.form.get('title'),
        'company_name': request.form.get('company'),
        'status': 'Pending',
        'email': user['email'],
        'phone': user['phone'],
        'submitted_at': datetime.utcnow().isoformat()
    }

    JOB_APPLICATIONS_TABLE.put_item(Item=application_item)
    return render_template("index.html", status="Job application submitted")

@app.route("/application")
def application():
    if 'username' not in session:
        return redirect(url_for('login'))

    applications_response = JOB_APPLICATIONS_TABLE.query(
        IndexName='jobpostedname-index',
        KeyConditionExpression=Key('jobpostedname').eq(session['username'])
    )
    applications = applications_response['Items']
    return render_template("application.html", applications=applications)

# Profile Editing Routes
@app.route("/profileedit", methods=['POST'])
def profileedit():
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    bio = request.form.get("bio", "")
    skills = request.form.get("skills", "")
    resume_link = request.form.get('resume_link')

    # Update user item
    update_expression = "SET username = :un, email = :em, phone = :ph, bio = :bio, skills = :sk, resume = :res"
    expression_values = {
        ':un': new_name,
        ':em': email,
        ':ph': phone,
        ':bio': bio,
        ':sk': skills,
        ':res': resume_link
    }

    USERS_TABLE.update_item(
        Key={'username': old_name},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )

    # Update session
    session['username'] = new_name

    return render_template('profile.html', status="Profile updated successfully")


@app.route("/newjobs", methods=['GET'])
def newjobs():
    job_id = request.args.get('job_id')
    
    # Ensure user is logged in
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login page if user is not authenticated

    # Fetch user's companies
    companies_response = COMPANIES_TABLE.query(
        KeyConditionExpression=Key('username').eq(username)
    )
    companies = companies_response.get('Items', [])

    job = None
    if job_id:
        # Fetch specific job details using BOTH partition key (username) and sort key (job_id)
        job_response = JOBS_TABLE.query(
            KeyConditionExpression=Key('username').eq(username) & Key('job_id').eq(job_id)
        )
        job_items = job_response.get('Items', [])
        job = job_items[0] if len(job_items) > 0 else None  # Get the first job if exists

    return render_template("newjobs.html", job=job, companies=companies)


# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)