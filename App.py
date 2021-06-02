from os import name
import re

import MySQLdb
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, Response, session
from flask.helpers import flash
from flask_mysqldb import MySQL
from fpdf import FPDF
from functools import wraps




#Este codigo es para iniciar el servidor
app = Flask(__name__)

#Conexion a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ARuiz'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'menagerie'
mysql = MySQL(app)

#Settings
app.secret_key = 'mysecretkey'

#Rutas para nuestra app
@app.route('/')
def Index():
    return render_template('index.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None or session.get('loggedin') is None:
            return redirect('/login',code=302)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
   # Output message if something goes wrong...
    msg = ''

     # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
    
        password = password.encode('utf-8')
        
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        #bcrypt.checkpw(password, hashed_password)
        

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = md5(%s)', (username, hashed_password,))
        # Fetch one record and return result
        account = cursor.fetchone()

         # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            #id = account[0]
            #username = account[1]

            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg='') 

@app.route('/login/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        password = password.encode('utf-8')

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username,])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, hashed_password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/login/home')
@login_required
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pets')
@login_required
def pets():
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM pet')
    data = cursorMySQL.fetchall()
    return render_template('pets.html', pets = data)

@app.route('/events')
@login_required
def events():
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM event')
    data = cursorMySQL.fetchall()
    return render_template('events.html', events = data)

@app.route('/add_pet', methods=['POST'])
def add_pet():
    if request.method == 'POST':
        name = request.form['name']
        owner = request.form['owner']
        species = request.form['species']
        sex = request.form['sex']
        birth = request.form['birth']
        death = request.form['death']

        #Pasar datos a MySQL
        cursorMySQL = mysql.connection.cursor()
        cursorMySQL.execute('INSERT INTO pet (name, owner, species, sex, birth, death) VALUES (%s, %s, %s, %s, %s, %s)', 
        (name, owner, species, sex, birth, death))
        mysql.connection.commit()

        flash('Mascota agregada correctamente!')

    return redirect(url_for('pets'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        type = request.form['type']
        remark = request.form['remark']

        #pasar datos a mysql
        cursorMySQL = mysql.connection.cursor()
        cursorMySQL.execute('INSERT INTO event (name, date, type, remark) VALUES (%s, %s, %s, %s)',
        (name, date, type, remark))
        mysql.connection.commit()
        flash('Evento agregado correctamente.')
    return redirect(url_for('events'))
        

@app.route('/edit/<id>')
def edit_pet(id):
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM pet WHERE id = %s', [id])
    data = cursorMySQL.fetchall()
    print(data[0])
    return render_template('edit-pet.html', pet = data[0])

@app.route('/edit_event/<id>')
def edit_event(id):
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM event WHERE id = %s', [id])
    data = cursorMySQL.fetchall()
    print(data[0])
    return render_template('edit-event.html', event = data[0])

@app.route('/update/<id>', methods = ['POST'])
def update_pet(id):
    if request.method == 'POST':

        name = request.form['name']
        owner = request.form['owner']
        species = request.form['species']
        sex = request.form['sex']
        birth = request.form['birth']
        death = request.form['death']

        cursorMySQL = mysql.connection.cursor()

        cursorMySQL.execute(""" 
            UPDATE pet
            SET name = %s,
                owner = %s,
                species = %s,
                sex = %s,
                birth = %s,
                death = %s 
            WHERE id = %s
        """, [name, owner, species, sex, birth, death, id])
    
        flash('Mascota actualizada correctamente.')
        mysql.connection.commit()
        return redirect(url_for('Index'))

@app.route('/update_event/<id>', methods = ['POST'])
def update_event(id):
    if request.method == 'POST':

        name = request.form['name']
        date = request.form['date']
        type = request.form['type']
        remark = request.form['remark']

        cursorMySQL = mysql.connection.cursor()

        cursorMySQL.execute(""" 
            UPDATE event
            SET name = %s,
                date = %s,
                type = %s,
                remark = %s
            WHERE id = %s
        """, [name, date, type, remark, id])
    
        flash('Evento actualizado correctamente.')
        mysql.connection.commit()
        return redirect(url_for('events'))


@app.route('/delete/<string:id>')
def delete_pet(id):
    cursorMySQl = mysql.connection.cursor()
    cursorMySQl.execute('DELETE FROM pet WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Mascota removida correctamente')
    return redirect(url_for('pets'))
    
@app.route('/delete_event/<string:id>')
def delete_event(id):
    cursorMySQl = mysql.connection.cursor()
    cursorMySQl.execute('DELETE FROM event WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Evento removida correctamente')
    return redirect(url_for('events'))

@app.route('/download/report_pet/pdf')
def download_report_pets():
   
    pdf = FPDF('P', 'mm','A4')
    pdf.add_page()
    page_width = pdf.w - 2 
    pdf.set_font('Times', 'B', 14.0)
    pdf.set_fill_color(0,0,255)
    pdf.cell(190, 10, "Reporte de mascotas", 10, 25, "C")
    pdf.cell(15, 10, "ID", 1, 0)
    pdf.cell(35, 10, "Nombre", 1, 0)
    pdf.cell(38, 10, "Dueño", 1, 0)
    pdf.cell(30, 10, "Especie", 1, 0)
    pdf.cell(15, 10, "Sexo", 1, 0)
    pdf.cell(40, 10, "Nacimiento", 1, 0)
    pdf.cell(30, 10, "Muerte", 1, 1)
    

    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute("SELECT * FROM pet")
    resultado = cursorMySQL.fetchall()

    th = 14

    for reg in resultado:
        id = reg[0]
        name = reg[1]
        owner = reg[2]
        species = reg[3]
        sex = reg[4]
        birth = reg[5]
        death = reg[6]
        pdf.cell(15, 10, "id=%s" %(id), 1, 0)
        pdf.cell(35, 10, "name=%s" %(name,), 1, 0)
        pdf.cell(38, 10, "owner=%s" %(owner), 1, 0)
        pdf.cell(30, 10, "species=%s" %(species), 1, 0)
        pdf.cell(15, 10, "sex=%s" %(sex), 1, 0)
        pdf.cell(40, 10, "birth=%s" %(birth), 1, 0)
        pdf.cell(30, 10, "death=%s" %(death), 1, 0)
        pdf.ln(th)
    
    pdf.ln(14)
    pdf.cell(page_width, 0.0, '- end of report -')


    return pdf.output(name = "reporte_mascotas.pdf", dest = 'F')

        

    
if __name__ == '__main__':
    app.run(port=3000, debug= True)