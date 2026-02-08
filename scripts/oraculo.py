
import os
import requests
import json
import sys
import datetime
import re

# Cargamos la llave desde el entorno
API_KEY = os.getenv("GOOGLE_API_KEY")
MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory")
THREADS_DIR = os.path.join(MEMORY_DIR, "threads")

if not API_KEY:
    print("❌ Error: No se encontro GOOGLE_API_KEY.")
    sys.exit(1)

def diagnostico_modelos():
    print("🔍 Diagnosticando modelos disponibles...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Modelos encontrados:")
            for m in models:
                print(f"  - {m['name']}")
            return True
        else:
            print(f"❌ Error de Diagnostico ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexion: {e}")
        return False

def chat_oraculo():
    # Este es el nombre exacto que aparecio en tu lista y suele tener cuota libre
    model_to_use = "gemini-flash-latest" 

    print(f"--- 🦅 ORACULO PEGASO (Modelo: {model_to_use}) ---")
    print("Escribe 'salir' para terminar.")
    
    full_transcript = ""

    while True:
        user_input = input(">> Operador: ")
        if user_input.lower() in ['salir', 'exit', 'quit']:
            break
        
        # Usamos v1beta que es donde vimos la lista
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_use}:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": user_input}]}]}
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.text}")
                continue
            
            data = response.json()
            answer = data['candidates'][0]['content']['parts'][0]['text']
            print(f"\n>> Gemini: {answer}\n")
            full_transcript += f"Operador: {user_input}\nGemini: {answer}\n\n"
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            break

    if full_transcript:
        print("💾 Guardando charla en la mente fractal...")
        # Guardado manual simplificado
        if not os.path.exists(THREADS_DIR): os.makedirs(THREADS_DIR)
        safe_date = datetime.date.today()
        filename = f"{safe_date}_Charla_Oraculo.md"
        filepath = os.path.join(THREADS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Charla con Oraculo\nFecha: {datetime.datetime.now()}\n\n## RESUMEN DE LA CHARLA\n{full_transcript}")
        
        # Sincronizamos con Git
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.system(f'git -C "{repo_dir}" add memory/*')
        os.system(f'git -C "{repo_dir}" commit -m "Pegaso: Charla del Oraculo guardada"')
        os.system(f'git -C "{repo_dir}" push origin main')
        print("✅ Sincronizado con la nube.")

if __name__ == "__main__":
    chat_oraculo()
