import requests
import time

def test_generation():
    url = "http://localhost:5000/generar-pasaporte"
    print(f"[TEST] Enviando peticion a {url}...")
    
    try:
        start_time = time.time()
        response = requests.post(url, json={"test": True})
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Exito ({duration:.2f}s)")
            print("--- Respuesta del Servidor ---")
            print(f"Status: {data.get('status')}")
            print("Capas Generadas:")
            for layer, link in data.get('layers', {}).items():
                print(f"  - {layer}: {link}")
        else:
            print(f"[ERROR] Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Error de conexion: {e}")
        print("Asegurate de que server.py este corriendo en otra terminal.")

if __name__ == "__main__":
    # Esperamos un poco para dar tiempo al servidor de arrancar
    time.sleep(2)
    test_generation()
