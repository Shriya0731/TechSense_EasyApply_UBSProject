import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import DBConnection as db

sender_email = "shriya.deshpande@cumminscollege.in"


def send_mail(receiver_email, receiver_name):

    message = MIMEMultipart()
    message["From"] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "NEW JOB OPPORTUNITY ALERT"
    text ="Hey ,"+receiver_name+'''\n
It is our good pleasure to inform you that your Resume/profile has been selected online for our company’s direct recruitments. We came across your profile, and feel that your background is a direct match for the — role at UBS. 
We would like to invite you to the next round of interviews. 
.
If this is where you see your career grow please do confirm your interest to be a part of the process for this role by applying through the following link;
https://www.ubs.com/global/en/careers.html

Good Luck, We look forward to reading your response.
Regards, 

Amit Gupta
 HR Manager
 UBS,
 G.T. Karnal Road, 
Industrial Area, New Delhi - 91
 Email - appointment@post.com 
Contact No. – 09675715533, 08937914088

    '''


    message.attach(MIMEText(text))

    my_message = message.as_string()
    email_session = smtplib.SMTP('smtp.gmail.com', 587)
    email_session.starttls()
    email_session.login(sender_email, "Shriya@0731")
    email_session.sendmail(sender_email, receiver_email, my_message)
    email_session.quit()


def multiple_mails(mails,names):
    count = len(mails)
    i = 0
    while(i<count):
        send_mail(mails[i],names[i])
        i=i+1

