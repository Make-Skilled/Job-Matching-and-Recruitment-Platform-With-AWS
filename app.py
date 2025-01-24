from flask import Flask,render_template,request,session,jsonify
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


cluster=MongoClient("127.0.0.1:27017")
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
    # Retrieve user details from session
    user_name = session['username']
    username = session.get('username')
    
    if username:
        # Fetch user data based on username
        user_data = users.find_one({"username": username})
    else:
        user_data = None

    if user_name:
        # Fetch applied jobs for this user
        applied_jobs = db.job_application.find({"username": user_name})
        applied_jobs = list(applied_jobs)  # Convert cursor to list
    else:
        applied_jobs = []

    return render_template('profile.html', data=user_data, applied_jobs=applied_jobs)

@app.route("/job")
def job():
    a=applyjobs.find()
    return render_template("x.html",data=a)

@app.route("/apply")
def apply():
    return render_template("apply.html")

@app.route("/application")
def application():
    if 'username' not in session:
        return render_template('/login')
    
    # Retrieve job applicant data
    applications = list(db.job_application.find({'jobpostedname':session['username']}))

    print("Applications Retrieved:", applications)
    return render_template("application.html",applications=applications)

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
    com_id = request.args.get('_id')  # Get the job_id from the URL parameters
    excom=None
    if com_id:  # Check if _id is provided
        try:
            # Convert com_id to ObjectId and query the collection
            excom = companies.find_one({"_id": ObjectId(com_id)})
            print("Company details for one are", excom)
        except Exception as e:
            print("Error converting _id to ObjectId:", e)
            excom = None
    return render_template("setup.html",excom=excom)

@app.route("/registeruser",methods=["post"])
def registeruser():
    username = request.form.get("username")
    email = request.form.get("email")
    phnumber = request.form.get("phnumber")
    password = request.form.get("pass")
    conpass = request.form.get("conpass")
    user_type = request.form.get("user_type")  # Get the user type

    # Check if the username already exists in the database
    existing_user = users.find_one({"username": username})
    if existing_user:
        return render_template("signup.html", status="Username already exists")

    # Check if the email already exists
    existing_email = users.find_one({"email": email})
    if existing_email:
        return render_template("signup.html", status="Email already registered")

    # Check if the phone number already exists
    existing_phone = users.find_one({"number": phnumber})
    if existing_phone:
        return render_template("signup.html", status="Phone number already registered")

    # Validate and insert user if all is well
    if username and '@' in email and '.com' in email and len(phnumber) == 10 and password == conpass:
        session['username']=username
        users.insert_one({
            "username": username,
            "email": email,
            "number": phnumber,
            "pass": password,
            "user_type": user_type  # Store the user type
        })

        return render_template("login.html", status="Registration successful, please log in")
    else:
        return render_template("signup.html", status="Please fill all fields correctly")



@app.route("/userlogin", methods=['POST'])
def userlogin():
    # Get form data
    email = request.form.get("email")
    password = request.form.get("password")
    user_type = request.form.get("userType")

    # Check if the email exists in the database
    user = users.find_one({"email": email, "user_type": user_type})
    
    if user:
        # Verify the password (direct comparison since plain text, but hashing is recommended)
        if user["pass"] == password:
            # Redirect based on user type
            if user_type == "employee":
                session['email']=email
                a=users.find_one({'email':session['email']})
                session['username']=a['username']
                return render_template("login.html", status="Welcome back, employee!",data=a)
            elif user_type == "recruiter":
                session['email']=email
                a=users.find_one({'email':session['email']})
                session['username']=a['username']
                return render_template("login.html", status="Welcome back, recruiter!" ,data=a)
        else:
            # Invalid password
            return render_template("login.html", status="Invalid password, please try again.")
    else:
        # User not found or user type mismatch
        return render_template("login.html", status="User not found or incorrect user type.")


@app.route("/createcompany", methods=['post'])
def createcompany():
    compname = request.form.get("compname")
    
    # Check if the company name is empty (after trimming leading/trailing spaces)
    if not compname or len(compname.strip()) == 0:
        return render_template("create.html", status="Company name cannot be empty.")

    # Check if the company already exists for the current user
    company = companies.find_one({"companyname": compname, "username": session['username']})
    if company:
        return render_template("create.html", status="This company name already exists.")

    # Insert the new company record
    companies.insert_one({"companyname": compname, "username": session['username'], "Date": datetime.utcnow()})

    # Fetch the newly created company
    a = companies.find_one({"companyname": compname, "username": session['username']})
    
    # Format the date
    if 'Date' in a and isinstance(a['Date'], datetime):
        a['Date'] = a['Date'].strftime("%Y-%m-%d")  # Format as 'YYYY-MM-DD'

    # Return the setup page with a success message and the new company data
    return render_template("setup.html", status="Company created successfully.", data=a)

@app.route("/establishcompany", methods=['POST'])
def establishcompany():
    # Get form data from the request
    company_name = request.form.get("company_name")
    description = request.form.get("description")
    website = request.form.get("website")
    location = request.form.get("location")
    image = request.form.get("image")  # This will be the image URL entered as text
    
    # Validate that all fields are filled out
    if not (company_name and description and website and location):
        return render_template("setup.html", status="All fields are required.")
    
    # Check if the company already exists for the current user
    existing_company = companies.find_one({"companyname": company_name, "username": session.get("username")})
    
    if existing_company is None:
        # Create a new company entry
        new_company = {
            "companyname": company_name,
            "description": description,
            "website": website,
            "location": location,
            "username": session.get("username"),
            "company_logo": image  # Store the image URL as text
        }
        
        # Insert company data into the database
        companies.insert_one(new_company)
        
        return render_template("companies.html", status="Company created successfully.")
    else:
        # Update the existing company
        update_data = {
            "description": description,
            "website": website,
            "location": location,
            "company_logo": image  # Update the image URL
        }
        
        # Update the company data in the database
        companies.update_one(
            {"companyname": company_name, "username": session.get("username")},
            {"$set": update_data}
        )
        
        return render_template("companies.html", status="Company updated successfully.")




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


@app.route("/postjobs", methods=['POST'])
def postjobs():
    job_id = request.form.get("job_id")  # Get job ID from the form
    print("Job id is ",job_id)
    # Get the rest of the form data, including the company name
    title = request.form.get("title")
    location = request.form.get("location")
    description = request.form.get("description")
    job_type = request.form.get("jobType")
    requirements = request.form.get("requirements")
    salary = request.form.get("salary")
    experience_level = request.form.get("experienceLevel")
    no_of_positions = request.form.get("noOfPosition")
    company_name = request.form.get("company")  # Added company field
    date=request.form.get("date")
    company_logo = request.form.get("logo")  # Updated variable name for clarity
    print(company_logo)

    # Validate form data
    if not title or not location or not description or not job_type or not requirements or not salary or not experience_level or not no_of_positions or not company_name:
        return render_template("newjobs.html", status="Please fill in all required fields.")

    # If job_id exists, update the job; otherwise, create a new job
    if job_id:
        # Update the existing job posting
        result = applyjobs.update_one(
            {"_id": ObjectId(job_id), "username": session.get("username")},
            {"$set": {
                "title": title,
                "location": location,
                "description": description,
                "job_type": job_type,
                "requirements": requirements,
                "salary": float(salary),
                "experience_level": int(experience_level),
                "no_of_positions": int(no_of_positions),
                "company": company_name,  # Include the company name
                'date':date,
                "company_logo": company_logo  # Use consistent variable name

            }}
        )
        
        # Check if the update was successful
        if result.modified_count > 0:
            return render_template("jobs.html", status="Job updated successfully!")
        else:
            return render_template("newjobs.html", status="Error updating job. Job may not have changed.")
    else:
        # Create new job if job_id is not provided
        applyjobs.insert_one({
            "title": title,
            "location": location,
            "description": description,
            "job_type": job_type,
            "requirements": requirements,
            "salary": float(salary),
            "experience_level": int(experience_level),
            "no_of_positions": int(no_of_positions),
            "username": session.get("username"),
            "company": company_name,  # Include the company name
            'date':date,
            "company_logo": company_logo  # Use consistent variable name

        })
        return render_template("jobs.html", status="Job posted successfully!")
    

# @app.route('/job_form', methods=['GET'])
# def job_form():
#     # Check if the user is logged in
#     if 'username' not in session:
#         return render_template('login.html')
    
#     # Fetch all companies created by the logged-in user
#     company = db.companies.find({"username": session['username']})  # Make sure 'companies' is the correct collection

#     # Convert the cursor to a list
#     # company = list(company)
#     x=companies.find()
    
#     # Debug print the company data to verify
#     print("Companies found for user:", session['username'], company)
    
#     # If no companies are found, this will help debug
#     if not company:
#         print("No companies found for the logged-in user")
    
#     return render_template('newjobs.html', companies=x)


@app.route("/x")
def x():
    a=applyjobs.find()
    return render_template("x.html",data=a)

@app.route("/viewdetails")
def viewdet():
    a = request.args.get("id")
    data = applyjobs.find_one({"_id": ObjectId(a)})
    return render_template("apply.html", x=data)


#status for application 
@app.route("/appliedjob",methods=['post'])
def appliedjob():
    title=request.form.get('title')
    company=request.form.get('company')
    jobpostedname=request.form.get('jobpostedname')
    print(title,company)
    user=users.find_one({'username':session['username']})
    application = {
        'companyname':company,
        'title':title,
        'status':"Pending",
        'username':user['username'],
        'email':user['email'],
        'number':user['number'],
        'resume':user['resume'],
        'jobpostedname':jobpostedname
         }
    
    job_application.insert_one(application)
    return render_template("index.html")

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



if __name__=="__main__":
    app.run(port=4000,debug=True)