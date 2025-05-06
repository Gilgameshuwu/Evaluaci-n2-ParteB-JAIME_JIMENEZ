import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = "ed904bdb-7088-4486-b5b2-d60ea98f7a43"

def geocoding(location, key):
    while location == "":
        location = input("Ingrese la ubicación nuevamente: ")
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({"q": f"{location}, Región Metropolitana, Chile", "limit": "1", "key": key})

    replydata = requests.get(url)
    json_data = replydata.json()
    json_status = replydata.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        name = json_data["hits"][0]["name"]
        value = json_data["hits"][0]["osm_value"]

        country = json_data["hits"][0].get("country", "")
        state = json_data["hits"][0].get("state", "")

        if state and country:
            new_loc = f"{name}, {state}, {country}"
        elif state:
            new_loc = f"{name}, {state}"
        else:
            new_loc = name

        print(f"URL API Geocodificación para {new_loc} (Tipo: {value})\n{url}")
    else:
        lat = lng = "null"
        new_loc = location
        if json_status != 200:
            print(f"Estado API: {json_status}\nError: {json_data.get('message', '')}")
    return json_status, lat, lng, new_loc

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de transporte disponibles:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("auto, bicicleta, pie, moto, camión, patinete, transporte público")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    perfiles = {"auto": "car", "bicicleta": "bike", "pie": "foot", "moto": "motorcycle", "camion": "small_truck", "patinete": "scooter", "transporte público": "pt"}

    vehiculo = input("Elija perfil de transporte: ").lower()
    if vehiculo in ["s", "salir"]:
        break
    vehiculo = perfiles.get(vehiculo, "car")

    loc1 = input("Ciudad a Comenzar: ").strip()
    if loc1 == "salir" or loc1 == "s":
        break

    orig = geocoding(loc1, key)

    loc2 = input("Ciudad que gusta terminar: ").strip()
    if loc2 == "salir" or loc2 == "s":
        break

    dest = geocoding(loc2, key)

    print("=================================================")
    if orig[0] == 200 and dest[0] == 200:
        if orig[3].lower() == dest[3].lower():
            print("Error: Las ciudades deben ser diferentes")
            continue

        params = {
            "key": key,
            "vehicle": vehiculo,
            "locale": "es",
            "point": [f"{orig[1]},{orig[2]}", f"{dest[1]},{dest[2]}"]
        }

        paths_url = route_url + urllib.parse.urlencode(params, doseq=True)
        respuesta = requests.get(paths_url)
        datos = respuesta.json()

        print(f"Estado API: {respuesta.status_code}\nURL: {paths_url}")
        print("=================================================")
        print(f"Ruta desde {orig[3]} hasta {dest[3]} en {vehiculo}")
        print("=================================================")

        if respuesta.status_code == 200:
            distancia_km = datos["paths"][0]["distance"]/1000
            tiempo_total_segundos = datos["paths"][0]["time"]/1000

            horas = int(tiempo_total_segundos // 3600)
            minutos = int((tiempo_total_segundos % 3600) // 60)
            segundos = int(tiempo_total_segundos % 60)

            print(f"Distancia: {distancia_km:.2f} km")
            print(f"Duración: {horas:02d} h | {minutos:02d} m | {segundos:02d} s")
            print("=================================================")

            print("Narrativa del viaje:")
            for paso in datos["paths"][0]["instructions"]:
                texto = paso["text"]
                distancia = paso["distance"]/1000
                print(f"- {texto} ({distancia:.2f} km)")

        else:
            print(f"Error de la API de enrutamiento: {datos.get('message', 'Error desconocido')}")

    print("=============================================")