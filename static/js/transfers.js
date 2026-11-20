let selectedOutId    = null;
let selectedOutPos   = null;
let selectedOutPrice = 0;
let replSearch       = '';

document.getElementById('close-replacements').addEventListener('click', () => {
    document.getElementById('replacements-panel').classList.remove('active');
    document.querySelectorAll('.pitch-player, .bench-player').forEach(el => el.classList.remove('selected'));
    selectedOutId = null;
});

document.getElementById('replacement-search').addEventListener('input', e => {
    replSearch = e.target.value.toLowerCase();
    renderReplacements();
});

function selectOut(playerId, position, price) {
    selectedOutId    = playerId;
    selectedOutPos   = position;
    selectedOutPrice = price;

    document.querySelectorAll('.pitch-player, .bench-player').forEach(el => el.classList.remove('selected'));
    const el = document.getElementById('tp-' + playerId);
    if (el) el.classList.add('selected');

    document.getElementById('replacements-title').textContent =
        'Zamjena za ' + position;
    document.getElementById('replacements-panel').classList.add('active');
    renderReplacements();
}

function renderReplacements() {
    const list   = document.getElementById('replacements-list');
    const myIds  = new Set(MY_PLAYERS.map(p => p.player_id));
    const budget = BUDGET_LEFT + selectedOutPrice;

    const clubCount = {};
    MY_PLAYERS.filter(p => p.player_id !== selectedOutId).forEach(p => {
        clubCount[p.team_name] = (clubCount[p.team_name] || 0) + 1;
    });

    let players = ALL_PLAYERS.filter(p => {
        if (myIds.has(p.player_id)) return false;
        if (p.position !== selectedOutPos) return false;
        if (replSearch && !`${p.first_name} ${p.last_name}`.toLowerCase().includes(replSearch)) return false;
        return true;
    }).sort((a, b) => b.total_points - a.total_points);

    if (players.length === 0) {
        list.innerHTML = '<p class="text-muted" style="padding:16px;">Nema dostupnih igrača.</p>';
        return;
    }

    list.innerHTML = players.map(p => {
        const tooExp   = p.price > budget;
        const clubFull = (clubCount[p.team_name] || 0) >= 3 && p.team_name !== MY_PLAYERS.find(mp => mp.player_id === selectedOutId)?.team_name;
        const disabled = tooExp || clubFull;
        const priceDiff = p.price - selectedOutPrice;
        const diffStr   = (priceDiff >= 0 ? '+' : '') + priceDiff.toFixed(1) + 'm';
        const diffClass = priceDiff > 0 ? 'text-danger' : 'text-gold';

        return `
        <div class="replacement-card ${disabled ? 'replacement-card--disabled' : ''}"
             ${disabled ? '' : `onclick="confirmTransfer(${p.player_id})"`}>
            <div class="replacement-card__avatar">${(p.first_name[0] + p.last_name[0]).toUpperCase()}</div>
            <div class="replacement-card__info">
                <p class="replacement-card__name">${p.first_name} ${p.last_name}</p>
                <p class="replacement-card__club">${p.team_short} · ${p.position}</p>
                ${tooExp ? '<span class="sidebar-card__reason">Nedovoljno sredstava</span>' : ''}
                ${clubFull ? '<span class="sidebar-card__reason">Maks. klub</span>' : ''}
            </div>
            <div class="replacement-card__stats">
                <span class="replacement-card__price ${tooExp ? 'text-danger' : 'text-gold'}">${p.price.toFixed(1)}m</span>
                <span class="replacement-card__pts ${diffClass}" style="font-size:11px;">${diffStr}</span>
                <span class="replacement-card__pts">${p.total_points} bod</span>
            </div>
        </div>`;
    }).join('');
}

async function confirmTransfer(playerInId) {
    if (!selectedOutId) return;

    const errEl  = document.getElementById('transfer-error');
    const succEl = document.getElementById('transfer-success');
    errEl.style.display  = 'none';
    succEl.style.display = 'none';

    try {
        const res  = await fetch('/fantasy/transfers', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ player_out_id: selectedOutId, player_in_id: playerInId }),
        });
        const data = await res.json();

        if (data.success) {
            succEl.textContent   = data.message;
            succEl.style.display = 'block';
            document.getElementById('replacements-panel').classList.remove('active');
            setTimeout(() => window.location.reload(), 1200);
        } else {
            errEl.textContent   = data.message;
            errEl.style.display = 'block';
        }
    } catch {
        errEl.textContent   = 'Greška pri komunikaciji sa serverom.';
        errEl.style.display = 'block';
    }
}