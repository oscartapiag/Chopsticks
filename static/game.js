const API_BASE = '/api';

// Colors from Style/Python
const COLORS = {
    human: "#89B4FA",
    ai: "#F38BA8",
    finger: "#F9E2AF", // Yellow/Peach
    select: "#A6E3A1", // Green
    bg: "#1E1E2E"
};

let gameState = {
    human_hands: [1, 1],
    ai_hands: [1, 1],
    turn: 'human',
    winner: null
};

let selectedHand = null; // 'l' or 'r'
let gameOver = false;



document.addEventListener('DOMContentLoaded', () => {
    log("Game Started.");
    fetchState();
});

// ---------------------------
// LOGIC
// ---------------------------

async function fetchState() {
    try {
        const res = await fetch(`${API_BASE}/state?t=${Date.now()}`);
        const data = await res.json();
        updateUI(data);
    } catch (e) {
        console.error("Failed to fetch state", e);
    }
}

function updateUI(data) {
    gameState = data;
    // log(`UpdateUI: Turn=${data.turn} Winner=${data.winner}`);

    // Draw Hands
    drawHand('cv-human-l', data.human_hands[0], true, selectedHand === 'l');
    drawHand('cv-human-r', data.human_hands[1], true, selectedHand === 'r');
    drawHand('cv-ai-l', data.ai_hands[0], false, false);
    drawHand('cv-ai-r', data.ai_hands[1], false, false);

    // Update Status
    const statusLbl = document.getElementById('status-bar');
    const subLbl = document.getElementById('sub-status');

    if (data.winner !== null) {
        gameOver = true;
        if (data.winner === 'human' || data.winner === 0) {
            statusLbl.textContent = "YOU WIN!";
            statusLbl.style.color = COLORS.select;
            subLbl.textContent = "Congratulations!";
        } else if (data.winner === 'ai' || data.winner === 1) {
            statusLbl.textContent = "AI WINS";
            statusLbl.style.color = COLORS.ai;
            subLbl.textContent = "Better luck next time.";
        } else if (data.winner === 'human_stalemate') {
            statusLbl.textContent = "YOU WIN (BY RULES)";
            statusLbl.style.color = COLORS.select;
            subLbl.textContent = "Loop detected. You had more fingers.";
        } else if (data.winner === 'ai_stalemate') {
            statusLbl.textContent = "AI WINS (BY RULES)";
            statusLbl.style.color = COLORS.ai;
            subLbl.textContent = "Loop detected. AI had more fingers.";
        } else if (data.winner === 'draw' || data.winner === -1) {
            statusLbl.textContent = "GAME TIED";
            statusLbl.style.color = COLORS.finger;
            subLbl.textContent = "Both players have equal fingers in loop.";
        }
        return;
    }

    if (data.turn === 'human') {
        statusLbl.textContent = "Your Turn";
        statusLbl.style.color = COLORS.human;
        if (selectedHand) {
            subLbl.textContent = "Select a target to attack or split";
        } else {
            subLbl.textContent = "Select your hand";
        }
    } else {
        statusLbl.textContent = "AI Thinking...";
        statusLbl.style.color = COLORS.ai;
        subLbl.textContent = "Please wait";

        // Trigger AI
        setTimeout(triggerAIMove, 800);
    }
}

async function handleCanvasClick(owner, side) {
    // console.log(`[Click] Owner: ${owner}, Side: ${side}, Turn: ${gameState.turn}, GameOver: ${gameOver}, Selected: ${selectedHand}`);

    if (gameOver) {
        console.warn("Click ignored: Game Over");
        return;
    }

    if (gameState.turn !== 'human') {
        console.warn("Click ignored: Not human turn");
        return;
    }

    if (selectedHand === null) {
        // Selection State
        if (owner === 'ai') {
            log("Select your own hand first!");
            return;
        }
        const fingers = side === 'l' ? gameState.human_hands[0] : gameState.human_hands[1];
        if (fingers === 0) {
            log("Cannot select empty hand.");
            return;
        }
        selectedHand = side;
        console.log(`[Selection] Selected hand: ${selectedHand}`);
        // Just refresh UI to show selection
        fetchState();
    } else {
        // Action State
        const source = selectedHand;
        const target = side;
        console.log(`[Action] Source: ${source}, Target: ${target}, Owner: ${owner}`);

        if (owner === 'human') {
            if (source === target) {
                // Deselect
                console.log("[Action] Deselecting");
                selectedHand = null;
                fetchState();
            } else {
                // Split
                log(`Attempting Split ${source.toUpperCase()} -> ${target.toUpperCase()}`);
                await sendMove('s', source); // API handles split logic if m0='s', but wait..
                // My API expects m0='s', m1='l/r'.
                // If I click Left then Right: source='l', target='r'.
                // If I click Right then Left: source='r', target='l'.
                // stick.py split logic: split(left): if true, split left hand.
                // So if source is 'l', we split 'l'.
                // My API m0='s', m1=source.
                // Let's check sendMove
            }
        } else {
            // Hit
            log(`Attempting Hit ${source.toUpperCase()} -> ${target.toUpperCase()}`);
            await sendMove(source, target);
        }
    }
}

async function sendMove(m0, m1) {
    // Note: for split, I decided in game.js before that m0='s', m1=handedness.
    // If I split FROM left, logic says split(True).
    // In app.py: m0='s'. if m1='l' -> split(True).
    // So if m0='s', m1 should be the SOURCE hand.

    // If hitting: m0=source, m1=target.

    const payload = { m0, m1 };



    try {
        const res = await fetch(`${API_BASE}/move`, {
            method: 'POST',

            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });


        const json = await res.json();

        if (!res.ok) {
            log(`Invalid move: ${json.detail}`);
            alert(`Error: ${json.detail}`);
            // Don't deselect, let user retry
        } else {
            if (m0 === 's') {
                log(`You: Split ${m1.toUpperCase()}`);
            } else {
                log(`You: Hit ${m0.toUpperCase()} -> ${m1.toUpperCase()}`);
            }
            selectedHand = null;
            fetchState();
        }
    } catch (e) {
        console.error(e);
        log(`Network Error: ${e.message}`);
    }
}

async function triggerAIMove() {
    try {
        const res = await fetch(`${API_BASE}/ai_move`, { method: 'POST' });


        const data = await res.json();

        if (!res.ok) {
            console.warn("AI Move failed:", data);
            // If backend says not AI turn, or other error, we should resync.
            log(`Syncing... (Backend says: ${data.detail})`);
            fetchState();
            return;
        }

        if (data.status === 'game_over') {
            fetchState(); // will handle winner
            return;
        }

        const move = data.ai_move_made; // e.g. "ll" or "sl"
        if (move) {
            let desc = "";
            if (move[0] === 's') {
                desc = `Split ${move[1].toUpperCase()}`;
            } else {
                desc = `Hit ${move[0].toUpperCase()} -> ${move[1].toUpperCase()}`;
            }
            log(`AI: ${desc}`);
        }
        fetchState();
    } catch (e) {
        console.error(e);
        log(`AI Error: ${e.message}`);
        // Reset state/poll again just in case? Or alert?
        alert(`AI Move Failed: ${e.message}. See Console.`);
        fetchState(); // Attempt to resync
    }
}

async function resetGame() {
    await fetch(`${API_BASE}/reset`, { method: 'POST' });
    log("Game Started.");
    gameOver = false;
    selectedHand = null;
    fetchState();
}

function log(msg) {
    const box = document.getElementById('log-box');
    box.innerHTML += `> ${msg}\n`;
    box.scrollTop = box.scrollHeight;
}

// ---------------------------
// CANVAS DRAWING (Ported from gui.py)
// ---------------------------
function drawHand(canvasId, fingers, isHuman, isSelected) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    // Clear
    ctx.fillStyle = COLORS.bg;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const w = 120;
    const h = 120;
    const cx = w / 2;

    let cy, dy;
    // Orientation
    if (isHuman) {
        cy = h - 35;
        dy = -1;
    } else {
        cy = 35;
        dy = 1;
    }

    const baseColor = isHuman ? COLORS.human : COLORS.ai;
    const palmFill = isSelected ? COLORS.select : baseColor;
    const fingerFill = COLORS.finger;

    // 1. Draw Fingers
    let offsets = [];
    if (fingers === 1) offsets = [0];
    else if (fingers === 2) offsets = [-12, 12];
    else if (fingers === 3) offsets = [-20, 0, 20];
    else if (fingers === 4) offsets = [-28, -10, 10, 28];

    ctx.strokeStyle = fingerFill;
    ctx.lineWidth = 14;
    ctx.lineCap = 'round';

    offsets.forEach(off => {
        const x = cx + off;
        ctx.beginPath();
        ctx.moveTo(x, cy);
        ctx.lineTo(x, cy + (dy * 50));
        ctx.stroke();
    });

    // 2. Draw Palm
    const r = 30;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.fillStyle = palmFill;
    ctx.fill();
    ctx.lineWidth = 3;
    ctx.strokeStyle = baseColor;
    ctx.stroke();

    // Text count
    ctx.fillStyle = COLORS.bg;
    ctx.font = "bold 16px Helvetica";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(fingers.toString(), cx, cy);
}
