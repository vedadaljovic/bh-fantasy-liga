let activeUserId = null;

async function loadUser(id) {
    activeUserId = id;
    document.querySelectorAll('.admin-user-row').forEach(r => r.classList.remove('selected'));
    document.querySelector(`.admin-user-row[onclick*="loadUser(${id})"]`)?.classList.add('selected');

    const res  = await fetch(`/admin/users/${id}`);
    const u    = await res.json();

    document.getElementById('user-detail-empty').style.display = 'none';
    document.getElementById('user-detail').style.display       = 'block';

    document.getElementById('detail-avatar').textContent     = u.username[0].toUpperCase();
    document.getElementById('detail-username').textContent   = u.username;
    document.getElementById('detail-email').textContent      = u.email;
    document.getElementById('detail-registered').textContent = u.created_at;
    document.getElementById('detail-team').textContent       = u.fantasy_team || 'Nema tima';
    document.getElementById('detail-points').textContent     = u.total_points;
    document.getElementById('detail-gw-points').textContent  = u.gw_points;

    const statusEl = document.getElementById('detail-status');
    statusEl.textContent = u.is_active ? 'Aktivan' : 'Deaktiviran';
    statusEl.className   = `badge badge--${u.is_active ? 'success' : 'danger'}`;

    const btn = document.getElementById('detail-toggle-btn');
    btn.textContent = u.is_active ? 'Deaktiviraj korisnika' : 'Aktiviraj korisnika';
    btn.className   = `btn ${u.is_active ? 'btn--danger' : 'btn--primary'}`;
}

async function toggleUser() {
    if (!activeUserId) return;
    const res  = await fetch(`/admin/users/${activeUserId}/toggle`, { method: 'POST' });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

async function deleteUser(id, username) {
    if (!confirm(`Obrisati korisnika "${username}"? Ovo će obrisati i njegov fantasy tim.`)) return;
    const res  = await fetch(`/admin/users/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

let currentTab = 'all';
function filterTab(tab, btn) {
    currentTab = tab;
    document.querySelectorAll('.admin-user-tab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterUsers();
}

function filterUsers() {
    const search = document.getElementById('user-search').value.toLowerCase();
    let count = 0;
    document.querySelectorAll('.admin-user-row').forEach(row => {
        const nameMatch   = row.dataset.name.includes(search);
        const statusMatch = currentTab === 'all' || row.dataset.status === currentTab;
        const show = nameMatch && statusMatch;
        row.style.display = show ? '' : 'none';
        if (show) count++;
    });
    document.getElementById('user-count').textContent = `${count} korisnika prikazano`;
}

function showMsg(msg, type) {
    const el = document.getElementById('admin-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}