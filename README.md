# BESTIA TÁNTRICA | CYBER TAROT & ASTROLOGÍA

## Consolidación del Proyecto

Este repositorio es la unificación de los múltiples repositorios de @BestiaTantrica relacionados con el juego de Tarot y Astrología.

### Estructura de Proyecto

- **/core**: Reglas, matrices de datos y lógica fundamental del juego.
- **/backend**:
  - `astro-oraculo`: API FastAPI con integración de Swiss Ephemeris.
  - `astrotarot-ai`: Soporte de I.A. para lecturas.
- **/frontend**: Interfaz de usuario (en desarrollo).

### Estado de la Misión

- [x] Unificación de repositorios dispersos.
- [x] Limpieza y organización de archivos JSON de reglas.
- [x] Consolidación de APIs de backend.
- [ ] Desarrollo de frontend premium.
- [ ] Integración de sistema de puntaje y tránsitos en tiempo real.

### Cómo ejecutar (Backend)

1. Instalar dependencias: `pip install -r backend/astro-oraculo/requirements.txt`
2. Iniciar API: `uvicorn backend.astro-oraculo.app.main:app --reload`
