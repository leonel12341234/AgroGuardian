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


def analizar_condiciones_por_grano(tipo_grano: str, humedad: int, temperatura: int):
    """Devuelve el mensaje recomendado y si está dentro/fuera de rango para el grano dado."""
    if not tipo_grano:
        tipo = ''
    else:
        tipo = tipo_grano.strip().lower()


    # Rangos recomendados por grano
    rangos = {
        'soja': {'humedad_max': 13, 'temp_min': 25, 'temp_max': 30},
        'maiz': {'humedad_max': 14, 'temp_min': 25, 'temp_max': 30},
        'maíz': {'humedad_max': 14, 'temp_min': 25, 'temp_max': 30},
        'trigo': {'humedad_max': 14, 'temp_min': 20, 'temp_max': 25},
        'girasol': {'humedad_max': 10, 'temp_min': 20, 'temp_max': 25},
        'cebada': {'humedad_max': 13, 'temp_min': 20, 'temp_max': 25},
    }


    # Normalización para cubrir "maíz" y "maiz"
    tipo_clave = 'maíz' if tipo in ('maiz', 'maíz') else tipo
    r = rangos.get(tipo_clave)
    if not r:
        # Si no se reconoce el grano, usar un rango por defecto amplio para no falsear
        r = {'humedad_max': 14, 'temp_min': 20, 'temp_max': 30}


    dentro_humedad = humedad <= r['humedad_max']
    dentro_temperatura = r['temp_min'] <= temperatura <= r['temp_max']


    if not dentro_humedad or not dentro_temperatura and (humedad > r['humedad_max'] or temperatura > r['temp_max']):
        mensaje = f"⚠️ Atención: condiciones críticas para {tipo_grano}. Riesgo de deterioro. Recomendación: ventilar el silo y controlar periódicamente."
        estado = 'critico'
    elif humedad < 0 or temperatura < -50:
        # Valores imposibles, fallback
        mensaje = f"ℹ️ Valores atípicos detectados para {tipo_grano}. Verifica los sensores."
        estado = 'atipico'
    elif humedad < r['humedad_max'] or temperatura < r['temp_min']:
        if dentro_humedad and dentro_temperatura:
            # Ya cubierto por el caso óptimo más abajo, no entra aquí
            pass
        mensaje = f"ℹ️ Condiciones por debajo de lo óptimo en {tipo_grano}. Recomendación: verificar la hermeticidad del silo o considerar un calentamiento controlado para evitar daños."
        estado = 'bajo'
    else:
        mensaje = f"✅ Condiciones óptimas para {tipo_grano}. El silo se encuentra en buen estado."
        estado = 'optimo'


    analisis = {
        'mensaje': mensaje,
        'estado': estado,
        'humedad_max': r['humedad_max'],
        'temp_min': r['temp_min'],
        'temp_max': r['temp_max'],
    }
    return analisis


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
            # Esto es propenso a fallar en algunos MySQL, pero se deja por robustez si la DB lo soporta.
            # Si falla, simplemente se hace rollback y se sigue, asumiendo que la columna existe.
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
        nuevo_id = cursor.lastrowid
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
    analisis_grano = analizar_condiciones_por_grano(tipo_grano, humedad_val, temperatura_val)
    estado = analisis_grano['mensaje']


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
                'tipo_grano': tipo_grano,
                'rangos': {
                    'humedad_max': analisis_grano['humedad_max'],
                    'temp_min': analisis_grano['temp_min'],
                    'temp_max': analisis_grano['temp_max'],
                }
            }
        })
    else:
        return redirect(url_for('resultados', silo_id=nuevo_id))


@app.route('/resultados/<int:silo_id>')
def resultados(silo_id: int):
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a los resultados', 'error')
        return redirect(url_for('login'))


    connection = get_db_connection()
    if not connection:
        flash('No se pudo conectar a la base de datos.', 'error')
        return redirect(url_for('dashboard'))


    registro = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, user_id, tipo_grano, capacidad, Ocupacion, Humedad, Temperatura, fecha FROM silos WHERE id = %s AND user_id = %s",
            (silo_id, session['user_id'])
        )
        registro = cursor.fetchone()
        if not registro:
            flash('Registro no encontrado.', 'error')
            return redirect(url_for('dashboard'))
    except mysql.connector.Error as err:
        print(f"Error obteniendo resultados: {err}")
        flash('Error al obtener resultados.', 'error')
        return redirect(url_for('dashboard'))
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()


    analisis_grano = analizar_condiciones_por_grano(
        registro['tipo_grano'], int(registro['Humedad']), int(registro['Temperatura'])
    )


    porcentaje_ocupacion = 0
    try:
        capacidad_val = int(registro['capacidad'])
        ocupacion_val = int(registro['Ocupacion'])
        porcentaje_ocupacion = round((ocupacion_val / capacidad_val) * 100, 2) if capacidad_val else 0
    except Exception:
        porcentaje_ocupacion = 0


    return render_template(
        'Resultados.html',
        registro=registro,
        analisis=analisis_grano,
        porcentaje_ocupacion=porcentaje_ocupacion,
    )


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
        # Agregar mensaje de recomendación por cada registro
        for r in registros:
            try:
                anal = analizar_condiciones_por_grano(r['tipo_grano'], int(r['Humedad']), int(r['Temperatura']))
                r['recomendacion'] = anal['mensaje']
            except Exception:
                r['recomendacion'] = '—'
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


# NUEVA RUTA: ELIMINAR HISTORIAL COMPLETO
@app.route('/historial/eliminar', methods=['POST'])
def eliminar_historial():
    """
    Maneja la solicitud POST para eliminar todos los registros de silos del usuario actual.
    """
    if 'user_id' not in session:
        flash('Debes iniciar sesión para realizar esta acción', 'error')
        return redirect(url_for('login'))


    user_id = session['user_id']
    connection = get_db_connection()


    if not connection:
        flash('Error de conexión a la base de datos. No se pudo eliminar el historial.', 'error')
        return redirect(url_for('historial'))


    try:
        cursor = connection.cursor()
       
        # Consulta SQL para eliminar todos los registros de silos asociados al user_id
        cursor.execute(
            "DELETE FROM silos WHERE user_id = %s",
            (user_id,)
        )
        connection.commit()
        flash('El historial de análisis ha sido ELIMINADO completamente.', 'success')
       
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error DB (eliminar historial): {err}")
        flash('Error al intentar eliminar el historial.', 'error')
       
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()
   
    # Redirige a la página de historial (que ahora estará vacía)
    return redirect(url_for('historial'))




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)



