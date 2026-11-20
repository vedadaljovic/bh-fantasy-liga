function showMsg(msg, type) {
    const el = document.getElementById('profile-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (type === 'success') setTimeout(() => el.style.display = 'none', 4000);
}

async function saveTeamName() {
    const name = document.getElementById('team-name-input').value.trim();
    const res  = await fetch('/user/update-team-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ team_name: name }),
    });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
}

async function changePassword() {
    const res = await fetch('/user/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            current_password: document.getElementById('current-password').value,
            new_password:     document.getElementById('new-password').value,
            confirm_password: document.getElementById('confirm-password').value,
        }),
    });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) {
        document.getElementById('current-password').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
    }
}

async function deleteAccount() {
    const password = document.getElementById('delete-password').value;
    if (!password) { showMsg('Unesite lozinku za potvrdu.', 'error'); return; }
    if (!confirm('Jeste li sigurni? Ova akcija je trajna i ne može se poništiti.')) return;

    const res  = await fetch('/user/delete-account', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
    });
    const data = await res.json();
    if (data.success) {
        window.location.href = data.redirect;
    } else {
        showMsg(data.message, 'error');
    }
}