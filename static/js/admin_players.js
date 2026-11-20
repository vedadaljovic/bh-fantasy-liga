function filterPlayers() {
    const search = document.getElementById('player-search').value.toLowerCase();
    const team   = document.getElementById('filter-team').value;
    const pos    = document.getElementById('filter-pos').value;
    let count = 0;

    document.querySelectorAll('.player-row').forEach(row => {
        const nameMatch = row.dataset.name.includes(search);
        const teamMatch = !team || row.dataset.team === team;
        const posMatch  = !pos  || row.dataset.pos  === pos;
        const show = nameMatch && teamMatch && posMatch;
        row.style.display = show ? '' : 'none';
        if (show) count++;
    });
    document.getElementById('player-count').textContent = `${count} igrača prikazano`;
}

function openEditPlayer(id, first, last, teamId, pos, price, available) {
    document.getElementById('edit-player-id').value = id;
    document.getElementById('p-first-name').value   = first;
    document.getElementById('p-last-name').value    = last;
    document.getElementById('p-team').value         = teamId;
    document.getElementById('p-position').value     = pos;
    document.getElementById('p-price').value        = price;
    document.getElementById('p-available').value    = available ? 'true' : 'false';
    document.getElementById('form-title').textContent     = 'Uredi igrača';
    document.getElementById('form-btn-label').textContent = 'Sačuvaj izmjene';
    document.getElementById('p-first-name').focus();
}

function resetPlayerForm() {
    document.getElementById('edit-player-id').value = '';
    document.getElementById('p-first-name').value   = '';
    document.getElementById('p-last-name').value    = '';
    document.getElementById('p-team').value         = '';
    document.getElementById('p-position').value     = '';
    document.getElementById('p-price').value        = '';
    document.getElementById('p-available').value    = 'true';
    document.getElementById('form-title').textContent     = 'Dodaj igrača';
    document.getElementById('form-btn-label').textContent = 'Dodaj igrača';
}

async function savePlayer() {
    const id = document.getElementById('edit-player-id').value;
    const payload = {
        first_name:   document.getElementById('p-first-name').value.trim(),
        last_name:    document.getElementById('p-last-name').value.trim(),
        team_id:      document.getElementById('p-team').value,
        position:     document.getElementById('p-position').value,
        price:        parseFloat(document.getElementById('p-price').value),
        is_available: document.getElementById('p-available').value === 'true',
    };

    const url = id ? `/admin/players/${id}/edit` : '/admin/players/add';
    const res  = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

async function deletePlayer(id, name) {
    if (!confirm(`Obrisati igrača "${name}"?`)) return;
    const res  = await fetch(`/admin/players/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

function showMsg(msg, type) {
    const el = document.getElementById('admin-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}