def calculate_aura_modifiers(natal_positions):
    """
    Traduce las posiciones planetarias natales en modificadores de aura pasivos.
    """
    modifiers = {
        "cost_reduction": 0,
        "draw_bonus": 0,
        "power_boosts": {}, # Por elemento
        "special_abilities": []
    }
    
    # 1. Sol: Dicta la reducción de costos base
    sol_sign = natal_positions.get("Sun", {}).get("sign")
    if sol_sign in ["Aries", "Leo", "Sagitario"]: # Fuego
        modifiers["cost_reduction"] = 1 # Abarata cartas de acción
    
    # 2. Luna: Dicta el robo de cartas
    luna_sign = natal_positions.get("Moon", {}).get("sign")
    if luna_sign in ["Géminis", "Libra", "Acuario"]: # Aire
        modifiers["draw_bonus"] = 1
        
    # 3. Marte: Potencia el daño de elementos específicos
    marte_sign = natal_positions.get("Mars", {}).get("sign")
    if marte_sign:
        # Simplificación: Marte potencia su propio elemento natal
        # Usamos un mapeo rápido de signos a elementos
        sign_to_elem = {
            "Aries": "Fuego", "Leo": "Fuego", "Sagitario": "Fuego",
            "Tauro": "Tierra", "Virgo": "Tierra", "Capricornio": "Tierra",
            "Géminis": "Aire", "Libra": "Aire", "Acuario": "Aire",
            "Cáncer": "Agua", "Escorpio": "Agua", "Piscis": "Agua"
        }
        elem = sign_to_elem.get(marte_sign)
        modifiers["power_boosts"][elem] = modifiers.get("power_boosts", {}).get(elem, 0) + 2
        
    return modifiers

# Ejemplo de estructura de salida
# {
#   "cost_reduction": 1,
#   "draw_bonus": 0,
#   "power_boosts": {"Fuego": 2},
#   "special_abilities": ["Aura de Marte: +2 PB a cartas de Fuego"]
# }
