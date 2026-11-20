function openEditTeam(id, name, short, logo) {
    document.getElementById('edit-team-id').value = id;
    document.getElementById('t-name').value  = name;
    document.getElementById('t-short').value = short;
    document.getElementById('t-logo').value  = logo;
    document.getElementById('t-name').focus();
}

function resetTeamForm() {
    document.getElementById('edit-team-id').value = '';
    document.getElementById('t-name').value  = '';
    document.getElementById('t-short').value = '';
    document.getElementById('t-logo').value  = '';
}

async function saveTeam() {
    const id = document.getElementById('edit-team-id').value;
    if (!id) { showMsg('Odaberite klub za uređivanje.', 'error'); return; }

    const res  = await fetch(`/admin/teams/${id}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name:       document.getElementById('t-name').value.trim(),
            short_name: document.getElementById('t-short').value.trim(),
            logo_url:   document.getElementById('t-logo').value.trim(),
        }),
    });
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