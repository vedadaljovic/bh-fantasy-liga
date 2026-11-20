async function publishArticle() {
    const title   = document.getElementById('n-title').value.trim();
    const content = document.getElementById('n-content').value.trim();
    if (!title || !content) { showMsg('Naslov i sadržaj su obavezni.', 'error'); return; }

    const res  = await fetch('/admin/news/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title,
            content,
            category:  document.getElementById('n-category').value,
            image_url: document.getElementById('n-image').value.trim(),
        }),
    });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

async function deleteArticle(id, title) {
    if (!confirm(`Obrisati vijest "${title}..."?`)) return;
    const res  = await fetch(`/admin/news/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

function resetNewsForm() {
    document.getElementById('n-title').value    = '';
    document.getElementById('n-content').value  = '';
    document.getElementById('n-image').value    = '';
    document.getElementById('n-category').value = 'Vijesti';
}

function showMsg(msg, type) {
    const el = document.getElementById('admin-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 4000);
}