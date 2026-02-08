
import os
import json
import datetime
import re

MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory")
THREADS_DIR = os.path.join(MEMORY_DIR, "threads")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")
MANIFEST_PATH = os.path.join(MEMORY_DIR, "MANIFEST.md")
PROMPT_LLAVE_PATH = os.path.join(MEMORY_DIR, "PROMPT_LLAVE.md")

class PegasoMemory:
    def __init__(self):
        for d in [THREADS_DIR, ARCHIVE_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def distill(self, raw_text_path):
        """Lee una charla cruda y extrae puntos clave."""
        if not os.path.exists(raw_text_path):
            print(f"❌ No se encuentra el archivo: {raw_text_path}")
            return

        with open(raw_text_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Lógica simple de extracción de puntos clave (Heuristicas)
        # Podríamos usar una IA para esto, pero buscamos algo local y rápido.
        lines = content.split('\n')
        title = lines[0][:50] if lines else "Conversacion_Sin_Titulo"
        
        # Guardamos el hilo
        self.log_thread(title, content, tags=["distilled"])

    def log_thread(self, title, content, tags=[]):
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
        filename = f"{datetime.date.today()}_{safe_title}.md"
        filepath = os.path.join(THREADS_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n")
            f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tags: {', '.join(tags)}\n\n")
            f.write("## RESUMEN DE LA CHARLA\n")
            f.write(content[:1000] + "\n... [Resto del hilo guardado en archivo] ...")
        
        print(f"Hilo destilado y guardado: {filename}")
        self.update_all()

    def update_all(self):
        self.update_manifest()
        self.build_master_prompt()

    def update_manifest(self):
        content = "# 🦅 MANIFIESTO DE MEMORIA PEGASO\n\n"
        content += f"Ultima actualizacion: {datetime.datetime.now()}\n\n"
        content += "## HISTORIAL RECIENTE\n"
        
        threads = sorted(os.listdir(THREADS_DIR), reverse=True)[:10]
        for t in threads:
            content += f"- {t}\n"

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            f.write(content)

    def build_master_prompt(self):
        """Genera el PROMPT_LLAVE.md basado en el estado actual."""
        status_path = os.path.join(MEMORY_DIR, "STATUS.md")
        status_content = ""
        if os.path.exists(status_path):
            with open(status_path, "r", encoding="utf-8") as f:
                status_content = f.read()

        prompt = f"""# PROTOCOLO PEGASO: LLAVE DE ACTIVACION DE MEMORIA

**FECHA DE GENERACION:** {datetime.date.today()}
**ESTADO:** OPERACIONAL

{status_content}

---
## ULTIMOS HILOS DE CONOCIMIENTO
"""
        threads = sorted(os.listdir(THREADS_DIR), reverse=True)[:3]
        for t in threads:
            with open(os.path.join(THREADS_DIR, t), "r", encoding="utf-8") as f:
                content = f.read()
                # Extraemos solo el resumen del hilo
                resumen = re.search(r"## RESUMEN DE LA CHARLA\n(.*?)(?:\n---|\n...|$)", content, re.DOTALL)
                if resumen:
                    prompt += f"### {t}\n{resumen.group(1).strip()}\n\n"

        prompt += "\n--- \n**INSTRUCCION:** Continua desde este punto. No repitas lo ya listado arriba."

        with open(PROMPT_LLAVE_PATH, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"PROMPT_LLAVE.md actualizado. Listo para copiar.")
        self.sync_git()

    def sync_git(self):
        """Sincronizacion total: Add, Commit y Push."""
        try:
            print("Sincronizando con la nube (Git Push)...")
            repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Usar comillas dobles para rutas con espacios y asegurar compatibilidad
            os.system(f'git -C "{repo_dir}" add memory/*')
            os.system(f'git -C "{repo_dir}" commit -m "Pegaso: Actualizacion de Memoria (Mobile/PC)"')
            os.system(f'git -C "{repo_dir}" push origin main') 
            print(">>> Memoria SINCRONIZADA con la nube.")
        except Exception as e:
            print(f"Error en Git: {e}")

    def prune(self, keep_latest=10):
        """Mueve hilos viejos a archive/ para mantener ligero el contexto."""
        all_threads = sorted(os.listdir(THREADS_DIR), reverse=True)
        to_prune = all_threads[keep_latest:]
        
        for t in to_prune:
            src = os.path.join(THREADS_DIR, t)
            dst = os.path.join(ARCHIVE_DIR, t)
            os.rename(src, dst)
            print(f"Archive: {t}")

if __name__ == "__main__":
    import sys
    pegaso = PegasoMemory()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "distill" and len(sys.argv) > 2:
            pegaso.distill(sys.argv[2])
        elif cmd == "update":
            pegaso.update_all()
        elif cmd == "prune":
            pegaso.prune()
    else:
        print("Pegaso Memory Core")
        print("Usage:")
        print("  python pegaso_memory.py distill <path_to_transcript.txt>")
        print("  python pegaso_memory.py update")
        print("  python pegaso_memory.py prune")
