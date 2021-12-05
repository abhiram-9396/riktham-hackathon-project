from datetime import datetime
from flask import Flask, flash, render_template, request, session, redirect, url_for

import mysql.connector
from mysql.connector import cursor
from werkzeug.utils import secure_filename
import os


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="riktam"
)


app = Flask(__name__)
app.secret_key = 'your secret key'


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
   msg = ''
   if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
      email = request.form['email']
      password = request.form['password']
      cursor = mydb.cursor(buffered=True)

      # sql="select * from accounts where email=%s and password=%s",((email,password))
      cursor.execute(
          "select * from accounts where email=%s and password=%s", (email, password,))
      account = cursor.fetchone()

      if account:
         session['loggedin'] = True
         session['id'] = account[0]
         session['username'] = account[1]
         session['admin'] = account[4]
         flash('Logged in successfully!')

         return redirect(url_for('index'))
      else:
         msg = 'Incorrect username or password!'
   return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('admin', None)
   return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
   msg = ''
   if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'cpassword' in request.form:
      username = request.form['username']
      password = request.form['password']
      cpassword = request.form['cpassword']
      if cpassword != password:
         msg = 'password not matched'

      else:
         email = request.form['email']
         cursor = mydb.cursor()

         # sql="select * from accounts where email=%s",((email))
         cursor.execute("select * from accounts where email=%s", (email,))
         account = cursor.fetchone()
         if account:
            msg = 'account with this mail already exist!'
         else:
            sql = "INSERT INTO accounts(id,username,email,password) VALUES (NULL,%s,%s,%s)"
            val = (username, email, password)
            cursor.execute(sql, val)
            mydb.commit()
            flash("registered successfully! please login")
            return redirect(url_for('login'))
   elif request.method == 'POST':
      msg = 'please fill the details'
   return render_template('register.html', msg=msg)


@app.route("/index")
def index():
   if 'loggedin' in session:
        cursor=mydb.cursor()
        cursor.execute("select * from items order by id desc")
        items=cursor.fetchall()
        return render_template("index.html",items=items,admin=session['admin'])
   return redirect(url_for('login'))


@app.route("/request_item", methods=['GET', 'POST'])
def create():
   msg = ''
   if 'loggedin' in session:
       if request.method == 'POST' and 'title' in request.form and 'body':

            title = request.form['title']
            body = request.form['body']
            address_raised=request.form['address_raised']

            isprivate = 0
            if request.form.get('isprivate'):
                isprivate = 1

            cursor = mydb.cursor()

            # sql="select * from accounts where attachment=%s",((attachment))
            cursor.execute("select * from items where title=%s", (title,))
            item = cursor.fetchone()
            if item:
                msg = 'item already posted!'
            else:
                sql = "INSERT INTO items VALUES (NULL,%s,%s,NULL,%s,%s,%s,NULL)"
                val = (title, body, session['id'], isprivate,address_raised)
                cursor.execute(sql, val)
                mydb.commit()
                flash('item posted for request')
                return redirect(url_for('index'))
       elif request.method=='POST':
            msg='please fill the details'
       return render_template('requestitem.html',msg=msg,admin=session['admin'])
   return redirect(url_for('login'))


@app.route("/item/<int:item_id>")
def item(item_id):

    if 'loggedin' in session:

        cursor=mydb.cursor()
        cursor.execute("select * from items where id=%s",(item_id,))
        items=cursor.fetchone()
        created_by=items[4]


        cursor.execute("select * from accounts where id=%s",(created_by,))
        author=cursor.fetchone()
        author=author[1]

        return render_template('item.html',items=items,author=author,admin=session['admin'])
    return render_template('login.html')


@app.route("/update_item/<int:item_id>",methods=['GET','POST'])
def update_item(item_id):
   msg=''
   if 'loggedin' in session:
      if session['admin']==1  or session['admin']==0:
         cursor=mydb.cursor()
         cursor.execute("select * from items where id=%s",(item_id,))
         upitem=cursor.fetchone()
         if request.method == 'POST' and 'title' in request.form and 'body' in request.form:
            title = request.form['title']
            body = request.form['body']
            address_raised=request.form['address_raised']
            address_received=request.form['address_available']
            isprivate=0
            if request.form.get('isprivate'):
               isprivate=1

            cursor=mydb.cursor()
            cursor.execute("update items set title=%s,body=%s,private=%s,address_raised=%s,address_available=%s where id=%s",(title,body,isprivate,address_raised,address_received,item_id,))
            mydb.commit()
            flash('item updated successfully')
            return redirect(url_for('index'))
         elif request.method=='POST':
            msg='please fill the details'
      return render_template('update_item.html',upitem=upitem,msg=msg,admin=session['admin'])       
   return redirect(url_for('login'))

@app.route("/delete_item/<int:item_id>",methods=['GET','POST'])
def delete_item(item_id):
    if 'loggedin' in session:
        cursor=mydb.cursor()
        cursor.execute("delete from items where id=%s",(item_id,))
        mydb.commit()
        flash("circular deleted successfully")
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route("/display")
def display():
   if 'loggedin' in session:
      cursor=mydb.cursor()
      #sql="select * from accounts where id=%s",((session['id']))
      cursor.execute("select * from accounts where id=%s",(session['id'],))
      account=cursor.fetchone()
      return render_template('display.html',account=account,admin=session['admin'])
   return redirect(url_for('login'))
  




if __name__ == "__main__":
   app.run(debug=True)