from os import name
import re
from flask import Flask, render_template, request, redirect, url_for
from flask.helpers import flash
from flask_mysqldb import MySQL



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

@app.route('/pets')
def pets():
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM pet')
    data = cursorMySQL.fetchall()
    return render_template('pets.html', pets = data)

@app.route('/events')
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
    cursorMySQL.execute('SELECT * FROM pet WHERE id = %s', (id))
    data = cursorMySQL.fetchall()
    print(data[0])
    return render_template('edit-pet.html', pet = data[0])

@app.route('/edit_event/<id>')
def edit_event(id):
    cursorMySQL = mysql.connection.cursor()
    cursorMySQL.execute('SELECT * FROM event WHERE id = %s', (id))
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


if __name__ == '__main__':
    app.run(port=3000, debug= True)