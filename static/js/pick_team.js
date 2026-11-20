let PLAYERS_DATA = [];

'use strict';

const BUDGET       = 100.0;
const MAX_PER_CLUB = 3;
const FREE_TRANSFERS = 2;

const FORMATIONS = {
    '4-4-2': { DEF: 4, MID: 4, FWD: 2 },
    '4-3-3': { DEF: 4, MID: 3, FWD: 3 },
    '3-5-2': { DEF: 3, MID: 5, FWD: 2 },
    '5-3-2': { DEF: 5, MID: 3, FWD: 2 },
    '3-4-3': { DEF: 3, MID: 4, FWD: 3 },
};

const POS_LIMITS   = { GK: 2, DEF: 5, MID: 5, FWD: 3 };
const POS_LABELS   = { GK: 'Golman', DEF: 'Branič', MID: 'Veznjak', FWD: 'Napadač' };

let remainingBudget  = BUDGET;
let currentFormation = '4-4-2';
let activeSlotKey    = null;   // which pitch/bench slot is being filled
let captainId        = null;
let viceCaptainId    = null;
let filterPos        = 'ALL';
let searchQuery      = '';


const bench = { bench_gk: null, bench_def: null, bench_mid: null, bench_fwd: null };
let starting = {};

document.addEventListener('DOMContentLoaded', () => {
    PLAYERS_DATA = JSON.parse(document.getElementById('players-data').textContent);
    const modal = document.getElementById('welcome-modal');
    document.getElementById('welcome-close').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    document.querySelectorAll('.pick-formation-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pick-formation-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            changeFormation(btn.dataset.formation);
        });
    });

    document.querySelectorAll('.pick-filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pick-filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterPos = btn.dataset.pos;
            renderSidebar();
        });
    });

    document.getElementById('player-search').addEventListener('input', e => {
        searchQuery = e.target.value.toLowerCase();
        renderSidebar();
    });


    buildStartingSlots(currentFormation);
    renderPitch();
    renderBenchSlots();
    renderSidebar();
});

//Formation
function changeFormation(formation) {
    if (!FORMATIONS[formation]) return;

    const current = Object.values(starting).filter(Boolean);

    buildStartingSlots(formation);
    currentFormation = formation;

    const byPos = { GK: [], DEF: [], MID: [], FWD: [] };
    current.forEach(p => byPos[p.position].push(p));

    Object.keys(starting).forEach(key => starting[key] = null);

    Object.keys(starting).forEach(key => {
        const pos = slotPos(key);
        if (byPos[pos].length) {
            starting[key] = byPos[pos].shift();
        }
    });


    renderPitch();
    updateBudget();
    updateProgress();
    renderSidebar();
}

function buildStartingSlots(formation) {
    const f = FORMATIONS[formation];
    starting = {};
    starting['gk1'] = null;
    for (let i = 1; i <= f.DEF; i++) starting[`def${i}`] = null;
    for (let i = 1; i <= f.MID; i++) starting[`mid${i}`] = null;
    for (let i = 1; i <= f.FWD; i++) starting[`fwd${i}`] = null;
}

function slotPos(key) {
    if (key.startsWith('gk'))    return 'GK';
    if (key.startsWith('def'))   return 'DEF';
    if (key.startsWith('mid'))   return 'MID';
    if (key.startsWith('fwd'))   return 'FWD';
    if (key === 'bench_gk')      return 'GK';
    if (key === 'bench_def')     return 'DEF';
    if (key === 'bench_mid')     return 'MID';
    if (key === 'bench_fwd')     return 'FWD';
    return null;
}


function renderPitch() {
    const pitch = document.getElementById('pick-pitch');
    const f     = FORMATIONS[currentFormation];

    const gkRow  = rowHtml(['gk1']);
    const defRow = rowHtml(range('def', f.DEF));
    const midRow = rowHtml(range('mid', f.MID));
    const fwdRow = rowHtml(range('fwd', f.FWD));

    pitch.innerHTML = gkRow + defRow + midRow + fwdRow;
    attachSlotHandlers(starting);
}

function renderBenchSlots() {
    const container = document.getElementById('bench-slots');
    const keys = ['bench_gk', 'bench_def', 'bench_mid', 'bench_fwd'];
    container.innerHTML = keys.map(key => slotHtml(key, bench[key])).join('');
    attachSlotHandlers(bench);
}

function rowHtml(keys) {
    return `<div class="pitch-row">${keys.map(k => slotHtml(k, starting[k])).join('')}</div>`;
}

function slotHtml(key, player) {
    const pos = slotPos(key);
    if (!player) {
        return `
        <div class="pitch-slot pitch-slot--empty" id="slot-${key}" data-slot="${key}">
            <div class="pitch-slot__avatar"><i class="fas fa-plus"></i></div>
            <p class="pitch-slot__pos">${pos}</p>
        </div>`;
    }
    const isCap  = player.player_id === captainId;
    const isVice = player.player_id === viceCaptainId;
    const badge  = isCap  ? '<span class="pitch-slot__cap-badge">C</span>'
                 : isVice ? '<span class="pitch-slot__cap-badge pitch-slot__cap-badge--vice">V</span>'
                 : '';
    return `
    <div class="pitch-slot pitch-slot--filled" id="slot-${key}" data-slot="${key}">
        ${badge}
        <div class="pitch-slot__avatar pitch-slot__avatar--filled">${initials(player.first_name, player.last_name)}</div>
        <p class="pitch-slot__name">${player.last_name}</p>
        <p class="pitch-slot__club">${player.team_short}</p>
        <p class="pitch-slot__price">${player.price.toFixed(1)}m</p>
        <button class="pitch-slot__remove" data-slot="${key}"><i class="fas fa-times"></i></button>
    </div>`;
}

function attachSlotHandlers(slotObj) {
    Object.keys(slotObj).forEach(key => {
        const el = document.getElementById('slot-' + key);
        if (!el) return;

        el.addEventListener('click', (e) => {
            if (e.target.closest('.pitch-slot__remove')) return;
            activeSlotKey = key;
            document.querySelectorAll('.pitch-slot').forEach(s => s.classList.remove('active'));
            el.classList.add('active');
            // Auto-filter sidebar to this position
            const pos = slotPos(key);
            filterPos = pos;
            document.querySelectorAll('.pick-filter-btn').forEach(b => {
                b.classList.toggle('active', b.dataset.pos === pos);
            });
            renderSidebar();
        });

        const removeBtn = el.querySelector('.pitch-slot__remove');
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                removeFromSlot(key, slotObj);
            });
        }
    });
}

function range(prefix, count) {
    return Array.from({ length: count }, (_, i) => `${prefix}${i + 1}`);
}


function addToSlot(player) {
    if (!activeSlotKey) return;

    const isStarting = activeSlotKey in starting;
    const slotObj    = isStarting ? starting : bench;

    const prev = slotObj[activeSlotKey];
    if (prev) {
        remainingBudget = round1(remainingBudget + prev.price);
        if (prev.player_id === captainId)     captainId = null;
        if (prev.player_id === viceCaptainId) viceCaptainId = null;
    }

    slotObj[activeSlotKey] = player;
    remainingBudget = round1(remainingBudget - player.price);

    activeSlotKey = null;
    document.querySelectorAll('.pitch-slot').forEach(s => s.classList.remove('active'));

    renderPitch();
    renderBenchSlots();
    updateBudget();
    updateProgress();
    renderSidebar();
    renderCaptainGrid();
}

function removeFromSlot(key, slotObj) {
    const player = slotObj[key];
    if (!player) return;

    remainingBudget = round1(remainingBudget + player.price);
    if (player.player_id === captainId)     captainId = null;
    if (player.player_id === viceCaptainId) viceCaptainId = null;

    slotObj[key] = null;

    renderPitch();
    renderBenchSlots();
    updateBudget();
    updateProgress();
    renderSidebar();
    renderCaptainGrid();
}


function renderSidebar() {
    const list = document.getElementById('sidebar-player-list');

    const pickedIds = new Set([
        ...Object.values(starting).filter(Boolean).map(p => p.player_id),
        ...Object.values(bench).filter(Boolean).map(p => p.player_id),
    ]);

    const clubCount = {};
    [...Object.values(starting), ...Object.values(bench)].forEach(p => {
        if (p) clubCount[p.team_name] = (clubCount[p.team_name] || 0) + 1;
    });

    const posCount = {};
    Object.keys(POS_LIMITS).forEach(pos => {
        posCount[pos] = [...Object.values(starting), ...Object.values(bench)]
            .filter(p => p && p.position === pos).length;
    });

    let players = PLAYERS_DATA.filter(p => {
        if (pickedIds.has(p.player_id)) return false;
        if (filterPos !== 'ALL' && p.position !== filterPos) return false;
        if (searchQuery && !`${p.first_name} ${p.last_name}`.toLowerCase().includes(searchQuery)) return false;
        return true;
    });

    players.sort((a, b) => {
        const aOk = a.price <= remainingBudget;
        const bOk = b.price <= remainingBudget;
        if (aOk !== bOk) return aOk ? -1 : 1;
        return b.total_points - a.total_points;
    });

    if (players.length === 0) {
        list.innerHTML = '<p class="pick-sidebar__empty">Nema dostupnih igrača.</p>';
        return;
    }

    list.innerHTML = players.map(p => {
        const tooExp   = p.price > remainingBudget;
        const clubFull = (clubCount[p.team_name] || 0) >= MAX_PER_CLUB;
        const posFull  = posCount[p.position] >= POS_LIMITS[p.position];
        const disabled = tooExp || clubFull || posFull;

        let reason = '';
        if (tooExp)   reason = '<span class="sidebar-card__reason">Nedovoljno sredstava</span>';
        else if (clubFull) reason = '<span class="sidebar-card__reason">Maks. klub</span>';
        else if (posFull)  reason = '<span class="sidebar-card__reason">Popunjena pozicija</span>';

        return `
        <div class="sidebar-card ${disabled ? 'sidebar-card--disabled' : ''}"
             ${disabled ? '' : `onclick="sidebarPick(${p.player_id})"`}>
            <div class="sidebar-card__avatar">${initials(p.first_name, p.last_name)}</div>
            <div class="sidebar-card__info">
                <p class="sidebar-card__name">${p.first_name} ${p.last_name}</p>
                <p class="sidebar-card__meta">${p.team_short} · ${p.position}</p>
                ${reason}
            </div>
            <div class="sidebar-card__stats">
                <span class="sidebar-card__price ${tooExp ? 'text-danger' : 'text-gold'}">${p.price.toFixed(1)}m</span>
                <span class="sidebar-card__pts">${p.total_points} bod</span>
            </div>
        </div>`;
    }).join('');
}

function sidebarPick(playerId) {
    if (!activeSlotKey) {
        const player = PLAYERS_DATA.find(p => p.player_id === playerId);
        if (!player) return;

        const emptyStarting = Object.keys(starting).find(
            k => !starting[k] && slotPos(k) === player.position
        );
        const emptyBench = Object.keys(bench).find(
            k => !bench[k] && slotPos(k) === player.position
        );

        const slot = emptyStarting || emptyBench;
        if (!slot) return;

        activeSlotKey = slot;
    }

    const player = PLAYERS_DATA.find(p => p.player_id === playerId);
    if (player) addToSlot(player);
}


function renderCaptainGrid() {
    const wrap = document.getElementById('captain-wrap');
    const grid = document.getElementById('captain-grid');
    const total = allPicked().length;

    if (total < 15) {
        wrap.style.display = 'none';
        return;
    }

    wrap.style.display = 'block';

    const startingPlayers = Object.values(starting).filter(Boolean);
    grid.innerHTML = startingPlayers.map(p => {
        const isCap  = p.player_id === captainId;
        const isVice = p.player_id === viceCaptainId;
        return `
        <div class="captain-card ${isCap ? 'captain-card--cap' : ''} ${isVice ? 'captain-card--vice' : ''}">
            <div class="captain-card__avatar">${initials(p.first_name, p.last_name)}</div>
            <p class="captain-card__name">${p.last_name}</p>
            <p class="captain-card__club">${p.team_short}</p>
            <div class="captain-card__btns">
                <button class="cap-btn ${isCap ? 'cap-btn--active' : ''}"
                        onclick="setCaptain(${p.player_id})">C</button>
                <button class="cap-btn cap-btn--v ${isVice ? 'cap-btn--active' : ''}"
                        onclick="setVice(${p.player_id})">V</button>
            </div>
        </div>`;
    }).join('');
}

function setCaptain(id) {
    if (viceCaptainId === id) viceCaptainId = null;
    captainId = id;
    renderCaptainGrid();
    renderPitch();
    updateProgress();
}

function setVice(id) {
    if (captainId === id) captainId = null;
    viceCaptainId = id;
    renderCaptainGrid();
    renderPitch();
    updateProgress();
}


function updateBudget() {
    document.getElementById('remaining-budget').textContent = remainingBudget.toFixed(1) + 'm';
    document.getElementById('spent-budget').textContent     = round1(BUDGET - remainingBudget).toFixed(1) + 'm';
}

function updateProgress() {
    const filled = allPicked().length;
    document.getElementById('progress-count').textContent          = `${filled} / 15`;
    document.getElementById('progress-bar-fill').style.width       = `${(filled / 15) * 100}%`;

    const canSave = filled === 15 && captainId && viceCaptainId;
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = !canSave;
}

function allPicked() {
    return [
        ...Object.values(starting).filter(Boolean),
        ...Object.values(bench).filter(Boolean),
    ];
}


async function saveTeam() {
    const teamName = document.getElementById('team-name-input').value.trim();
    if (!teamName || teamName.length < 3) {
        showError('Unesite naziv tima (min. 3 karaktera).');
        return;
    }
    if (!captainId || !viceCaptainId) {
        showError('Postavite kapitena i potkapitena.');
        return;
    }

    const startingIds = Object.values(starting).filter(Boolean).map(p => p.player_id);
    const benchIds    = Object.values(bench).filter(Boolean).map(p => p.player_id);
    const playerIds   = [...startingIds, ...benchIds];

    if (playerIds.length !== 15) {
        showError('Morate odabrati svih 15 igrača.');
        return;
    }

    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Snimanje...';

    try {
        const res  = await fetch('/fantasy/pick-team', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                team_name:       teamName,
                player_ids:      playerIds,
                captain_id:      captainId,
                vice_captain_id: viceCaptainId,
            }),
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = data.redirect || '/fantasy/my-team';
        } else {
            showError(data.message || 'Greška pri snimanju.');
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-check"></i> Spremi tim';
        }
    } catch {
        showError('Greška pri komunikaciji sa serverom.');
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fas fa-check"></i> Spremi tim';
    }
}


function initials(first, last) {
    return ((first?.[0] ?? '') + (last?.[0] ?? '')).toUpperCase();
}

function round1(n) {
    return Math.round(n * 10) / 10;
}

function showError(msg) {
    const el = document.getElementById('pick-error');
    el.textContent  = msg;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 4000);
}