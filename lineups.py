from json import JSONDecoder
import psycopg2  # Reemplazamos pyodbc por psycopg2
import LanusStats
import json
import pandas as pd
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Configuración de la conexión a PostgreSQL
try:
    connection = psycopg2.connect(
        host="localhost",  # Si está en tu máquina local
        database="fantasy",  # Nombre de tu base de datos
        user="postgres",  # Tu usuario de PostgreSQL (cámbialo si es diferente)
        password="Jp202020",  # Tu contraseña de PostgreSQL
        port="5432"  # Puerto por defecto de PostgreSQL
    )
    print("Conexión exitosa a la base de datos")

    # Crear un cursor para ejecutar consultas
    cursor = connection.cursor()

except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

# Tu código existente
sofascore = LanusStats.SofaScore()
response = sofascore.get_lineups("https://www.sofascore.com/es/football/match/alianza-universidad-universitario/fWskIxc#id:13523625")


# Ejemplo de cómo guardar los datos en la base de datos
# Primero, crear una tabla (esto es un ejemplo, ajústalo a tus necesidades)




# Insertar los jugadores en la base de datos
for player in response['home']['players']:
    print(json.dumps(player['player'], indent=4, ensure_ascii=False))
    name = player['player']['name'].replace('\'', '')
    shortname = player['player']['shortName'].replace('\'', '')
    pais = player['player']['country']['name'] if 'name' in player['player']['country'].keys() else 'Peru'
    # Ejemplo de inserción
    insert_query = f"""
    INSERT INTO players (slug, name, shortname, position, country, team)
    VALUES ('{player['player']['slug']}', '{name}', '{shortname}', '{player['player']['position']}', '{pais}', 'Universitario')
    """
    try:
        cursor.execute(insert_query)
    except Exception as e:
        continue

# Confirmar los cambios
connection.commit()

# Cerrar la conexión
cursor.close()
connection.close()
print("Conexión cerrada")