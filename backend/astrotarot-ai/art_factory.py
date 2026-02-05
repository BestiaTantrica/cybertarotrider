import time
import requests
import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# ==================================================================================
# ART FACTORY: MOTOR MULTI-PROVEEDOR ROBUSTO CON SUPABASE
# ==================================================================================
# Estrategia de Redundancia:
# 1. Pollinations AI (Flux) -> Calidad Máxima, Gratis.
# 2. Hugging Face API (Flux.1-dev) -> Requiere Token, Alta Estabilidad.
# 3. Fallback Local (SVG) -> Último recurso.
# 
# PERSISTENCIA: Los activos se suben a Supabase Storage para evitar llenar el disco.
# ==================================================================================

class ArtProvider:
    def generate(self, prompt, seed, width, height) -> bytes:
        raise NotImplementedError("Método generate debe ser implementado.")

class PollinationsProvider(ArtProvider):
    MAX_RETRIES = 2
    
    def generate(self, prompt, seed, width, height) -> bytes:
        # Limpieza de prompt
        clean_prompt = prompt.replace(" ", "%20")
        # Url base (incluye modelo Flux y no-logo)
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={width}&height={height}&seed={seed}&model=flux&nologo=true"
        
        print(f"   [Pollinations] Requesting: {url[:60]}...")
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    return response.content
                elif response.status_code == 502:
                    print(f"   [Pollinations] 502 Bad Gateway (Attempt {attempt+1})")
                    time.sleep(1) # Espera breve antes de reintentar
                else:
                    print(f"   [Pollinations] Error {response.status_code}")
            except Exception as e:
                print(f"   [Pollinations] Connection Error: {e}")
        
        raise Exception("Pollinations failed after retries.")

class HuggingFaceProvider(ArtProvider):
    def generate(self, prompt, seed, width, height) -> bytes:
        # Requiere token en variable de entorno
        token = os.getenv("HF_TOKEN")
        if not token:
            raise Exception("HF_TOKEN not found in environment.")
            
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Hugging Face a veces requiere payload con seed
        payload = {
            "inputs": prompt,
            "parameters": {"seed": seed, "width": width, "height": height}
        }
        
        try:
            print(f"   [HuggingFace] Requesting via API...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"HF Error {response.status_code}: {response.text}")
        except Exception as e:
            raise Exception(f"HuggingFace Connection Error: {e}")

class LocalFallbackProvider(ArtProvider):
    def generate(self, prompt, seed, width, height) -> bytes:
        print("   [Fallback] Generando SVG de emergencia...")
        # Genera un SVG abstracto simple basado en el seed (color)
        random.seed(seed)
        color1 = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        color2 = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        
        svg = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad)" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="white" font-size="40">
                SYSTEM OFFLINE
            </text>
        </svg>
        """
        return svg.encode('utf-8')

class ArtFactory:
    """
    Gestor principal que orquesta los proveedores y la persistencia en Supabase.
    """
    
    def __init__(self):
        self.providers = [
            PollinationsProvider(),
            LocalFallbackProvider()
        ]
        # Inicializar Supabase (usamos .env o vars de entorno)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            self.supabase: Client = create_client(url, key)
            self.bucket = "assets-juego" # Asegúrate de que este bucket exista en Supabase
        else:
            self.supabase = None
            print("[WARN] Supabase no configurado. Se usara almacenamiento local (TEMPORAL).")
        
    def generate_asset(self, prompt, seed, filename, width=1024, height=1024):
        """
        Intenta generar el activo e intenta subirlo a Supabase.
        Devuelve la URL (Supabase o Local).
        """
        for provider in self.providers:
            provider_name = provider.__class__.__name__
            try:
                print(f"[INFO] Intentando con {provider_name}...")
                image_data = provider.generate(prompt, seed, width, height)
                
                # 1. Intentar subir a Supabase Storage
                if self.supabase:
                    try:
                        storage_path = f"pasaportes/{filename}"
                        # El content-type es importante para que el navegador lo vea como imagen
                        self.supabase.storage.from_(self.bucket).upload(
                            path=storage_path,
                            file=image_data,
                            file_options={"content-type": "image/png", "upsert": "true"}
                        )
                        public_url = self.supabase.storage.from_(self.bucket).get_public_url(storage_path)
                        print(f"[OK] Subido a Supabase: {public_url}")
                        return public_url
                    except Exception as upload_err:
                        print(f"[WARN] Fallo subida a Supabase: {upload_err}")
                        # Si falla Supabase, caemos a local por seguridad para no perder la imagen
                
                # 2. Fallback Local (si no hay Supabase o falló la subida)
                local_path = os.path.join("static/assets", filename)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(image_data)
                
                print(f"[OK] Guardado localmente: {local_path}")
                return f"/static/assets/{filename}"
                
            except Exception as e:
                print(f"[WARN] Fallo {provider_name}: {e}")
                continue 
                
        print("[ERROR] CRITICAL: Todos los proveedores fallaron.")
        return None

# --- PROMPTS MAESTROS ---
def get_prompts_for_user(natal_data):
    # Aquí iría la lógica dinámica de emotion_engine
    return {
        "back": "Abstract cosmic void, burnt edges, deep crimson, 8k cinematic",
        "mid": "Floating crystalline shards, broken glass, on black background",
        "front": "Electric plasma arcs, pure light energy, on black background"
    }

if __name__ == "__main__":
    # Test rápido
    factory = ArtFactory()
    seed = 42240412
    prompts = get_prompts_for_user({})
    
    # Crear carpeta de output si no existe
    os.makedirs("output_assets", exist_ok=True)
    
    factory.generate_asset(prompts["back"], seed+1, "output_assets/test_back.png")
