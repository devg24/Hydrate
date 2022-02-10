import mysql.connector
from flask import redirect,request,render_template,session,Flask
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)
app.secret_key="hellos"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = mysql.connector.connect(host='localhost',user='root',passwd='9810401668',database='dev')
cursor=db.cursor()


@app.route("/index")
def index():
    if session.get("user") != None:
        cursor.execute('select weight,datediff(curdate(),date),req_water from users where name = %s',(session["user"],))
        data = cursor.fetchall()
        if len(data)==1 and data[0][1] >= 1:
            cursor.execute('update users set req_water = %s,date = curdate() where name = %s',(int(data[0][0])/2,session["user"]))
            db.commit()
        return render_template("index.html",data = data)
    else:
        return redirect("/login")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        cursor.execute("select name,pass_hash from users where name = %s",(request.form.get("username"),))
        data = cursor.fetchall()
        if request.form.get("username")=="" or request.form.get("password")=="":
            return render_template("apology.html")
        elif len(data) != 1 or not check_password_hash(data[0][1],request.form.get("password")):
            return render_template("apology.html")
        else:
            session["user"]= request.form.get("username")
            return redirect("/index")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    else:
        if request.form.get("username") == "" or request.form.get("password") == "" or request.form.get("confirm") == "" or request.form.get("weight") == "":
            return render_template("apology.html")
        else:
            cursor.execute('insert into users(name,pass_hash,weight,req_water,date) values (%s,%s,%s,%s,curdate())',(request.form.get("username"),generate_password_hash(request.form.get("password")),float(request.form.get("weight")),float(request.form.get("weight"))/2))
            db.commit()
            return redirect("/login")

@app.route("/add",methods=["GET","POST"])
def add():
    if session.get("user") != None:
        if request.method=="GET":
            cursor.execute("select intake,time,datediff(curdate(),date(time)) from intake where name=%s",(session["user"],))
            data1=cursor.fetchall()
            for i in data1:
                if i[2]>=3:
                    data1.remove(i)
            return render_template("add.html",data=data1)
        else:
            num = request.form.get("water")
            if num != "":
                cursor.execute('update users set req_water = req_water - %s where name = %s',(float(num)*0.033814,session["user"]))
                cursor.execute('insert into intake values(%s,%s,current_timestamp())',(session["user"],float(num)))
                db.commit()
                return redirect("/index")
            else:
                return render_template("apology.html")
    else:
        return render_template("apology.html")

@app.route("/logout")
def logout():
    session.pop("user")
    session.clear()
    return redirect("/login")

@app.route("/activity",methods=["GET","POST"])
def activity():
    if request.method=="GET":
        cursor.execute("select info,time,name,datediff(curdate(),date(time)) from activity where name=%s",(session["user"],))
        data2=cursor.fetchall()
        for i in data2:
            if i[3] >= 3:
                data2.remove(i)
        return render_template("activity.html",data=data2)
    else:
        cal=float(request.form.get("cal"))
        cursor.execute("insert into activity values(%s,current_timestamp(),%s)",(int(cal),session["user"]))
        cursor.execute("update users set req_water=req_water + %s where name = %s",(cal/7000,session["user"]))
        db.commit()
        return redirect("/index")

@app.route("/")
def home():
    return render_template("home.html")
