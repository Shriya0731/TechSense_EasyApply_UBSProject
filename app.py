#Step – 1(import necessary library)
from flask import (Flask, render_template, request, redirect, session)
import DBConnection as db
import backend
import send_mail

#Step – 2 (configuring your application)
app = Flask(__name__)
app.secret_key = 'shriya'

#step – 3 (creating a dictionary to store information about users)
user = {"username": "abc", "password": "xyz"}


@app.route('/', methods=['POST', 'GET'])
def start():
    return render_template("index.html")


@app.route('/addjd')
def addjd():
    return render_template("add_jd.html")

@app.route('/add', methods=['POST'])
def addjdtodb():
    if (request.method == 'POST'):
        role = request.form.get('role')
        desc = request.form.get('desc')
        db.insert_new_jd(role,desc)
    #return render_template("index.html")
    return redirect('/displayrole')
    #return render_template("job-desc.html",usr=db.getrole())

@app.route('/display')
def display():
    return render_template("table.html",usr=db.display_table())

#
@app.route('/showprofiles', methods=['POST'])
def showprofiles():
    if (request.method == 'POST'):
        title = request.form.get('jobtitle')
        print(title)
        job_desc = db.getjobdesc(title)
        skilldataset = backend.cleanprofilesdataset()
        backend.findsimilarityscore(job_desc,skilldataset)



    return render_template("profiles.html",usr=db.getmatchedprofiles())



    #return db.getrole()

    # return render_template("table.html",usr=db.display_table())
    return render_template("job-desc.html",usr=db.getrole())

@app.route('/sendmails')
def sendmails():
    data = db.getmails_name()
    print("Mail Sent to:")
    print(data[1])
    send_mail.multiple_mails(data[0], data[1])
    return render_template("profiles.html",usr=db.getmatchedprofiles())

@app.route('/displayrole')
def displayroles():
    #return db.getrole()
    # return render_template("table.html",usr=db.display_table())
    return render_template("job-desc.html",usr=db.getrole())


#Step – 4 (creating route for login)
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if(request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')     
        if username == user['username'] and password == user['password']:
            
            session['user'] = username
            return redirect('/dashboard')

        return "<h1>Wrong username or password</h1>"    

    return render_template("login.html")

#Step -5(creating route for dashboard and logout)
@app.route('/dashboard')
def dashboard():
    if('user' in session and session['user'] == user['username']):
        return '<h1>Welcome to the dashboard</h1>'
    

    return '<h1>You are not logged in.</h1>'  

#Step -6(creating route for logging out)
@app.route('/logout')
def logout():
    session.pop('user')         
    return redirect('/login')

#Step -7(run the app)
if __name__ == '__main__':
    app.run(debug=True)
