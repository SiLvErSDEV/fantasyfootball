from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor  # Para obtener resultados como diccionarios
import json
import os
from flask_cors import CORS

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    return conn

@app.route('/api/team-selection', methods=['POST'])
def save_team_selection():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        players = data.get('players', [])

        if not user_id:
            return jsonify({"error": "ID de usuario requerido"}), 400

        if not players:
            return jsonify({"error": "No se enviaron jugadores"}), 400

        # Conectar a la base de datos
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Verificar si ya existe un equipo para este usuario con fecha 8
        cursor.execute(
            "SELECT idequipo FROM equipos WHERE idusuario = %s AND fecha = %s",
            (user_id, 8)
        )
        existing_team = cursor.fetchone()

        # Preparar los datos de los jugadores (usamos slug)
        # Rellenamos con None si hay menos de 11 jugadores
        player_slugs = [player.get('slug') for player in players] + [None] * (11 - len(players))

        if existing_team:
            # Actualizar registro existente
            query = """
                UPDATE equipos 
                SET 
                    jugador1 = %s,
                    jugador2 = %s,
                    jugador3 = %s,
                    jugador4 = %s,
                    jugador5 = %s,
                    jugador6 = %s,
                    jugador7 = %s,
                    jugador8 = %s,
                    jugador9 = %s,
                    jugador10 = %s,
                    jugador11 = %s,
                    totalpuntos = %s
                WHERE idequipo = %s
            """
            cursor.execute(query, (
                player_slugs[0],
                player_slugs[1],
                player_slugs[2],
                player_slugs[3],
                player_slugs[4],
                player_slugs[5],
                player_slugs[6],
                player_slugs[7],
                player_slugs[8],
                player_slugs[9],
                player_slugs[10],
                '0',  # totalpuntos por defecto
                existing_team['idequipo']
            ))
        else:
            # Insertar nuevo registro
            query = """
                INSERT INTO equipos (
                    idusuario, fecha, 
                    jugador1, jugador2, jugador3, jugador4, jugador5,
                    jugador6, jugador7, jugador8, jugador9, jugador10,
                    jugador11, totalpuntos
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING idequipo
            """
            cursor.execute(query, (
                user_id,
                8,  # fecha fija en 8
                player_slugs[0],
                player_slugs[1],
                player_slugs[2],
                player_slugs[3],
                player_slugs[4],
                player_slugs[5],
                player_slugs[6],
                player_slugs[7],
                player_slugs[8],
                player_slugs[9],
                player_slugs[10],
                '0'  # totalpuntos por defecto
            ))

        # Confirmar los cambios
        conn.commit()

        # Imprimir para depuración
        print(f"Equipo guardado para usuario {user_id}:")
        for i, slug in enumerate(player_slugs[:len(players)], 1):
            print(f"Jugador {i}: {slug}")

        # Respuesta exitosa
        return jsonify({
            "message": "Equipo guardado exitosamente",
            "userId": user_id,
            "playerCount": len(players)
        }), 200

    except Exception as e:
        print(f"Error procesando la selección de equipo: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"error": "Error interno al procesar la selección"}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Ruta para obtener todos los jugadores
@app.route('/api/players', methods=['GET'])
def get_all_players():
    try:
        # Obtener conexión
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

        # Crear cursor que devuelve diccionarios
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Ejecutar query
        cursor.execute("SELECT * FROM players")
        players = cursor.fetchall()

        # Cerrar cursor y conexión
        cursor.close()
        conn.close()

        # Convertir los resultados a una lista de diccionarios
        return jsonify(players), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/users', methods=['POST'])
def validate_user():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        # Obtener el código de acceso del request
        data = request.get_json()
        access_code = data.get('accesscode')

        if not access_code:
            return jsonify({"error": "Código de acceso requerido"}), 400

        # Crear cursor que devuelve diccionarios
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Consultar el usuario por el código de acceso
        query = "SELECT * FROM usuarios WHERE accesscode = %s"
        cursor.execute(query, (access_code,))
        user = cursor.fetchone()

        if user:
            # Convertir el resultado a un diccionario serializable
            user_dict = dict(user)
            return jsonify(user_dict), 200
        else:
            return jsonify({"error": "Código de acceso inválido"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

# Ruta básica para verificar que el servidor funciona
@app.route('/')
def home():
    return "¡Bienvenido a la API de Fantasy!"


# Correr la aplicación
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)