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

    return redirect(url_for('Index'))

@app.route('/edit')
def edit_pet():
    return 'Editar mascotas'

@app.route('/delete')
def delete_pet():
    return 'Elimiar Mascota'



if __name__ == '__main__':
    app.run(port=3000, debug= True)