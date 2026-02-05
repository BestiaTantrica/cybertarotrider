/* ================= DATOS CORE (V4 - CAOS & COSMOS) ================= */
const ARCANOS_MAYORES = [
    { id: 0, name: "EL LOCO", element: "Aire", power: 7, cost: 3, effect: "SALTO", desc: "Se mueve cada turno buscando aire.", icon: "🌪️" },
    { id: 1, name: "EL MAGO", element: "Aire", power: 8, cost: 4, effect: "VINCULO", desc: "Duplica el poder de la próxima carta.", icon: "✨" },
    { id: 2, name: "LA SACERDOTISA", element: "Agua", power: 5, cost: 4, effect: "REFLEJO", desc: "Copia el PB del oponente.", icon: "🌙" },
    { id: 3, name: "LA EMPERATRIZ", element: "Tierra", power: 8, cost: 5, effect: "ARMONIA", desc: "Nutre la casa con PB pasivo.", icon: "🌿" },
    { id: 4, name: "EL EMPERADOR", element: "Fuego", power: 9, cost: 6, effect: "LEY", desc: "Autoridad que ignora caos rival.", icon: "🔥" },
    { id: 10, name: "LA RUEDA", element: "Fuego", power: 7, cost: 5, effect: "AZAR", desc: "Giro del destino cuántico.", icon: "🎡" },
    { id: 13, name: "LA MUERTE", element: "Agua", power: 10, cost: 8, effect: "RUPTURA", desc: "Cosecha la debilidad.", icon: "💀" },
    { id: 16, name: "LA TORRE", element: "Fuego", power: 12, cost: 9, effect: "COLAPSO", desc: "Impacto físico total.", icon: "⚡" }
];

const ARCANOS_MENORES = [
    // Bastos (Fuego)
    { id: 101, name: "AS DE BASTOS", element: "Fuego", power: 4, cost: 1, effect: "IMPULSO", desc: "+1 Energía el próximo turno.", icon: "🪄" },
    { id: 102, name: "TRES DE BASTOS", element: "Fuego", power: 5, cost: 2, effect: "VISION", desc: "Revela una carta del rival.", icon: "🔭" },
    // Copas (Agua)
    { id: 201, name: "AS DE COPAS", element: "Agua", power: 3, cost: 1, effect: "FLUIR", desc: "Sana 2 de puntuación global.", icon: "🍷" },
    { id: 205, name: "CINCO DE COPAS", element: "Agua", power: 4, cost: 2, effect: "DUELO", desc: "-2 PB a carta rival.", icon: "🥀" },
    // Espadas (Aire)
    { id: 301, name: "AS DE ESPADAS", element: "Aire", power: 5, cost: 1, effect: "CORTE", desc: "Ignora protecciones simples.", icon: "⚔️" },
    { id: 308, name: "OCHO DE ESPADAS", element: "Aire", power: 4, cost: 3, effect: "PRISION", desc: "Carta rival no puede moverse.", icon: "🕸️" },
    // Oros (Tierra)
    { id: 401, name: "AS DE OROS", element: "Tierra", power: 4, cost: 1, effect: "SOLIDEZ", desc: "+2 PB a esta carta si hay tierra.", icon: "🪙" },
    { id: 410, name: "DIEZ DE OROS", element: "Tierra", power: 6, cost: 3, effect: "LEGADO", desc: "Poder se mantiene tras morir.", icon: "🏰" }
];

const ARCANOS = [...ARCANOS_MAYORES, ...ARCANOS_MENORES];

const SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"];
const MATRIX = {
    "Fuego": { color: "#ff4d4d", weak: "Agua", name: "Fuego" },
    "Tierra": { color: "#8b5a2b", weak: "Aire", name: "Tierra" },
    "Aire": { color: "#a4d6ff", weak: "Tierra", name: "Aire" },
    "Agua": { color: "#1e90ff", weak: "Fuego", name: "Agua" }
};

const PLANETS = [
    { name: "Sol", glyph: "☉", color: "#ffd700", speed: 1, element: "Fuego" },
    { name: "Luna", glyph: "☽", color: "#e0e0e0", speed: 13.3, element: "Agua" },
    { name: "Mercurio", glyph: "☿", color: "#c0c0ff", speed: 4.1, element: "Aire" },
    { name: "Venus", glyph: "♀", color: "#ffb3d9", speed: 1.6, element: "Tierra" },
    { name: "Marte", glyph: "♂", color: "#ff3333", speed: 0.5, element: "Fuego" },
    { name: "Júpiter", glyph: "♃", color: "#ff9933", speed: 0.08, element: "Fuego" },
    { name: "Saturno", glyph: "♄", color: "#996633", speed: 0.03, element: "Tierra" }
];

/* ================= MOTOR DE ESTADO ================= */
let state = {
    turn: 'PLAYER',
    gameActive: true,
    round: 1,
    maxRounds: 6,
    energy: 10,
    maxEnergy: 10,
    playerScore: 0,
    enemyScore: 0,
    hand: [],
    playerDeck: [],
    enemyDeck: [],
    houses: Array(12).fill(null).map(() => []),
    planetPositions: [],
    currentAspects: [],
    currentRules: [], // Reglas de los Tránsitos
    nextCardMultiplier: 1,
    selectedCardIdx: null,
    selectedHouseIdx: null
};

/* ================= PASAPORTE VIVO (FÁBRICA DE ARTE) ================= */
async function loadPassport() {
    console.log("🌌 Conectando con El Telar de las Almas...");
    try {
        const response = await fetch('http://localhost:5000/generar-pasaporte', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: "tomy_alpha" })
        });

        const data = await response.json();

        if (data.status === 'success') {
            const layers = data.layers;
            // Aplicar imágenes a las capas del centro del Mándala
            // Las URLs vienen como /static/assets/... que Flask sabe servir
            const apiBase = "http://localhost:5000";
            document.getElementById('l-back').style.backgroundImage = `url('${apiBase}${layers.back}')`;
            document.getElementById('l-mid').style.backgroundImage = `url('${apiBase}${layers.mid}')`;
            document.getElementById('l-front').style.backgroundImage = `url('${apiBase}${layers.front}')`;

            log("Conexión Estelar: Pasaporte Cósmico Sincronizado.", "SYS");
        }
    } catch (e) {
        console.warn("⚠️ Fábrica de Arte Offline. Usando modo de ahorro energético.");
        log("Tensión en el Éter: Los activos visuales no pudieron cargarse.", "SYS");
    }
}


/* ================= INIT ================= */
async function init() {
    calculateEphemeris();
    state.currentAspects = calculateAspects();
    state.currentRules = generateRulesFromAspects();

    // Cargar Pasaporte Cósmico (Arte Vivo) desde el Backend
    await loadPassport();

    // Crear Mazos Únicos
    state.playerDeck = generateCustomDeck();
    state.enemyDeck = generateCustomDeck();

    // Reparto inicial
    for (let i = 0; i < 5; i++) {
        state.hand.push(state.playerDeck.pop());
    }

    renderMandala();
    renderPlanets();
    renderHandUI();
    drawAspects();
    updateHeader();
    updateEnergyUI();

    generateOracleReport();

    // Mouse Trail
    document.addEventListener('mousemove', (e) => {
        if (Math.random() > 0.8) createMouseParticle(e.clientX, e.clientY);
    });
}

function generateCustomDeck() {
    let deck = [];
    // 15 Menores al azar (sin repetir por ahora en el pool expandido)
    let menores = [...ARCANOS_MENORES].sort(() => 0.5 - Math.random()).slice(0, 15);
    // 5 Mayores al azar
    let mayores = [...ARCANOS_MAYORES].sort(() => 0.5 - Math.random()).slice(0, 5);
    deck = [...menores, ...mayores];
    return shuffle(deck);
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function generateRulesFromAspects() {
    let rules = [];
    state.currentAspects.forEach(asp => {
        if (asp.type === 'square') {
            rules.push({
                msg: `TENSIÓN: Las cartas de ${asp.p1.desc} y ${asp.p2.desc} cuestan +1.`,
                target: [asp.p1.desc, asp.p2.desc],
                effect: 'cost_up'
            });
        }
        if (asp.type === 'trine') {
            rules.push({
                msg: `ARMONÍA: Cartas de ${asp.p1.desc} ganan +2 PB.`,
                target: [asp.p1.desc],
                effect: 'power_up'
            });
        }
    });
    return rules;
}

function generateOracleReport() {
    log("--- REPORTE DEL ORÁCULO ---", "SYS");
    const sun = state.planetPositions.find(p => p.name === "Sol");
    log(`El Sol ilumina ${SIGNS[sun.signIdx]}. El elemento ${sun.desc} rige este ciclo.`, "SYS");

    state.currentAspects.forEach(asp => {
        if (asp.type === 'trine') {
            log(`Armonía Estelar: Un Trino entre ${asp.p1.name} y ${asp.p2.name} potencia el flujo energético.`, "PLAYER");
        } else {
            log(`Tensión Cósmica: ${asp.p1.name} en cuadratura con ${asp.p2.name}. El Éter es denso.`, "ENEMY");
        }
    });
}

function calculateEphemeris() {
    const now = new Date();
    const epoch = new Date(2000, 0, 1);
    const days = (now - epoch) / (1000 * 60 * 60 * 24);

    state.planetPositions = PLANETS.map(p => {
        let baseAngle = 0;
        if (p.name === 'Sol') baseAngle = 280;
        let dailySpeed = 0.9856;
        if (p.name === 'Luna') dailySpeed = 13.17;
        if (p.name === 'Mercurio') dailySpeed = 4.09;
        if (p.name === 'Venus') dailySpeed = 1.6;
        if (p.name === 'Marte') dailySpeed = 0.52;
        if (p.name === 'Júpiter') dailySpeed = 0.083;
        if (p.name === 'Saturno') dailySpeed = 0.033;

        const totalDeg = (baseAngle + days * dailySpeed) % 360;
        const angle = totalDeg < 0 ? totalDeg + 360 : totalDeg;
        const signIdx = Math.floor(angle / 30);
        return { name: p.name, glyph: p.glyph, color: p.color, angle: angle, signIdx: signIdx, desc: p.element };
    });
}

function calculateAspects() {
    let aspects = [];
    const bodies = state.planetPositions;
    for (let i = 0; i < bodies.length; i++) {
        for (let j = i + 1; j < bodies.length; j++) {
            let diff = Math.abs(bodies[i].angle - bodies[j].angle);
            if (diff > 180) diff = 360 - diff;

            if (Math.abs(diff - 120) < 6) aspects.push({ p1: bodies[i], p2: bodies[j], type: 'trine', color: '#00ffaa' });
            if (Math.abs(diff - 90) < 6) aspects.push({ p1: bodies[i], p2: bodies[j], type: 'square', color: '#ff4444' });
        }
    }
    return aspects;
}

/* ================= LÓGICA DE JUEGO ================= */

function selectCard(idx) {
    if (!state.gameActive || state.turn !== 'PLAYER') return;
    state.selectedCardIdx = (state.selectedCardIdx === idx) ? null : idx;
    renderHandUI();
    highlightSynergies();
}

function selectHouse(idx) {
    if (!state.gameActive || state.turn !== 'PLAYER' || state.selectedCardIdx === null) return;

    const card = state.hand[state.selectedCardIdx];
    const realCost = calculateRealCost(card);

    if (state.energy < realCost) {
        log(`BLOQUEO: Escasez de Éter. Requiere ${realCost}`, "SYS");
        shakeScreen(10);
        return;
    }

    playCard(state.selectedCardIdx, idx, 'PLAYER');
}

function calculateRealCost(card) {
    let cost = card.cost;
    // Tensión por Cuadraturas aumenta costo de elementos involucrados
    state.currentAspects.filter(a => a.type === 'square').forEach(asp => {
        if (asp.p1.desc === card.element || asp.p2.desc === card.element) {
            cost += 1;
        }
    });
    return cost;
}

function playCard(cardIdx, houseIdx, owner) {
    const card = owner === 'PLAYER' ? state.hand[cardIdx] : ARCANOS[Math.floor(Math.random() * ARCANOS.length)];
    const cost = owner === 'PLAYER' ? calculateRealCost(card) : 0;

    // 1. GASTO
    if (owner === 'PLAYER') {
        state.energy -= cost;
        // Robar carta si queda mazo
        if (state.playerDeck.length > 0) {
            state.hand[cardIdx] = state.playerDeck.pop();
        } else {
            state.hand.splice(cardIdx, 1); // Quitar carta de la mano si no hay mazo
        }
        updateEnergyUI();
    }

    // 2. EFECTOS ESPECIALES
    let finalPower = card.power;

    // El Mago
    if (owner === 'PLAYER' && state.nextCardMultiplier > 1) {
        finalPower *= state.nextCardMultiplier;
        state.nextCardMultiplier = 1;
        log(`¡CANALIZACIÓN! ${card.name} resuena con poder duplicado.`, "PLAYER");
    }
    if (card.effect === "VINCULO") state.nextCardMultiplier = 2;

    // Sacerdotisa
    if (card.effect === "REFLEJO") {
        const enemyCards = state.houses[houseIdx].filter(c => c.owner !== owner);
        if (enemyCards.length > 0) {
            finalPower = Math.max(...enemyCards.map(c => c.power));
            log(`${card.name} se convierte en un espejo de ${finalPower} PB.`, owner);
        }
    }

    // LA TORRE (Motor de Caos)
    if (card.effect === "COLAPSO") {
        log(`¡LA TORRE CAE! El impacto desplaza las energías de ${SIGNS[houseIdx]}.`, "SYS");
        shakeScreen(30);
        triggerVisualEffect(houseIdx, 'explosion', '#ff0000');

        const cardsToDisplace = state.houses[houseIdx];
        state.houses[houseIdx] = []; // Limpiar casa original

        cardsToDisplace.forEach(c => {
            if (c.power > 5) {
                const side = Math.random() > 0.5 ? 1 : -1;
                const newHouse = (houseIdx + side + 12) % 12;
                log(`Mecánica de Empuje: ${c.name} desplazado a ${SIGNS[newHouse]}.`, "SYS");
                state.houses[newHouse].push(c);
            } else {
                log(`Colapso: ${c.name} no resiste el impacto y cae del paño.`, "ENEMY");
                // Visualmente se pierden
            }
        });
    }

    // 3. REGISTRO
    if (card.effect !== "COLAPSO") { // Si no es Torre (que ya limpió y desplazó)
        state.houses[houseIdx].push({
            ...card,
            power: finalPower,
            owner: owner,
            originalId: card.id
        });
    }

    // 4. RECALCULAR
    recalculateGlobalScore();
    renderBoard();

    // 5. TURNO
    state.selectedCardIdx = null;
    renderHandUI();

    if (state.turn === 'PLAYER' && owner === 'PLAYER') {
        state.turn = 'ENEMY';
        setStatus("SISTEMA PENSANDO...", "#ff0055");
        setTimeout(enemyAI, 1500);
    } else {
        processEndTurnEffects();
    }
}

function processEndTurnEffects() {
    for (let i = 0; i < 12; i++) {
        state.houses[i].forEach((card, idx) => {
            // El Loco
            if (card.effect === "SALTO") {
                const target = (i + (Math.random() > 0.5 ? 1 : -1) + 12) % 12;
                log(`Inestabilidad: El Loco huye del orden hacia ${SIGNS[target]}.`, card.owner);
                state.houses[target].push(state.houses[i].splice(idx, 1)[0]);
            }
            // Armonía persistente
            if (card.effect === "ARMONIA") {
                card.power += 1;
                createFloatingText(i, "+1 PB", "#00ff00");
            }
        });
    }
    recalculateGlobalScore();
    renderBoard();

    if (state.turn === 'ENEMY') advanceRound();
}

function recalculateGlobalScore() {
    let pTotal = 0; let eTotal = 0;

    for (let i = 0; i < 12; i++) {
        state.houses[i].forEach(c => {
            let pwr = c.power;

            // Sinergia Signo
            if (getElementOfSign(i) === c.element) pwr += 2;

            // Sinergia Tránsitos
            state.planetPositions.filter(p => p.signIdx === i).forEach(plan => {
                if (plan.name === 'Sol') pwr *= 1.5;
                if (plan.name === 'Júpiter') pwr += 3;
                if (plan.name === 'Saturno') pwr -= 3;
                if (plan.desc === c.element) pwr += 2;
            });

            // Sinergia Aspectos (Armonía)
            state.currentAspects.filter(a => a.type === 'trine').forEach(asp => {
                if (asp.p1.desc === c.element || asp.p2.desc === c.element) {
                    pwr += 1;
                }
            });

            if (c.owner === 'PLAYER') pTotal += pwr;
            else eTotal += pwr;
        });
    }
    state.playerScore = Math.floor(pTotal);
    state.enemyScore = Math.floor(eTotal);
    updateHeader();
}

function advanceRound() {
    state.round++;
    if (state.round > state.maxRounds) {
        endGame(state.playerScore > state.enemyScore ? 'MAESTRO DE LAS ESTRELLAS' : 'COLAPSO COSMICO');
        return;
    }
    state.energy = state.maxEnergy;
    state.turn = 'PLAYER';
    updateEnergyUI();
    setStatus(`RONDA ${state.round}`, "#00f3ff");
}

function enemyAI() {
    if (state.enemyDeck.length === 0) {
        log("SISTEMA SIN DESTINO: El oponente se ha quedado sin cartas.", "SYS");
        state.turn = 'PLAYER'; // Forzar fin si no hay cartas
        advanceRound();
        return;
    }
    const house = Math.floor(Math.random() * 12);
    const card = state.enemyDeck.pop();
    log(`SISTEMA juega ${card.name} en ${SIGNS[house]}.`, "ENEMY");
    playCardFromObject(card, house, 'ENEMY');
}

function playCardFromObject(card, houseIdx, owner) {
    // Versión de playCard que acepta un objeto directamente para el enemigo
    state.houses[houseIdx].push({
        ...card,
        owner: owner,
        originalId: card.id
    });
    recalculateGlobalScore();
    renderBoard();
    processEndTurnEffects();
}

/* ================= RENDERIZADO ================= */

function renderBoard() {
    document.querySelectorAll('.token').forEach(t => t.remove());
    state.houses.forEach((house, hIdx) => {
        house.forEach(c => spawnToken(hIdx, c, c.owner));

        // Estrés Elemental (Visual)
        const hEl = document.querySelector(`.house-interactive[data-idx="${hIdx}"]`);
        if (hEl) {
            const isDesync = house.some(c => MATRIX[c.element].weak === getElementOfSign(hIdx));
            if (isDesync) hEl.classList.add('house-stress');
            else hEl.classList.remove('house-stress');
        }
    });
}

function renderMandala() {
    const m = document.getElementById('mandala');
    m.innerHTML = '<div id="orbits-layer"></div>';
    for (let i = 0; i < 12; i++) {
        let label = document.createElement('div');
        label.className = 'house-interactive'; label.dataset.idx = i;
        label.onclick = () => selectHouse(i);
        const rad = ((i * 30) + 15 - 90) * (Math.PI / 180);
        const r = 43;
        label.style.left = (50 + r * Math.cos(rad)) + '%'; label.style.top = (50 + r * Math.sin(rad)) + '%';
        label.innerHTML = `<div>${SIGNS[i].substring(0, 3)}</div>`;
        m.appendChild(label);
    }
}

function renderPlanets() {
    const layer = document.getElementById('orbits-layer');
    state.planetPositions.forEach(p => {
        let orb = document.createElement('div');
        orb.className = 'planet-orbit-arm';
        orb.style.transform = `rotate(${p.angle}deg)`;
        const symbol = document.createElement('div');
        symbol.className = 'planet-symbol'; symbol.innerText = p.glyph;
        symbol.style.color = p.color; symbol.style.transform = `rotate(-${p.angle}deg)`;
        symbol.onmouseenter = () => setInspector(`<b>${p.name}</b> en ${SIGNS[p.signIdx]}<br>Elemento: ${p.desc}`);
        orb.appendChild(symbol);
        layer.appendChild(orb);
    });
}

function drawAspects() {
    const layer = document.getElementById('orbits-layer');
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute('width', '100%'); svg.setAttribute('height', '100%');
    svg.style.position = 'absolute'; svg.style.top = '0'; svg.style.left = '0';
    svg.style.pointerEvents = 'none';

    state.currentAspects.forEach(asp => {
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.className = 'geo-line ' + (asp.type === 'trine' ? 'pulse-green' : 'pulse-red');
        const r = 35;
        const a1 = (asp.p1.angle - 90) * (Math.PI / 180);
        const a2 = (asp.p2.angle - 90) * (Math.PI / 180);
        line.setAttribute('x1', `${50 + r * Math.cos(a1)}%`); line.setAttribute('y1', `${50 + r * Math.sin(a1)}%`);
        line.setAttribute('x2', `${50 + r * Math.cos(a2)}%`); line.setAttribute('y2', `${50 + r * Math.sin(a2)}%`);
        line.setAttribute('stroke', asp.color);
        line.setAttribute('stroke-width', '2');
        line.onmouseenter = () => setInspector(`<b>Aspecto: ${asp.type === 'trine' ? 'TRINO' : 'CUADRATURA'}</b><br>${asp.type === 'trine' ? 'Armonía: PBA +2' : 'Tensión: Costo Éter +1'}`);
        svg.appendChild(line);
    });
    layer.appendChild(svg);
}

/* ================= UTILS UI ================= */

function updateEnergyUI() {
    const fill = document.getElementById('energy-fill');
    const text = document.getElementById('energy-text');
    if (fill) fill.style.width = `${(state.energy / state.maxEnergy) * 100}%`;
    if (text) text.innerText = `ÉTER: ${state.energy}/${state.maxEnergy}`;
}

function renderHandUI() {
    const c = document.getElementById('hand-container'); c.innerHTML = '';
    state.hand.forEach((card, i) => {
        const cost = calculateRealCost(card);
        let el = document.createElement('div'); el.className = 'card ' + (state.selectedCardIdx === i ? 'selected' : '');
        if (state.energy < cost) el.classList.add('card-disabled');

        el.onclick = () => selectCard(i);
        el.style.borderLeftColor = MATRIX[card.element].color;
        el.onmouseenter = () => setInspector(`<b>${card.name}</b> [${card.element}]<br>${card.desc}<br><i>Éter: ${cost} (Base: ${card.cost})</i>`);

        el.innerHTML = `<div class="card-top"><span class="card-name">${card.name}</span><span class="card-cost">${cost}⚡</span></div><div class="card-bot">${card.effect}</div>`;
        c.appendChild(el);
    });
}

function highlightSynergies() {
    document.querySelectorAll('.synergy-highlight').forEach(el => el.classList.remove('synergy-highlight'));
    if (state.selectedCardIdx === null) return;
    const card = state.hand[state.selectedCardIdx];
    for (let i = 0; i < 12; i++) {
        if (getElementOfSign(i) === card.element) {
            document.querySelector(`.house-interactive[data-idx="${i}"]`).classList.add('synergy-highlight');
        }
    }
}

function spawnToken(houseIdx, card, owner) {
    const m = document.getElementById('mandala');
    let t = document.createElement('div');
    t.className = 'token ' + (owner === 'ENEMY' ? 'enemy-token' : '');
    t.style.borderColor = MATRIX[card.element].color;
    t.style.backgroundColor = owner === 'ENEMY' ? 'transparent' : MATRIX[card.element].color;
    const angle = (houseIdx * 30) + 15 + (Math.random() * 16 - 8);
    const rad = (angle - 90) * (Math.PI / 180);
    const d = 18 + (Math.random() * 14);
    t.style.left = (50 + d * Math.cos(rad)) + '%'; t.style.top = (50 + d * Math.sin(rad)) + '%';
    m.appendChild(t);
}

function shakeScreen(magnitude) {
    document.body.classList.add('shaking');
    setTimeout(() => document.body.classList.remove('shaking'), 500);
}

function triggerVisualEffect(hIdx, type, color) {
    if (type === 'explosion') {
        createShockwave(hIdx, color);
        createParticles(hIdx, color, 30);
    } else {
        createParticles(hIdx, color, 12);
    }
}

function createShockwave(hIdx, color) {
    const m = document.getElementById('mandala');
    const angle = (hIdx * 30) + 15; const rad = (angle - 90) * (Math.PI / 180);
    const x = 50 + 35 * Math.cos(rad); const y = 50 + 35 * Math.sin(rad);

    const shock = document.createElement('div');
    shock.className = 'effect-shockwave';
    shock.style.borderColor = color;
    shock.style.left = x + '%'; shock.style.top = y + '%';
    m.appendChild(shock);
    setTimeout(() => shock.remove(), 800);
}

function createParticles(hIdx, color, count = 10) {
    const m = document.getElementById('mandala');
    const angle = (hIdx * 30) + 15; const rad = (angle - 90) * (Math.PI / 180);
    const x = 50 + 35 * Math.cos(rad); const y = 50 + 35 * Math.sin(rad);
    for (let i = 0; i < count; i++) {
        let p = document.createElement('div'); p.className = 'particle'; p.style.background = color;
        p.style.left = x + '%'; p.style.top = y + '%'; m.appendChild(p);
        const tx = (Math.random() - 0.5) * 200; const ty = (Math.random() - 0.5) * 200;
        p.animate([
            { transform: 'scale(1.5)', opacity: 1 },
            { transform: `translate(${tx}px,${ty}px) scale(0)`, opacity: 0 }
        ], { duration: 800 + Math.random() * 400, easing: 'cubic-bezier(0, .9, .57, 1)' }).onfinish = () => p.remove();
    }
}

function createMouseParticle(x, y) {
    const p = document.createElement('div'); p.className = 'mouse-particle';
    p.style.left = x + 'px'; p.style.top = y + 'px';
    document.body.appendChild(p);
    setTimeout(() => p.remove(), 600);
}

function createFloatingText(houseIdx, txt, col) {
    const el = document.createElement('div'); el.className = 'floating-text'; el.innerText = txt; el.style.color = col;
    const rad = ((houseIdx * 30) + 15 - 90) * (Math.PI / 180);
    el.style.left = (50 + 30 * Math.cos(rad)) + '%'; el.style.top = (50 + 30 * Math.sin(rad)) + '%';
    document.getElementById('mandala').appendChild(el); setTimeout(() => el.remove(), 1500);
}

function getElementOfSign(idx) { if ([0, 4, 8].includes(idx)) return "Fuego"; if ([1, 5, 9].includes(idx)) return "Tierra"; if ([2, 6, 10].includes(idx)) return "Aire"; return "Agua"; }
function setInspector(html) { document.getElementById('inspector-content').innerHTML = html || "..."; }
function updateHeader() {
    document.getElementById('p-score').innerText = state.playerScore;
    document.getElementById('e-score').innerText = state.enemyScore;
    document.getElementById('day-counter').innerText = `RONDA ${state.round}/${state.maxRounds}`;
}
function setStatus(msg, col) { const el = document.getElementById('status-text'); el.innerText = msg; el.style.color = col || '#fff'; }
function drawHand() { for (let i = 0; i < 5; i++) state.hand.push(randomCard()); renderHandUI(); }
function randomCard() { return ARCANOS[Math.floor(Math.random() * ARCANOS.length)]; }
function log(m, t) { document.getElementById('game-log').insertAdjacentHTML('afterbegin', `<div class="log-entry log-${t}">[R${state.round}] ${m}</div>`); }
function endGame(r) { alert(r); location.reload(); }

window.onload = init;
