class EmotionEngine:
    """
    Traduce datos astrológicos puros (ángulos, elementos) a
    firmas emocionales y visuales abstractas.
    """
    
    ELEMENT_COLORS = {
        "Fire": {"primary": "Crimson", "secondary": "Gold", "texture": "Plasma"},
        "Earth": {"primary": "Ochre", "secondary": "Moss Green", "texture": "Stone/Roots"},
        "Air": {"primary": "Electric Blue", "secondary": "White", "texture": "Vapor/Glass"},
        "Water": {"primary": "Indigo", "secondary": "Teal", "texture": "Liquid/Abyss"}
    }
    
    TENSION_TEXTURES = {
        "Opposition": "Fractured line, high contrast split, duality",
        "Square": "Sharp jagged edges, friction sparks, heavy weight",
        "Conjunction": "Intense fusion, singularity point, blinding core",
        "Trine": "Fluid flow, harmonic waves, seamless gradient"
    }

    @staticmethod
    def analyze_aspects(natal_data):
        """
        Detecta tensiones y armonías ocultas.
        Retorna una lista de 'Cicatrices' y 'Regalos'.
        """
        features = []
        
        # Ejemplo: Sol vs Saturno (Típico en la carta de Tomás: Oposición/Tensión)
        # Aquí iría la lógica matemática real comparando grados.
        # Simulamos detección para el prototipo:
        
        # Si Sol (Aries) y Saturno (Libra) están opuestos:
        features.append({
            "type": "Opposition",
            "meaning": "Identity under pressure",
            "visual_effect": "A burning core trying to break through a crystalline cage"
        })
        
        # Si Luna (Sagitario) conjunción Urano:
        features.append({
            "type": "Conjunction",
            "meaning": "Emotional Lightning",
            "visual_effect": "Sudden electric strikes in a dark void"
        })
        
        return features

    @staticmethod
    def get_core_palette(sun_sign, asc_sign):
        # Mapeo simplificado para prototipo
        # En la versión final usaremos la tabla de elementos real
        return {
            "base": "Deep Void", # El lienzo infinito
            "accent": "Red (Aries) and Electric Blue (Aquarius)",
            "style": "Abstract Expressionism meets Glitch Art"
        }
