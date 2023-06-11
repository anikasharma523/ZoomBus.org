import mysql
from flask import Flask, render_template, request, redirect,session
import mysql.connector as connection
import yaml
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL



app=Flask(__name__)
Bootstrap(app)


#configuring db
db = yaml.load(open('db.yaml'),Loader=yaml.FullLoader)
app.config['MYSQL_HOST']= db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
app.secret_key = 'jiokk'
mysql1=MySQL(app)

mydb = mysql.connector.connect(user='root', password='606609',host='localhost',database='bussapp2')
mycursor = mydb.cursor()
mycursor.execute("select year(date_for),count(*) from bookings group by year(date_for) order by count(*) desc limit 1")
max_bookings = mycursor.fetchall()

mycursor.execute("select bus_id from bookings group by bus_id order by count(*) desc limit 1")
max_bus_id = mycursor.fetchone()

mycursor.execute("select source, dest from bus_details where bus_id=%s", max_bus_id)
s_d_data = mycursor.fetchall()


data=[]
data=max_bookings+[max_bus_id]+s_d_data
print(data)
'''
#mycursor.execute("call revenue_for(2022)")
#revenue_this_year= mycursor.fetchall()

data=[]
data=max_bookings+[max_bus_id]+s_d_data

for i in mycursor:
    Book_ID.append(i[0])
    User_ID.append(i[1])
    Bus_ID.append(i[2])
    Date_Booking.append(i[3])
    Time_Booking.append(i[4])
    Date_For.append(i[5])
    Total_Seats.append(i[6])

bookings_df = pd.DataFrame(list(zip(Book_ID, User_ID, Bus_ID, Date_Booking, Time_Booking, Date_For, Total_Seats)),columns =['Booking ID', 'User_ID', 'Bus_ID', 'Date_Booking', 'Time_Booking', 'Date_For', 'Total_Seats'])
'''


@app.route('/statistics')
def report():
    return render_template('statistics.html', data=data)

@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method=='POST':
        # fetch form data
        userDetails=request.form
        name=userDetails['name']
        email=userDetails['email']
        password=userDetails['password']
        cur=mysql1.connection.cursor()
        cur.execute("Insert into users(user_name, user_email, user_password) values(%s, %s, %s)", (name, email, password))
        mysql1.connection.commit()
        cur.close()
        return redirect('/users')
    return render_template('signin.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur = mysql1.connection.cursor()
        cur.execute('SELECT * FROM users WHERE user_name = % s AND user_password = % s', (username, password,))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = request.form['username']
            msg = 'Logged in successfully !'
            if (username == "admin"):
                return redirect('/add_bus')
            else:
                return redirect('/search')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)





@app.route('/add_bus', methods=['GET', 'POST'])
def add_bus_admin():
    if request.method == 'POST':
        busDetails = request.form
        source = busDetails['source']
        destination = busDetails['destination']
        capacity = busDetails['capacity']
        price = busDetails['price']
        duration = busDetails['duration']
        cur = mysql1.connection.cursor()
        cur.execute("Insert into bus_details(source,dest,capacity,price,duration) values(%s,%s,%s,%s,%s)",
                    (source,destination,capacity,price,duration))
        mysql1.connection.commit()
        cur.close()
        return redirect('/bus_details')
    return render_template('add_bus.html')

@app.route('/add_driver', methods=['GET', 'POST'])
def add_driver():
    if request.method == 'POST':
        driverDetails = request.form
        driver_name = driverDetails['driver_name']
        driver_email = driverDetails['driver_email']
        driver_phone = driverDetails['driver_phone']
        bus_id = driverDetails['bus_id']
        cur = mysql1.connection.cursor()
        cur.execute("Insert into drivers(driver_name, driver_email,driver_phone, bus_id) values(%s,%s,%s,%s)",(driver_name, driver_email, driver_phone,bus_id))
        mysql1.connection.commit()
        cur.close()
        return redirect('/driver_details')
    return render_template('add_driver.html')

@app.route('/del_bus', methods=['GET', 'POST'])
def del_bus():
    if request.method == 'POST':
        busdetails = request.form
        buss_id = busdetails['bus_id']
        cur = mysql1.connection.cursor()
        cur.execute("Delete from bus_details where bus_id= % s " % buss_id)
        mysql1.connection.commit()
        cur.close()
        return redirect('/bus_details')
    return render_template('del_bus.html')

@app.route('/cancellation', methods=['GET','POST'])
def delete_booking():
    if request.method =='POST':
        deletion = request.form
        busiid = deletion['cancel_busid']
        cur = mysql.connection.cursor()
        cur.execute("delete from bookings where bus_id =%s", [busiid])
        mysql.connection.commit()
        cur.close()
    return render_template('cancellation.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        book = request.form
        source_bus = book['source']
        dest_bus = book['destination']
        cur = mysql1.connection.cursor()
        cur.execute("SELECT * from bus_details WHERE Source LIKE %s AND Dest LIKE %s", (source_bus, dest_bus))
        mysql1.connection.commit()
        data = cur.fetchall()
        cur.close()
        # all in the search box will return all the tuples
        if len(data) == 0 and book == 'all':
            cur.execute("SELECT * from bus_details")
            mysql1.connection.commit()
            data = cur.fetchall()
        return render_template('search.html', data=data)
    return render_template('search.html')

@app.route('/bookbus', methods=['GET', 'POST'])
def bookbus():
    if request.method == "POST":
        booking=request.form
        busid = booking['busid']
        tickets=booking['tickets']
        date_travel=booking['datetravel']
        user_name=booking['user_confirm']
        cur = mysql1.connection.cursor()
        cur.execute("insert into bookings(user_email, bus_id, date_booking, time_booking, date_for, total_seats) values((select user_id from users where user_email=%s), %s, curdate(), current_time(), %s, %s)",(user_name, busid, date_travel, tickets))
        mysql1.connection.commit()
        cur.close()
    return render_template('bookbus.html')

@app.route('/delete_bus', methods=['GET','POST'])
def delete_bus():
    if request.method == 'POST':
        delete = request.form
        busid = delete['busid']
        cur = mysql1.connection.cursor()
        cur.execute("delete from bus_details where bus_id=%s",[busid])
        mysql1.connection.commit()
        cur.close()
    return render_template('del_bus.html')

@app.route('/del_driver', methods=['GET','POST'])
def del_driver():
    if request.method == 'POST':
        delete = request.form
        driverid = delete['driver_id']
        cur = mysql1.connection.cursor()
        cur.execute("delete from drivers where driver_id=%s", [driverid])
        mysql1.connection.commit()
        cur.close()
    return render_template('del_driver.html')

@app.route('/users')
def users():
    cur = mysql1.connection.cursor()
    resultVal = cur.execute("SELECT * FROM users")
    if resultVal>0:
        user_details = cur.fetchall()
        return render_template('users.html',userDetails=user_details)

@app.route('/viewbooking', methods=['GET','POST'])
def view_bookings():
    if request.method == 'POST':
        booking = request.form
        email = booking['viewbooking']
        cur = mysql1.connection.cursor()
        cur.execute("SELECT * from bookings WHERE user_email LIKE %s", [email])
        mysql1.connection.commit()
        data = cur.fetchall()
        if len(data) > 0:
            return render_template('viewbooking.html', data=data)
    return render_template('viewbooking.html')

@app.route('/driver_details')
def driver_details():
    cur = mysql1.connection.cursor()
    resultVal = cur.execute("SELECT * FROM drivers")
    if resultVal>0:
        driver_details = cur.fetchall()
        return render_template('driver_details.html',driverDetails=driver_details)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/bus_details')
def bus_details():
    cur = mysql1.connection.cursor()
    resultVal = cur.execute("SELECT * FROM bus_details")
    if resultVal>0:
        bus_details = cur.fetchall()
        return render_template('bus_details.html',busDetails=bus_details)

if __name__ == "__main__":
    app.run(debug=True)