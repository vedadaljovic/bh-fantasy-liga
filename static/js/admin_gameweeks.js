async function setActive(id, number) {
    if (!confirm(`Aktivirati Kolo ${number}?`)) return;
    const res  = await fetch(`/admin/gameweeks/${id}/set-active`, { method: 'POST' });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

async function finishGw(id, number) {
    if (!confirm(`Zatvoriti Kolo ${number}? Ovo će ga označiti kao završeno.`)) return;
    const res  = await fetch(`/admin/gameweeks/${id}/finish`, { method: 'POST' });
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