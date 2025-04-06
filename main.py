import LanusStats
import json
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

sofascore = LanusStats.SofaScore()
response = sofascore.get_players_match_stats(
    'https://www.sofascore.com/es/football/match/adc-juan-pablo-ii-alianza-lima/lWsgzee#id:13387774')
print(response)
jugadores = []

for index, row in response[0].iterrows():
    print(row)
    jugador = {}
    jugador['id'] = row['slug']
    jugador['name'] = row['name']
    jugador['short'] = row['shortName']
    jugador['equipo'] = row['team']
    jugador['country'] = row['country']['name']
    jugador['posicion'] = str(row['position'])[12:13]
    jugador['puntos'] = 0  # Inicia en 0, un número válido

    # Validar todos los campos antes de usarlos
    jugador['minutos'] = row['minutesPlayed'] if pd.notna(row['minutesPlayed']) else 0
    if jugador['minutos'] > 60:
        jugador['puntos'] += 2
    elif 10 < jugador['minutos'] <= 60:
        jugador['puntos'] += 1
    if jugador['minutos'] >= 90:
        jugador['puntos'] += 1

    jugador['goles'] = row['goals'] if pd.notna(row['goals']) else 0
    if jugador['posicion'] == 'G':
        jugador['puntos'] += 10 * jugador['goles']
    elif jugador['posicion'] == 'D':
        jugador['puntos'] += 6 * jugador['goles']
    elif jugador['posicion'] == 'M':
        jugador['puntos'] += 5 * jugador['goles']
    elif jugador['posicion'] == 'F':
        jugador['puntos'] += 4 * jugador['goles']

    jugador['asistencias'] = row['goalAssist'] if pd.notna(row['goalAssist']) else 0
    jugador['puntos'] += 3 * jugador['asistencias']

    jugador['atajadas'] = row['saves'] if pd.notna(row['saves']) else 0
    jugador['puntos'] += jugador['atajadas'] // 3

    jugador['faltasProvocadas'] = row['wasFouled'] if pd.notna(row['wasFouled']) else 0
    jugador['puntos'] += 0.75 * jugador['faltasProvocadas']

    jugador['passesTotal'] = row['totalPass'] if pd.notna(row['totalPass']) else 0
    jugador['pasesBuenos'] = row['accuratePass'] if pd.notna(row['accuratePass']) else 0
    porcentajeCorrectos = (jugador['pasesBuenos'] / jugador['passesTotal']) * 100 if jugador['passesTotal'] > 0 else 0
    if jugador['passesTotal'] > 30:
        if porcentajeCorrectos >= 90:
            jugador['puntos'] += 6
        elif porcentajeCorrectos >= 80:
            jugador['puntos'] += 4
        elif porcentajeCorrectos >= 70:
            jugador['puntos'] += 2

    jugador['tirosDesviados'] = row['shotOffTarget'] if pd.notna(row['shotOffTarget']) else 0
    jugador['puntos'] += 0.25 * jugador['tirosDesviados']

    jugador['tirosPuerta'] = row['onTargetScoringAttempt'] if pd.notna(row['onTargetScoringAttempt']) else 0
    jugador['puntos'] += 0.5 * jugador['tirosPuerta']

    jugador['Entradas'] = row['totalCross'] if pd.notna(row['totalCross']) else 0
    jugador['puntos'] += jugador['Entradas']

    jugador['duelosAereos'] = row['aerialWon'] if pd.notna(row['aerialWon']) else 0
    jugador['puntos'] += 0.5 * jugador['duelosAereos']

    jugador['atajoPenal'] = False
    jugador['falloPenal'] = False
    jugador['ordenPuntosPartido'] = False
    jugador['resultadoPartido'] = ''

    jugadores.append(jugador)

print(json.dumps(jugadores, indent=4, ensure_ascii=False))