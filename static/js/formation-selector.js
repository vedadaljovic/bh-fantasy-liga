'use strict';

const POS_LABEL = { GK: 'Golman', DEF: 'Branič', MID: 'Veznjak', FWD: 'Napadač' };
const POS_ABB   = { GK: 'GK', DEF: 'DF', MID: 'MF', FWD: 'FW' };

let allPlayers     = [];
let startingPlayers = [];
let benchPlayers    = [];
let currentFormation = '4-4-2';

let subModeActive  = false;
let selectedPlayer = null;

document.addEventListener('DOMContentLoaded', () => {

    try { startingPlayers = JSON.parse(document.getElementById('starting-data').textContent); } catch(e) {}
    try { benchPlayers    = JSON.parse(document.getElementById('bench-data').textContent); }    catch(e) {}
    allPlayers = [...startingPlayers, ...benchPlayers];

    const formationSpan = document.getElementById('current-formation');
    if (formationSpan) currentFormation = formationSpan.textContent.trim();

    const formationToggle   = document.getElementById('formation-toggle');
    const formationSelector = document.getElementById('formation-selector');
    const formationClose    = document.getElementById('formation-close');

    formationToggle?.addEventListener('click', () => formationSelector.classList.toggle('active'));
    formationClose?.addEventListener('click',  () => formationSelector.classList.remove('active'));
    document.addEventListener('click', (e) => {
        if (!formationSelector?.contains(e.target) && !formationToggle?.contains(e.target)) {
            formationSelector?.classList.remove('active');
        }
    });

    renderAll();
});


function renderAll() {
    renderPitch();
    renderBench();
}

function renderPitch() {
    const display = document.getElementById('formation-display');
    if (!display) return;

    const gk  = startingPlayers.filter(p => p.position === 'GK');
    const def = startingPlayers.filter(p => p.position === 'DEF');
    const mid = startingPlayers.filter(p => p.position === 'MID');
    const fwd = startingPlayers.filter(p => p.position === 'FWD');

    display.innerHTML = `
        <div class="formation-row formation-row--gk">
            ${gk.map(p => playerSlotHtml(p)).join('')}
        </div>
        <div class="formation-row formation-row--defenders">
            ${def.map(p => playerSlotHtml(p)).join('')}
        </div>
        <div class="formation-row formation-row--midfielders">
            ${mid.map(p => playerSlotHtml(p)).join('')}
        </div>
        <div class="formation-row formation-row--forwards">
            ${fwd.map(p => playerSlotHtml(p)).join('')}
        </div>
    `;

    display.querySelectorAll('.player-slot[data-id]').forEach(el => {
        el.addEventListener('click', (e) => onPlayerClick(parseInt(el.dataset.id), e));
    });
}

function renderBench() {
    const container = document.querySelector('.bench-players');
    if (!container) return;

    container.innerHTML = benchPlayers.map(p => {
        const isSelected  = selectedPlayer?.player_id === p.player_id;
        const isEligible  = subModeActive && selectedPlayer && canSwap(selectedPlayer, p);
        return `
        <div class="bench-player bench-player--clickable
                    ${isSelected  ? 'bench-player--selected'  : ''}
                    ${isEligible  ? 'bench-player--eligible'  : ''}"
             data-id="${p.player_id}">
            <div class="bench-player__avatar">${p.position}</div>
            <div class="bench-player__info">
                <p class="bench-player__name">${p.first_name} ${p.last_name}</p>
                <p class="bench-player__position">${p.team_short} · ${p.position}</p>
            </div>
            <p class="bench-player__points">${p.total_points} bod</p>
        </div>`;
    }).join('');

    container.querySelectorAll('.bench-player[data-id]').forEach(el => {
        el.addEventListener('click', (e) => onPlayerClick(parseInt(el.dataset.id), e));
    });
}

function playerSlotHtml(p) {
    const isSelected = selectedPlayer?.player_id === p.player_id;
    const isEligible = subModeActive && selectedPlayer && canSwap(selectedPlayer, p);
    const badge = p.is_captain
        ? '<span class="player-slot__captain-badge"><i class="fas fa-crown"></i></span>'
        : p.is_vice_captain
        ? '<span class="player-slot__vice-captain-badge"><i class="fas fa-star"></i></span>'
        : '';

    return `
    <div class="player-slot ${p.position === 'GK' ? 'player-slot--gk' : ''}
                            ${isSelected ? 'player-slot--selected' : ''}
                            ${isEligible ? 'player-slot--eligible' : ''}"
         data-id="${p.player_id}">
        <div class="player-slot__content">
            ${badge}
            <div class="player-slot__avatar">${POS_ABB[p.position]}</div>
            <p class="player-slot__name">${p.last_name}</p>
            <p class="player-slot__position">${POS_LABEL[p.position]}</p>
            <p class="player-slot__club">${p.team_short}</p>
        </div>
    </div>`;
}


function onPlayerClick(playerId, e) {
    const player = allPlayers.find(p => p.player_id === playerId);
    if (!player) return;

    if (subModeActive && selectedPlayer && selectedPlayer.player_id !== playerId) {
        if (canSwap(selectedPlayer, player)) {
            executeSwap(selectedPlayer.player_id, player.player_id);
            return;
        }
    }

    cancelSubMode();
    showActionPopup(player, e);
}

function showActionPopup(player, e) {
    removePopup();

    const popup = document.createElement('div');
    popup.id = 'player-action-popup';
    popup.className = 'player-action-popup';
    popup.innerHTML = `
        <div class="player-action-popup__header">
            <strong>${player.first_name} ${player.last_name}</strong>
            <span class="player-action-popup__pos">${player.team_short} · ${player.position}</span>
        </div>
        <div class="player-action-popup__actions">
            <button class="btn btn--outline btn--sm" id="popup-sub">
                <i class="fas fa-right-left"></i> Zamijeni
            </button>
            <button class="btn btn--outline btn--sm" id="popup-cap">
                <i class="fas fa-crown"></i> Kapiten
            </button>
            <button class="btn btn--outline btn--sm" id="popup-vice">
                <i class="fas fa-star"></i> Potkapiten
            </button>
            <button class="btn btn--ghost btn--sm" id="popup-cancel">
                Odustani
            </button>
        </div>
    `;

    popup.style.position = 'fixed';
    popup.style.zIndex   = '999';
    popup.style.left     = Math.min(e.clientX, window.innerWidth - 220) + 'px';
    popup.style.top      = (e.clientY + 12) + 'px';

    document.body.appendChild(popup);

    //Close if clicking outside
    setTimeout(() => {
        document.addEventListener('click', function outsideClick(ev) {
            if (!popup.contains(ev.target)) {
                removePopup();
                document.removeEventListener('click', outsideClick);
            }
        });
    }, 50);

    document.getElementById('popup-sub').addEventListener('click', () => {
        removePopup();
        enterSubMode(player);
    });
    document.getElementById('popup-cap').addEventListener('click', () => {
        removePopup();
        setCaptain(player.player_id, 'captain');
    });
    document.getElementById('popup-vice').addEventListener('click', () => {
        removePopup();
        setCaptain(player.player_id, 'vice');
    });
    document.getElementById('popup-cancel').addEventListener('click', () => {
        removePopup();
    });
}

function removePopup() {
    document.getElementById('player-action-popup')?.remove();
}


function enterSubMode(player) {
    subModeActive  = true;
    selectedPlayer = player;
    showMessage(`Odaberite igrača s kojim želite zamijeniti ${player.last_name}`, 'info');
    renderAll();
}

function cancelSubMode() {
    subModeActive  = false;
    selectedPlayer = null;
}

function canSwap(playerA, playerB) {
    if (playerA.player_id === playerB.player_id) return false;
    if (playerA.position === 'GK' || playerB.position === 'GK') {
        return playerA.position === 'GK' && playerB.position === 'GK';
    }
    return true;
}

async function executeSwap(playerAId, playerBId) {
    cancelSubMode();
    removePopup();

    try {
        const res  = await fetch('/fantasy/swap', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ player_a_id: playerAId, player_b_id: playerBId }),
        });
        const data = await res.json();

        if (data.success) {
            const aIsStarting = startingPlayers.some(p => p.player_id === playerAId);
            const bIsStarting = startingPlayers.some(p => p.player_id === playerBId);
            const playerA = allPlayers.find(p => p.player_id === playerAId);
            const playerB = allPlayers.find(p => p.player_id === playerBId);

            if (aIsStarting && !bIsStarting) {
                startingPlayers = startingPlayers.map(p => p.player_id === playerAId ? playerB : p);
                benchPlayers    = benchPlayers.map(p => p.player_id === playerBId ? playerA : p);
            } else if (!aIsStarting && bIsStarting) {
                startingPlayers = startingPlayers.map(p => p.player_id === playerBId ? playerA : p);
                benchPlayers    = benchPlayers.map(p => p.player_id === playerAId ? playerB : p);
            }

            if (data.formation) {
                const span = document.getElementById('current-formation');
                if (span) span.textContent = data.formation;
            }

            renderAll();
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'error');
            renderAll();
        }
    } catch {
        showMessage('Greška pri komunikaciji sa serverom.', 'error');
        renderAll();
    }
}


async function setCaptain(playerId, role) {
    const currentCap  = allPlayers.find(p => p.is_captain)?.player_id;
    const currentVice = allPlayers.find(p => p.is_vice_captain)?.player_id;

    const captain_id      = role === 'captain' ? playerId : currentCap;
    const vice_captain_id = role === 'vice'    ? playerId : currentVice;

    if (!captain_id || !vice_captain_id) {
        showMessage('Morate imati i kapitena i potkapitena.', 'error');
        return;
    }

    if (captain_id === vice_captain_id) {
        showMessage('Kapiten i potkapiten moraju biti različiti igrači.', 'error');
        return;
    }

    try {
        const res  = await fetch('/fantasy/set-captain', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ captain_id, vice_captain_id }),
        });
        const data = await res.json();

        if (data.success) {
            // Update local state
            allPlayers.forEach(p => {
                p.is_captain      = p.player_id === captain_id;
                p.is_vice_captain = p.player_id === vice_captain_id;
            });
            startingPlayers.forEach(p => {
                p.is_captain      = p.player_id === captain_id;
                p.is_vice_captain = p.player_id === vice_captain_id;
            });
            renderAll();
            showMessage(data.message, 'success');
        } else {
            showMessage(data.message, 'error');
        }
    } catch {
        showMessage('Greška pri komunikaciji sa serverom.', 'error');
    }
}


function showMessage(msg, type) {
    let el = document.getElementById('formation-message');
    if (!el) {
        el = document.createElement('div');
        el.id = 'formation-message';
        document.querySelector('.team-formation')?.prepend(el);
    }
    el.className = `alert alert--${type === 'success' ? 'success' : type === 'info' ? 'info' : 'error'}`;
    el.textContent = msg;
    el.style.display = 'block';
    if (type !== 'info') {
        setTimeout(() => { el.style.display = 'none'; }, 3000);
    }
}