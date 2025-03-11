from flask import Flask,render_template,request,session,jsonify,redirect,url_for
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


cluster=MongoClient("mongodb+srv://anushaglory12:123456789Anusha@job-portal.0bmkr.mongodb.net/")
db=cluster['hirehub']
users=db['users']
companies=db['companies']
applyjobs=db['applyjobs']
job_application=db['job_application']

app=Flask(__name__)
app.secret_key="rajesh"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/profile', methods=['GET'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get user data
    user_data = users.find_one({"username": session['username']})
    if not user_data:
        return redirect(url_for('login'))

    # Get applied jobs for this user
    applied_jobs = list(job_application.find({"username": session['username']}))

    return render_template('profile.html', data=user_data, applied_jobs=applied_jobs)

@app.route("/job")
def job():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get all jobs and mark which ones the current user has applied to
        jobs = list(applyjobs.find())
        if session.get('user_type') == 'employee':
            applied_jobs = list(job_application.find({'username': session['username']}))
            applied_job_titles = [app['title'] for app in applied_jobs]
            
            for job in jobs:
                job['has_applied'] = job['title'] in applied_job_titles
                # Convert ObjectId to string for JSON serialization
                job['_id'] = str(job['_id'])
        
        error = request.args.get('error')
        return render_template("x.html", data=jobs, error=error)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/apply")
def apply():
    return render_template("apply.html")

@app.route("/application")
def application():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session.get('user_type') == 'recruiter':
        # For recruiters, show applications for their posted jobs
        applications = list(job_application.find({'jobpostedname': session['username']}))
    else:
        # For employees, show their own applications
        applications = list(job_application.find({'username': session['username']}))
    
    return render_template("application.html", applications=applications)

@app.route("/browser")
def browser():
    return render_template("browser.html")



@app.route("/companies", methods=["GET"])
def companies_route():
    # Fetch all companies related to the logged-in user
    print(session['username'])
    user_companies = list(companies.find({"username": session['username']}))  # Convert cursor to list then only we can use the realted details of particular user
    # Format the 'Date' field for each company if it exists
    for company in user_companies:
        if 'Date' in company and isinstance(company['Date'], datetime):
            company['Date'] = company['Date'].strftime("%Y-%m-%d")  # Format as 'YYYY-MM-DD'

    return render_template("companies.html", data=user_companies)

@app.route("/edit_company/<company_id>", methods=["POST"])
def edit_company(company_id):   
    # Fetch the company using the company_id from the database
    company = companies.find_one({"username": session['username']})

    if not company:
        return "Company not found", 404

    # Redirect to a page where you can edit the company details
    return render_template("edit_company.html", company=company)


@app.route("/create")
def create():
    return render_template("create.html")

@app.route("/jobs")
def jobsha():
    a=applyjobs.find({"username":session['username']})
    return render_template("jobs.html",data=a)

@app.route("/newjobs", methods=['GET'])
def newjobs():
    job_id = request.args.get('job_id')  # Get the job_id from the URL parameters

    if job_id:
        job = applyjobs.find_one({"_id": ObjectId(job_id), "username": session.get("username")})
        if job:
            # Convert job ID to string and format other fields as necessary
            job["_id"] = str(job["_id"])
            x=list(companies.find({'username':session['username']}))
            print("Job id is ",job["_id"])
            print("Company is ",x)
            print(f"Number of companies fetched: {len(x)}")
            return render_template("newjobs.html", job=job,companies=x)  # Pass the job data to the template
        else:
            return render_template("newjobs.html", status="Job not found.")
    else:
        print("Hello man")
        x=list(companies.find({'username':session['username']}))
        print("Company is ",x)
        print(f"Number of companies fetched: {len(x)}")
        return render_template("newjobs.html", companies=x)


@app.route("/recprofile")
def recprofile():
    if session.get('username'):
        a=users.find_one({'email':session['email']})
        return render_template('recprofile.html', data=a)
    else:
        return render_template('login.html')

@app.route("/setup", methods=['GET'])
def setup():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    com_id = request.args.get('_id')
    user_companies = list(companies.find({"username": session['username']}))
    excom = None
    
    if com_id:
        try:
            excom = companies.find_one({"_id": ObjectId(com_id)})
        except Exception as e:
            print("Error converting _id to ObjectId:", e)
    
    return render_template("setup.html", excom=excom, companies=user_companies)

@app.route("/registeruser", methods=["post"])
def registeruser():
    username = request.form.get("username")
    email = request.form.get("email")
    phnumber = request.form.get("phnumber")
    password = request.form.get("pass")
    conpass = request.form.get("conpass")
    user_type = request.form.get("user_type")

    # Basic validation
    if not all([username, email, phnumber, password, conpass, user_type]):
        return render_template("signup.html", status="All fields are required")
    
    if password != conpass:
        return render_template("signup.html", status="Passwords do not match")
    
    if not ('@' in email and '.com' in email):
        return render_template("signup.html", status="Invalid email format")
    
    if len(phnumber) != 10:
        return render_template("signup.html", status="Phone number must be 10 digits")

    # Check for existing user
    if users.find_one({"$or": [
        {"username": username},
        {"email": email},
        {"number": phnumber}
    ]}):
        return render_template("signup.html", status="Username, email, or phone number already registered")

    # Create new user
    users.insert_one({
        "username": username,
        "email": email,
        "number": phnumber,
        "pass": password,
        "user_type": user_type,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    })

    return render_template("login.html", status="Registration successful, please log in")

@app.route("/userlogin", methods=['POST'])
def userlogin():
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("userType")

    if not all([email, password, user_type]):
        return render_template("login.html", status="All fields are required")

    user = users.find_one({
        "email": email,
        "user_type": user_type
    })
    
    if not user:
        return render_template("login.html", status="User not found or incorrect user type")

    if user["pass"] != password:
        return render_template("login.html", status="Invalid password")

    # Set session data
    session['username'] = user['username']
    session['email'] = user['email']
    session['user_type'] = user['user_type']

    if user_type == "recruiter":
        # Get recruiter's company info
        company = companies.find_one({"username": user['username']})
        return render_template("recprofile.html", data=user, company=company)
    else:
        # Get employee's applied jobs
        applied_jobs = job_application.find({"username": user['username']})
        return render_template("profile.html", data=user, applied_jobs=list(applied_jobs))


@app.route("/createcompany", methods=['POST'])
def createcompany():
    if 'username' not in session or session.get('user_type') != 'recruiter':
        return redirect(url_for('login'))

    company_name = request.form.get("company_name")
    description = request.form.get("description")
    website = request.form.get("website")
    location = request.form.get("location")
    image = request.form.get("image")
    
    # Validate required fields
    if not all([company_name, description, website, location]):
        return render_template("setup.html", status="All fields are required.")
    
    # Check if company already exists for this recruiter
    existing_company = companies.find_one({
        "companyname": company_name,
        "username": session['username']
    })
    
    if existing_company:
        return render_template("setup.html", status="You already have a company with this name.")
    
    # Create new company
    company_data = {
        "companyname": company_name,
        "description": description,
        "website": website,
        "location": location,
        "username": session['username'],
        "company_logo": image,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }
    
    companies.insert_one(company_data)
    
    # Get user data
    user_data = users.find_one({"username": session['username']})
    if not user_data:
        return redirect(url_for('login'))
        
    return render_template("recprofile.html", data=user_data, company=company_data, status="Company created successfully!")

@app.route("/get_companies", methods=['GET'])
def get_companies():
    if 'username' not in session or session.get('user_type') != 'recruiter':
        return jsonify([])
    
    user_companies = list(companies.find({"username": session['username']}))
    return jsonify([{
        "id": str(company["_id"]),
        "name": company["companyname"]
    } for company in user_companies])

@app.route("/postjobs", methods=['POST'])
def postjobs():
    if 'username' not in session or session.get('user_type') != 'recruiter':
        return redirect(url_for('login'))
    
    # Get form data
    job_id = request.form.get("job_id")
    title = request.form.get("title")
    company_name = request.form.get("company")
    location = request.form.get("location")
    description = request.form.get("description")
    job_type = request.form.get("jobType")
    requirements = request.form.get("requirements")
    salary = request.form.get("salary")
    experience_level = request.form.get("experienceLevel")
    no_of_positions = request.form.get("noOfPosition")
    company_logo = request.form.get("logo")

    # Validate form data
    if not all([title, company_name, location, description, job_type, requirements, salary, experience_level, no_of_positions]):
        return render_template("newjobs.html", status="Please fill in all required fields.")

    # Verify company exists and belongs to recruiter
    company = companies.find_one({
        "companyname": company_name,
        "username": session['username']
    })
    
    if not company:
        return render_template("newjobs.html", status="Please select a valid company that you own.")

    job_data = {
        "title": title,
        "location": location,
        "description": description,
        "job_type": job_type,
        "requirements": requirements,
        "salary": float(salary),
        "experience_level": int(experience_level),
        "no_of_positions": int(no_of_positions),
        "username": session['username'],
        "company": company_name,
        "company_logo": company_logo or company.get("company_logo", ""),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "active"
    }

    if job_id:
        result = applyjobs.update_one(
            {"_id": ObjectId(job_id), "username": session['username']},
            {"$set": job_data}
        )
        status = "Job updated successfully!" if result.modified_count > 0 else "Error updating job."
    else:
        applyjobs.insert_one(job_data)
        status = "Job posted successfully!"

    # Get all jobs for this recruiter
    recruiter_jobs = list(applyjobs.find({"username": session['username']}))
    return render_template("newjobs.html", status=status, jobs=recruiter_jobs, company=company)

@app.route("/editform", methods=['POST'])
def editform():
    old_name = request.form.get("old_name")  # Get old username from hidden field
    new_name = request.form.get("name")      # Get updated username from form
    email = request.form.get("email")
    phone = request.form.get("phone")

    # Check if the user exists in the database using the old username
    user = users.find_one({"username": old_name})

    if user:
        # Update user details including the username if changed
        users.update_one(
            {"username": old_name},  # Match based on old username
            {"$set": {"username": new_name, "email": email, "number": phone}}   # Update the new values
        )
        status_message = "Profile updated successfully!"
        # Fetch the updated user details
        updated_user = users.find_one({"username": new_name})  # Fetch updated user data
    else:
        status_message = "User not found"
        updated_user = None  # Keep updated_user as None if the user is not found

    # Render the template and send the updated user data and status message
    return render_template('recprofile.html', data=updated_user if updated_user else user, status=status_message)

@app.route("/profileedit",methods=['post'])
def profileedit():
    # Fetch form data
    old_name = request.form.get("old_name")
    new_name = request.form.get("new_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    bio = request.form.get("bio", "")  # Optional
    skills = request.form.get("skills", "")  # Optional
    resume_link = request.form.get('resume_link')
  # Validate the link (you can add more validation to check if it's a valid Google Drive link)
    if not resume_link.startswith("https://drive.google.com/"):
        return "Invalid Google Drive link. Please make sure the link is correct."
    # Check if the user exists in the database using the old username
    user = users.find_one({"username": old_name})
    if user:
        # Prepare the data to be updated
        update_data = {
            "username": new_name,
            "email": email,
            "number": phone,
            "bio": bio,
            "skills": skills,
            'resume':resume_link
        }

        # Update the user document in the database
        users.update_one({"username": old_name}, {"$set": update_data})

        # Fetch the updated user data
        updated_user = users.find_one({"username": new_name})

        # Render the profile template with updated data
        status_message = "Profile updated successfully!"
        return render_template('profile.html', data=updated_user, status=status_message)
    else:
        # If the user is not found, return the original data with an error message
        
        status_message = "User not found"
        z=users.find_one({"username":session['username']})
        x=job_application.find({"username":session['username']})
        return render_template('profile.html', data=user, status=status_message,applied_jobs=x)


@app.route("/appliedjob", methods=['POST'])
def appliedjob():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Get form data
        title = request.form.get('title')
        company = request.form.get('company')
        jobpostedname = request.form.get('jobpostedname')

        # Get the job details from applyjobs collection
        job = applyjobs.find_one({
            'title': title,
            'company': company,
            'username': jobpostedname
        })

        if not job:
            return redirect(url_for('job', error="Job not found"))

        # Get user data including resume
        user = users.find_one({'username': session['username']})
        if not user:
            return redirect(url_for('job', error="User not found"))

        # Check if already applied
        existing_application = job_application.find_one({
            'username': session['username'],
            'title': title,
            'company': company
        })
        
        if existing_application:
            return redirect(url_for('job', error="You have already applied for this job"))

        # Create application
        application = {
            'company': company,
            'title': title,
            'status': "Pending",
            'username': user['username'],
            'email': user['email'],
            'number': user.get('number', ''),
            'resume': user.get('resume', ''),
            'location': job.get('location', ''),
            'jobpostedname': jobpostedname,
            'applied_date': datetime.now().strftime("%Y-%m-%d"),
            'job_id': str(job['_id'])
        }
        
        job_application.insert_one(application)
        return redirect(url_for('profile', message="Application submitted successfully"))

    except Exception as e:
        print("Error in appliedjob:", str(e))
        return redirect(url_for('job', error=str(e)))

@app.route("/view_applications")
def view_applications():
    if 'username' not in session or session.get('user_type') != 'recruiter':
        return redirect(url_for('login'))
        
    # Get all applications for jobs posted by this recruiter
    applications = list(job_application.find({'jobpostedname': session['username']}))
    return render_template("applications.html", applications=applications)

@app.route("/status_update",methods=['post'])
def statu_update():
    name=request.form.get("username")
    companyname=request.form.get("companyname")
    title=request.form.get("title")
    status=request.form.get('status')
    print(name,companyname,title,status)
    result = job_application.update_one(
        {'username': name, 'companyname': companyname, 'title': title},  # Filter query
        {'$set': {'status': status}}  # Fields to update
    )

    if result.modified_count > 0:
        return render_template("application.html", status="Status updated successfully!")
    else:
        return render_template("application.html", status="Failed to update status.")



@app.route("/x")
def x():
    a=applyjobs.find()
    return render_template("x.html",data=a)

@app.route("/viewdetails")
def viewdet():
    a = request.args.get("id")
    data = applyjobs.find_one({"_id": ObjectId(a)})
    return render_template("apply.html", x=data)


if __name__=="__main__":
    app.run(port=4000,debug=True,host='0.0.0.0')
