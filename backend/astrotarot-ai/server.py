from flask import Flask, request, jsonify 
import json

# Cargar los archivos JSON
with open("astroTarotData.json", "r", encoding="utf-8") as f:
    astro_tarot_data = json.load(f)

with open("carta natal tomy.json", "r", encoding="utf-8") as f:
    carta_natal_tomy = json.load(f)

app = Flask(__name__)

@app.route("/interpretar", methods=["GET"])
def interpretar():
    consulta = request.args.get("consulta", "").lower()
    
    # Ver si el usuario pide ver la estructura completa
    if consulta == "debug":
        return jsonify({"estructura_carta_natal": carta_natal_tomy})
    
    # Buscar en la base de datos de astrología
    if "tarot" in astro_tarot_data and "arcanos_mayores" in astro_tarot_data["tarot"] and consulta in astro_tarot_data["tarot"]["arcanos_mayores"]:
        respuesta = astro_tarot_data["tarot"]["arcanos_mayores"][consulta]
        return jsonify({"tipo": "arcano mayor", "nombre": consulta, "descripcion": respuesta["descripcion"], "efectos": respuesta["efectos"]})
    
    # Buscar información en la carta natal de Tomy
    if "carta_astral" in carta_natal_tomy:
        datos_personales = carta_natal_tomy["carta_astral"].get("datos_personales", {})
        interpretaciones = carta_natal_tomy["carta_astral"].get("interpretaciones", {})
        signos_data = datos_personales.get("signos", {})
        
        # Mapear consultas a los nombres correctos
        signos_claves = {"solar": "sol", "lunar": "luna", "ascendente": "ascendente"}
        
        for clave, nombre in signos_claves.items():
            if consulta == signos_data.get(clave, "").lower():
                descripcion = interpretaciones.get(nombre, {}).get("descripcion", "Sin descripción disponible.")
                return jsonify({"tipo": "signo", "nombre": consulta.capitalize(), "descripcion": descripcion})
    
    return jsonify({"mensaje": "No se encontró información para la consulta."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
