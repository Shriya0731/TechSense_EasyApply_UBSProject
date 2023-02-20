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
        print(job_desc)
        skilldataset = backend.cleanprofilesdataset()
        backend.findsimilarityscore(job_desc,skilldataset)

    matchedprofiles = db.getmatchedprofiles()
    if (job_desc!=False):
        return render_template("profiles.html",usr=matchedprofiles,title=title,desc=job_desc[0])
    else:
        return render_template("noprofiles.html")

@app.route('/sendmails', methods = ['POST', 'GET'])
def sendmails():
    tot= int(request.form.get('tot'))
    title = request.form.get('title')
    print("For position "+title)
    print("Total mails to be sent:",tot)
    data = db.getmails_name()
    print("Mail Sent to:")
    print(data[1])
    send_mail.multiple_mails(data[0], data[1],tot,title)
    return render_template("mailsent.html")

@app.route('/displayrole')
def displayroles():
    #return db.getrole()
    # return render_template("table.html",usr=db.display_table())
    return render_template("job-desc.html",usr=db.getrole())


if __name__ == '__main__':
    app.run(debug=True)
