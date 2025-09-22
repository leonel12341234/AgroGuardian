from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por una clave segura

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,  # Puerto por defecto de XAMPP
    'user': 'root',
    'password': 'admin123',  
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
                cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['user_email'] = user['email']
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
                cursor.execute("SELECT id FROM usuario WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('El email ya está registrado', 'error')
                    return render_template('register.html')
                
                # Insertar nuevo usuario
                cursor.execute(
                    "INSERT INTO usuario (email, password) VALUES (%s, %s)",
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

@app.route('/silos', methods=['POST'])
def crear_silo():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para guardar datos del silo', 'error')
        return redirect(url_for('login'))

    if request.is_json:
        payload = request.get_json(silent=True) or {}
        tipo_grano = payload.get('tipo_grano')
        capacidad = payload.get('capacidad')
        ocupacion = payload.get('ocupacion')
        humedad = payload.get('humedad')
        temperatura = payload.get('temperatura')
    else:
        tipo_grano = request.form.get('tipo_grano')
        capacidad = request.form.get('capacidad')
        ocupacion = request.form.get('ocupacion')
        humedad = request.form.get('humedad')
        temperatura = request.form.get('temperatura')

    # Validar campos mínimos
    if not all([tipo_grano, capacidad, ocupacion, humedad, temperatura]):
        if request.is_json:
            return jsonify({
                'ok': False,
                'message': 'Completa todos los campos del formulario.'
            }), 400
        else:
            flash('Completa todos los campos del formulario.', 'error')
            return redirect(url_for('dashboard'))

    try:
        capacidad_val = int(float(capacidad))
        ocupacion_val = int(float(ocupacion))
        humedad_val = int(float(humedad))
        temperatura_val = int(float(temperatura))
    except ValueError:
        if request.is_json:
            return jsonify({
                'ok': False,
                'message': 'Los campos numéricos deben ser válidos.'
            }), 400
        else:
            flash('Los campos numéricos deben ser válidos.', 'error')
            return redirect(url_for('dashboard'))

    connection = get_db_connection()
    if not connection:
        if request.is_json:
            return jsonify({'ok': False, 'message': 'No se pudo conectar a la base de datos.'}), 500
        else:
            flash('No se pudo conectar a la base de datos.', 'error')
            return redirect(url_for('dashboard'))

    try:
        cursor = connection.cursor()
        # Asegurar columna fecha en tabla silos (MariaDB soporta IF NOT EXISTS)
        try:
            cursor.execute(
                "ALTER TABLE silos ADD COLUMN IF NOT EXISTS fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )
            connection.commit()
        except Exception:
            # Si falla (ya existe o motor no soporta), continuar
            connection.rollback()

        cursor.execute(
            """
            INSERT INTO silos (user_id, tipo_grano, capacidad, Ocupacion, Humedad, Temperatura, fecha)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session['user_id'],
                tipo_grano,
                capacidad_val,
                ocupacion_val,
                humedad_val,
                temperatura_val,
                datetime.now(),
            ),
        )
        connection.commit()
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error DB (silos insert): {err}")
        if request.is_json:
            return jsonify({'ok': False, 'message': 'Error al guardar los datos del silo.'}), 500
        else:
            flash('Error al guardar los datos del silo.', 'error')
            return redirect(url_for('dashboard'))
    finally:
        cursor.close()
        connection.close()

    # Construir análisis para respuesta JSON y para UI
    porcentaje_ocupacion = 0
    try:
        porcentaje_ocupacion = round((ocupacion_val / capacidad_val) * 100, 2) if capacidad_val else 0
    except Exception:
        porcentaje_ocupacion = 0
    estado = '⚠️ Atención: condiciones críticas detectadas.' if (humedad_val > 14 or temperatura_val > 30) else '✅ Condiciones normales.'

    if request.is_json:
        return jsonify({
            'ok': True,
            'message': 'Datos del silo guardados correctamente.',
            'analisis': {
                'estado': estado,
                'porcentaje_ocupacion': porcentaje_ocupacion,
                'ocupacion': ocupacion_val,
                'capacidad': capacidad_val,
                'humedad': humedad_val,
                'temperatura': temperatura_val,
                'tipo_grano': tipo_grano
            }
        })
    else:
        flash('Datos del silo guardados correctamente.', 'success')
        return redirect(url_for('dashboard'))

@app.route('/historial')
def historial():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder al historial', 'error')
        return redirect(url_for('login'))

    connection = get_db_connection()
    if not connection:
        flash('No se pudo conectar a la base de datos.', 'error')
        return render_template('Historial.html', registros=[])

    registros = []
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, user_id, tipo_grano, capacidad, Ocupacion, Humedad, Temperatura, COALESCE(fecha, NOW()) AS fecha FROM silos WHERE user_id = %s ORDER BY fecha DESC, id DESC",
            (session['user_id'],)
        )
        registros = cursor.fetchall() or []
    except mysql.connector.Error as err:
        print(f"Error consultando silos: {err}")
        flash('Error al cargar el historial.', 'error')
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()

    return render_template('Historial.html', registros=registros)

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