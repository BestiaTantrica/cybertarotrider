from datetime import datetime
import random

class GameContext:
    def __init__(self, player_passport):
        self.passport = player_passport
        self.turn_count = 0
        self.field_temperature = 0 # 0 = Neutral, >0 = Hot (Aries), <0 = Cold (Saturn)
        
    def advance_turn(self):
        self.turn_count += 1
        # Lógica climática: Si tienes pasaporte Aries, el tablero se calienta solo
        if "Aries" in self.passport.get("sun_sign", ""):
            self.field_temperature += 1

class Card:
    def __init__(self, name, element, base_cost):
        self.name = name
        self.element = element
        self.base_cost = base_cost
        self.is_frozen = False
        self.experience_points = 0 # Las cartas pueden aprender

    def __repr__(self):
        status = "❄️" if self.is_frozen else "🔥" if self.experience_points > 0 else ""
        return f"[{self.name} {status} (Cost: {self.base_cost})]"

class GameMechanics:
    """
    Define y aplica las reglas de empátía y transmutación
    basadas en el Pasaporte Cósmico.
    """

    @staticmethod
    def apply_saturn_crystallization(hand, turn_count):
        """
        Reto de Saturno: Cristalización empática.
        No es un castigo, es una pausa forzada para madurar.
        """
        if turn_count % 3 == 0: # Ciclo de Saturno
            # Busca una carta para cristalizar
            target_card = random.choice([c for c in hand if not c.is_frozen])
            target_card.is_frozen = True
            return f"🌌 Saturno ha cristalizado '{target_card.name}'. Requiere calor para revelar su lección."
        return None

    @staticmethod
    def transmute_crystal(card, energy_invested):
        """
        Acción del Jugador: Derretir el cristal.
        Invierte energía para ganar experiencia (XP).
        """
        if not card.is_frozen:
            return "La carta no está cristalizada."
        
        if energy_invested >= 1:
            card.is_frozen = False
            card.experience_points += 10 # PREMIO por superar el obstáculo
            return f"🔥 ¡Transmutación exitosa! '{card.name}' se ha liberado y ganado 10 XP. Ahora es más sabia."
        else:
            return "Falta energía para derretir la estructura de Saturno."

    @staticmethod
    def apply_aries_impulse(card, field_temp):
        """
        Impulso de Aries: El calor del entorno acelera las cartas.
        """
        if field_temp > 5:
            # Si el campo está "Caliente" (Aries activado)
            # Las cartas son más baratas pero inestables
            effective_cost = max(0, card.base_cost - 1)
            return effective_cost, "⚡ Impulso de Aries activo (-1 Costo)"
        return card.base_cost, None

# --- SIMULACIÓN PARA TEST ---
if __name__ == "__main__":
    passport = {"sun_sign": "Aries", "aspects": ["Saturn_Opposition"]}
    ctx = GameContext(passport)
    
    # Mazo de prueba
    hand = [Card("Golpe de Fuego", "Fire", 3), Card("Escudo de Agua", "Water", 2), Card("La Torre", "Earth", 5)]
    
    print(f"--- INICIO: Mano del Jugador ---\n{hand}\n")
    
    # Turno 3: Saturno se activa
    ctx.turn_count = 3
    print(GameMechanics.apply_saturn_crystallization(hand, ctx.turn_count))
    print(f"--- Mano tras Saturno ---\n{hand}\n")
    
    # Jugador decide transmutar
    target = next(c for c in hand if c.is_frozen)
    print(f"🧙 Jugador invierte energía en '{target.name}'...")
    print(GameMechanics.transmute_crystal(target, energy_invested=2))
    print(f"--- Mano tras Transmutación (Evolución) ---\n{hand}")
