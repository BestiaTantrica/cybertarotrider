from fastapi import FastAPI, HTTPException
import os
import json
from .natal import natal_chart  # Reutilizamos la lógica que ya tienes

app = FastAPI(title="Mazo de Identidad Astral")

# Cargar mapeo de planetas a efectos del Heptagrama
HEPTAGRAM_EFFECTS = {
    "Sun": {"type": "SOL", "name": "Pulso", "desc": "Vitalidad y Poder Base directo."},
    "Moon": {"type": "LUNA", "name": "Espejo", "desc": "Reflejo y Reacción. Invisible boca abajo."},
    "Mercury": {"type": "MERCURIO", "name": "Vínculo", "desc": "Movilidad, Cambio y Conexión."},
    "Venus": {"type": "VENUS", "name": "Armonía", "desc": "Sinergia Elemental (Factor Candy)."},
    "Mars": {"type": "MARTE", "name": "Ruptura", "desc": "Conflicto y Sabotaje."},
    "Jupiter": {"type": "JUPITER", "name": "Expansión", "desc": "Multiplicador de Éxito."},
    "Saturn": {"type": "SATURNO", "name": "Límite", "desc": "Control, Restricción y Estructura."}
}

@app.get("/player/identity-deck")
def get_identity_deck(date: str, time: str, zone: str, lat: float, lon: float):
    """
    Genera el mazo de identidad único basado en la Carta Natal del jugador.
    """
    try:
        # 1. Obtener la carta natal usando tu lógica de Swiss Ephemeris
        chart = natal_chart(date, time, zone, lat, lon)
        positions = chart["positions"]
        
        identity_deck = []
        
        # 2. Mapear cada planeta natal a una carta especial del jugador
        for planet, info in positions.items():
            if planet in HEPTAGRAM_EFFECTS:
                effect = HEPTAGRAM_EFFECTS[planet]
                
                # Creamos la "Carta Astral" del jugador
                card = {
                    "card_id": f"NATAL_{planet.upper()}",
                    "name": f"Tu {planet} en {info['sign']}",
                    "arquetipo": planet,
                    "signo_natal": info["sign"],
                    "casa_natal": info["degree"], # Simplificación
                    "efecto_heptagrama": effect["type"],
                    "descripcion": f"{effect['name']}: {effect['desc']} Potenciada en la Casa de {info['sign']}.",
                    "power_base": 10 if planet == "Sun" else 5, # Valores base ejemplo
                    "especial": True
                }
                identity_deck.append(card)
                
        # 3. Identificar el "Avatar" (Basado en el Ascendente)
        asc = positions.get("Ascendant")
        avatar = {
            "tipo": "Ascendente",
            "signo": asc["sign"],
            "habilidad_pasiva": f"Inicia la partida con influencia de {asc['sign']}."
        }

        return {
            "player_avatar": avatar,
            "identity_deck": identity_deck,
            "total_cards": len(identity_deck)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generando mazo de identidad: {str(e)}")
