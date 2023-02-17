import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sender_email = "shriya.deshpande@cumminscollege.in"
receiver_email = "sayali.y.deshmukh@cumminscollege.in"
message = MIMEMultipart()
message["From"] = sender_email
message['To'] = receiver_email
message['Subject'] = "UBS Hackathon"
text = "Hi,Sayali"
message.attach(MIMEText(text))


my_message = message.as_string()
email_session = smtplib.SMTP('smtp.gmail.com', 587)
email_session.starttls()
email_session.login(sender_email, password)
email_session.sendmail(sender_email, receiver_email, my_message)
email_session.quit()
