import mysql.connector
import backend
# Creating connection object
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shriram@0731",
    database = "ubshack"
)


def insert_new_jd(role,desc):
    mycursor = mydb.cursor()
    sql = "INSERT INTO jd (Role, Description) VALUES (%s, %s)"
    val = (role,desc)
    if(role!='' and desc!=''):
        mycursor.execute(sql, val)
        mydb.commit()
        return "record inserted successfully!"

def display_table():
    mycursor = mydb.cursor()
    sql = "Select * from jd"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return data
def getrole():
    mycursor = mydb.cursor()
    sql = "Select Role from jd"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return data

def getallprofiles():
    mycursor = mydb.cursor()
    sql = "Select * from profiles"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    return data

def getjobdesc(job_title):
    mycursor = mydb.cursor()
    sql = "Select Description from jd where Role = %s"
    val = (job_title,)
    mycursor.execute(sql,val)
    data = mycursor.fetchall()
    print(data)
    if (len(data)!=0):
        return data[0]
    else:
        return False


def addsimilarityscore(name,score):
    mycursor = mydb.cursor()
    sql = "UPDATE profiles set similarity_score = %s where NAME = %s"
    val = (score,name)
    mycursor.execute(sql, val)
    mydb.commit()


def getmatchedprofiles():
        mycursor = mydb.cursor()
        sql = "Select NAME,similarity_score from profiles where similarity_score > 30 order by similarity_score desc"
        mycursor.execute(sql)
        data = mycursor.fetchall()
        #print(data)
        if (data != None):
            return data
        else:
            return False



def getmails_name():
    mycursor = mydb.cursor()
    sql = "Select NAME,EMAIL from profiles where similarity_score > 30 order by similarity_score desc"
    mycursor.execute(sql)
    data = mycursor.fetchall()
    print(data)
    mails=[]
    names=[]
    for i in data:
        mails.append(i[1])
        names.append(i[0])


    data =[mails,names]

    # print(data[0])
    # print(data[1])
    return data
# getmails_name()
