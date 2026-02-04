export const ARCANOS = [
    {
        "id": 0,
        "name": "EL LOCO",
        "element": "Aire",
        "heptagram": "MERCURIO",
        "effect": "SALTO: Al final del turno, se mueve a una casa adyacente al azar.",
        "shadow_bonus": "+1 Robo de carta si la casa es de Aire."
    },
    {
        "id": 1,
        "name": "EL MAGO",
        "element": "Aire",
        "heptagram": "MERCURIO",
        "effect": "VÍNCULO: Duplica el poder de la próxima carta jugada en esta casa.",
        "shadow_bonus": "-1 Costo de energía para el próximo Arcano Menor."
    },
    {
        "id": 2,
        "name": "LA SACERDOTISA",
        "element": "Agua",
        "heptagram": "LUNA",
        "effect": "REFLEJO: Boca abajo hasta el final. Copia el PB de la carta rival más fuerte.",
        "shadow_bonus": "Permite ver 1 carta oculta del mazo rival."
    },
    {
        "id": 3,
        "name": "LA EMPERATRIZ",
        "element": "Tierra",
        "heptagram": "VENUS",
        "effect": "ARMONÍA: Otorga +2 PB a todas las cartas de esta casa cada turno.",
        "shadow_bonus": "Genera +1 de Prana extra al inicio del turno."
    },
    {
        "id": 4,
        "name": "EL EMPERADOR",
        "element": "Fuego",
        "heptagram": "MARTE",
        "effect": "LEY: Bloquea los efectos de las cartas rivales en esta casa.",
        "shadow_bonus": "Tus cartas de Fuego no pueden ser reducidas en PB."
    },
    {
        "id": 5,
        "name": "EL SUMO SACERDOTE",
        "element": "Tierra",
        "heptagram": "JUPITER",
        "effect": "TRADICIÓN: +1 PB por cada carta del mismo elemento en la mesa.",
        "shadow_bonus": "Inmune a efectos de cartas de Aire."
    },
    {
        "id": 6,
        "name": "LOS ENAMORADOS",
        "element": "Aire",
        "heptagram": "VENUS",
        "effect": "DUALIDAD: Elige entre +3 PB o curar 3 puntos de vida.",
        "shadow_bonus": "Si se juega junto a otra carta, ambas ganan +1 PB."
    },
    {
        "id": 7,
        "name": "EL CARRO",
        "element": "Agua",
        "heptagram": "LUNA",
        "effect": "AVANCE: Se puede mover a una casa adyacente una vez por partida.",
        "shadow_bonus": "+2 PB si es la única carta en la casa."
    },
    {
        "id": 10,
        "name": "LA RUEDA DE LA FORTUNA",
        "element": "Fuego",
        "heptagram": "JUPITER",
        "effect": "EXPANSIÓN: Al azar, multiplica x2 o divide /2 el puntaje de la casa.",
        "shadow_bonus": "Aumenta la probabilidad de Sincronicidad en un 20%."
    },
    {
        "id": 13,
        "name": "LA MUERTE",
        "element": "Agua",
        "heptagram": "SATURNO",
        "effect": "RUPTURA: Destruye todas las cartas de PB inferior a 5 en esta casa.",
        "shadow_bonus": "Siguiente carta jugada activa su efecto dos veces."
    },
    {
        "id": 16,
        "name": "LA TORRE",
        "element": "Fuego",
        "heptagram": "MARTE",
        "effect": "COLAPSO: Destruye la casa. Ambos jugadores vuelven a 0 en este sector.",
        "shadow_bonus": "Si eres atacado, el atacante pierde 2 de Energía."
    }
];

export const MATRIX = {
    "elementos": {
        "Fuego": { "valor": 8, "descripcion": "Impulso creativo y acción directa", "color": "#FF4500" },
        "Tierra": { "valor": 6, "descripcion": "Estabilidad y recursos materiales", "color": "#8B4513" },
        "Aire": { "valor": 7, "descripcion": "Estrategia y comunicación", "color": "#87CEEB" },
        "Agua": { "valor": 5, "descripcion": "Intuición y conexión emocional", "color": "#1E90FF" }
    },
    "casas_astrologicas": {
        "activacion": ["mes_actual-1", "mes_actual", "mes_actual+1"],
        "capacidad_maxima": 6
    }
};
