from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,  # Puerto por defecto de XAMPP
    'user': 'root',
    'password': '',  # Contraseña por defecto de XAMPP (vacía)
    'database': 'agroguardian'
}

def get_db_connection():
    """Establece conexión con la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error conectando a la base de datos: {err}")
        return None

@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuario WHERE Gmail = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['contraseña'], password):
                    session['user_id'] = user['id']
                    session['user_email'] = user['Gmail']
                    flash('Inicio de sesión exitoso', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Credenciales incorrectas', 'error')
            except mysql.connector.Error as err:
                flash('Error en la base de datos', 'error')
                print(f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        
        # Validaciones
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('register.html')
        
        # Hash de la contraseña
        hashed_password = generate_password_hash(password)
        
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Verificar si el email ya existe
                cursor.execute("SELECT id FROM usuario WHERE Gmail = %s", (email,))
                if cursor.fetchone():
                    flash('El email ya está registrado', 'error')
                    return render_template('register.html')
                
                # Insertar nuevo usuario
                cursor.execute(
                    "INSERT INTO usuario (Gmail, contraseña) VALUES (%s, %s)",
                    (email, hashed_password)
                )
                connection.commit()
                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
                
            except mysql.connector.Error as err:
                flash('Error en la base de datos', 'error')
                print(f"Error: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Error de conexión a la base de datos', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al dashboard', 'error')
        return redirect(url_for('login'))
    return render_template('Dashboard.html')

@app.route('/historial')
def historial():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al historial', 'error')
        return redirect(url_for('login'))
    return render_template('Historial.html')

@app.route('/caracteristicas')
def caracteristicas():
    return render_template('caracteristicas.html')

@app.route('/beneficios')
def beneficios():
    return render_template('beneficios.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        # Aquí puedes agregar lógica para procesar el formulario de contacto
        nombre = request.form['nombre']
        email = request.form['email']
        asunto = request.form['asunto']
        mensaje = request.form['mensaje']
        
        # Por ahora solo mostramos un mensaje de confirmación
        flash('Mensaje enviado correctamente. Te contactaremos pronto.', 'success')
        return redirect(url_for('contacto'))
    
    return render_template('contacto.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)