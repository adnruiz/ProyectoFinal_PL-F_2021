from logging import debug
from flask import Flask

#Este codigo es para iniciar el servidor
app = Flask(__name__)

#Rutas para nuestra app
@app.route('/')
def Index():
    return 'Hello World'

@app.route('/add_pet')
def add_pet():
    return 'Aqui debemos agregar las mascotas.'

@app.route('/edit')
def edit_pet():
    return 'Editar mascotas'

@app.route('/delete')
def delete_pet():
    return 'Elimiar Mascota'



if __name__ == '__main__':
    app.run(port=3000, debug= True)