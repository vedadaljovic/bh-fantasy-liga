'use strict';

const POS_LABELS = { GK: 'GK', DEF: 'ODB', MID: 'VEZ', FWD: 'NAP' };
const POS_BADGE  = { GK: 'badge--gold', DEF: 'badge--success', MID: 'badge--info', FWD: 'badge--danger' };

let ALL_PLAYERS = [];
let filtered    = [];
let sortCol     = 'points';
let sortDir     = -1;

try {
    ALL_PLAYERS = JSON.parse(document.getElementById('players-data').textContent);
} catch(e) { console.error('Could not parse players data', e); }

let searchVal = '', clubVal = '', posVal = '', priceVal = '';

document.getElementById('search-input').addEventListener('input', e => {
    searchVal = e.target.value.toLowerCase();
    applyFilters();
});
document.getElementById('filter-club').addEventListener('change', e => {
    clubVal = e.target.value;
    applyFilters();
});
document.getElementById('filter-pos').addEventListener('change', e => {
    posVal = e.target.value;
    applyFilters();
});
document.getElementById('filter-price').addEventListener('change', e => {
    priceVal = e.target.value;
    applyFilters();
});

function applyFilters() {
    filtered = ALL_PLAYERS.filter(p => {
        const name = `${p.first_name} ${p.last_name}`.toLowerCase();
        if (searchVal && !name.includes(searchVal)) return false;
        if (clubVal   && p.team_name !== clubVal)    return false;
        if (posVal    && p.position  !== posVal)     return false;
        if (priceVal === 'low'  && p.price >= 5.0)   return false;
        if (priceVal === 'mid'  && (p.price < 5.0 || p.price > 7.0)) return false;
        if (priceVal === 'high' && p.price <= 7.0)   return false;
        return true;
    });
    sortPlayers();
    renderTable();
}

//Sort
document.querySelectorAll('.sortable').forEach(th => {
    th.addEventListener('click', () => {
        const col = th.dataset.col;
        if (sortCol === col) {
            sortDir *= -1;
        } else {
            sortCol = col;
            sortDir = col === 'points' || col === 'price' ? -1 : 1;
        }
        document.querySelectorAll('.sortable i').forEach(i => {
            i.className = 'fas fa-sort';
        });
        th.querySelector('i').className = sortDir === -1 ? 'fas fa-sort-down' : 'fas fa-sort-up';
        sortPlayers();
        renderTable();
    });
});

function sortPlayers() {
    filtered.sort((a, b) => {
        let valA, valB;
        if (sortCol === 'name')          { valA = `${a.first_name} ${a.last_name}`; valB = `${b.first_name} ${b.last_name}`; }
        else if (sortCol === 'club')     { valA = a.team_name;     valB = b.team_name; }
        else if (sortCol === 'position') { valA = a.position;      valB = b.position; }
        else if (sortCol === 'price')    { valA = a.price;         valB = b.price; }
        else if (sortCol === 'points')   { valA = a.total_points;  valB = b.total_points; }
        if (valA < valB) return -1 * sortDir;
        if (valA > valB) return  1 * sortDir;
        return 0;
    });
}

//Render table
function renderTable() {
    const tbody = document.getElementById('players-tbody');
    const count = document.getElementById('players-count');

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-muted" style="text-align:center;padding:24px;">Nema igrača koji odgovaraju filterima.</td></tr>`;
        count.textContent = 'Nema rezultata';
        return;
    }

    tbody.innerHTML = filtered.map(p => `
        <tr class="player-row" data-id="${p.player_id}" style="cursor:pointer;">
            <td><strong>${p.first_name} ${p.last_name}</strong></td>
            <td>${p.team_name}</td>
            <td><span class="badge ${POS_BADGE[p.position]}">${POS_LABELS[p.position]}</span></td>
            <td>${p.price.toFixed(1)}m</td>
            <td><span class="text-gold">${p.total_points}</span></td>
        </tr>
    `).join('');

    count.textContent = `Prikazano ${filtered.length} od ${ALL_PLAYERS.length} igrača`;

    document.querySelectorAll('.player-row').forEach(row => {
        row.addEventListener('click', () => openDrawer(parseInt(row.dataset.id)));
    });
}

function openDrawer(playerId) {
    const p = ALL_PLAYERS.find(pl => pl.player_id === playerId);
    if (!p) return;

    document.getElementById('drawerName').textContent        = `${p.first_name} ${p.last_name}`;
    document.getElementById('drawerClub').textContent        = p.team_name;
    document.getElementById('drawerPrice').textContent       = p.price.toFixed(1) + 'm';
    document.getElementById('drawerTotalPoints').textContent = p.total_points;

    //Stats
    document.getElementById('drawerGoals').textContent       = p.goals        ?? 0;
    document.getElementById('drawerAssists').textContent     = p.assists      ?? 0;
    document.getElementById('drawerMinutes').textContent     = (p.minutes     ?? 0) + "'";
    document.getElementById('drawerCleanSheets').textContent = p.clean_sheets ?? 0;
    document.getElementById('drawerYellows').textContent     = p.yellow_cards ?? 0;
    document.getElementById('drawerReds').textContent        = p.red_cards    ?? 0;

    const posEl = document.getElementById('drawerPosition');
    posEl.textContent = POS_LABELS[p.position];
    posEl.className   = 'badge ' + POS_BADGE[p.position];

    document.getElementById('playerDrawer').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeDrawer() {
    document.getElementById('playerDrawer').classList.remove('active');
    document.body.style.overflow = '';
}

document.getElementById('drawerClose').addEventListener('click', closeDrawer);
document.getElementById('drawerOverlay').addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDrawer(); });

applyFilters();