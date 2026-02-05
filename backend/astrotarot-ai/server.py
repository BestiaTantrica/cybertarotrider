from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from art_factory import ArtFactory

# Cargar los archivos JSON
with open("astroTarotData.json", "r", encoding="utf-8") as f:
    astro_tarot_data = json.load(f)

with open("carta natal tomy.json", "r", encoding="utf-8") as f:
    carta_natal_tomy = json.load(f)

app = Flask(__name__, static_folder="static")
CORS(app) # Permitir peticiones desde el frontend

# Inicializar Fábrica de Arte
art_factory = ArtFactory()
ASSETS_DIR = os.path.join(app.static_folder, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

@app.route("/generar-pasaporte", methods=["POST"])
def generar_pasaporte():
    """
    Endpoint para generar el 'Asset Bundle' del Pasaporte.
    Recibe datos natales (o usa los de Tomy por defecto).
    Devuelve URLs locales a las capas generadas.
    """
    data = request.json or {}
    # Si no nos pasan datos, usamos la carta de Tomy como semilla
    seed = 42240412 # Default seed
    
    # 1. Definir Prompts (Aquí se usaría EmotionEngine, hardcoded por ahora para test)
    prompts = {
        "back": "Abstract cosmic void, burnt edges, deep crimson, 8k cinematic",
        "mid": "Floating sharp crystalline shards, frozen structures, dark glass, cosmic dust",
        "front": "Electric plasma arcs, living fire filaments, bright energy core"
    }
    
    results = {}
    
    # 2. Generar capas con la Fábrica
    for layer, prompt in prompts.items():
        filename = f"{layer}_{seed}.png"
        
        # Intentar generar/obtener URL (ahora maneja Supabase internamente)
        asset_url = art_factory.generate_asset(prompt, seed, filename)
        
        if not asset_url:
            return jsonify({"error": f"Fallo generando capa {layer}"}), 500
        
        # El resultado ahora es una URL completa (Supabase) o relativa (Local)
        results[layer] = asset_url

    return jsonify({
        "status": "success",
        "layers": results,
        "config": {
            "pulse_speed": "FAST",
            "glow_color": "#00CCFF" 
        }
    })

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
