function showMsg(msg, type) {
    const el = document.getElementById('admin-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => el.style.display = 'none', 5000);
}

function setLoading(btn, loading) {
    btn.disabled = loading;
    btn.dataset.original = btn.dataset.original || btn.innerHTML;
    btn.innerHTML = loading
        ? '<i class="fas fa-spinner fa-spin"></i> Učitavanje...'
        : btn.dataset.original;
}

async function runScrapeNews() {
    const btn = document.getElementById('btn-scrape-news');
    if (!confirm('Pokrenuti scraper vijesti?')) return;
    setLoading(btn, true);
    const res  = await fetch('/admin/run/scrape-news', { method: 'POST' });
    const data = await res.json();
    setLoading(btn, false);
    showMsg(data.message, data.success ? 'success' : 'error');
}

async function runScrapeFixtures() {
    const btn = document.getElementById('btn-scrape-fixtures');
    if (!confirm('Pokrenuti scraper rasporeda? Ovo će ažurirati sve utakmice.')) return;
    setLoading(btn, true);
    const res  = await fetch('/admin/run/scrape-fixtures', { method: 'POST' });
    const data = await res.json();
    setLoading(btn, false);
    showMsg(data.message, data.success ? 'success' : 'error');
}

async function runScrapeLive() {
    const btn = document.getElementById('btn-scrape-live');
    if (!confirm('Pokrenuti live scraper? Ovo traje dok sve utakmice ne završe.')) return;
    setLoading(btn, true);
    const res  = await fetch('/admin/run/scrape-live', { method: 'POST' });
    const data = await res.json();
    setLoading(btn, false);
    showMsg(data.message, data.success ? 'success' : 'error');
}

async function runCalculatePoints() {
    const btn = document.getElementById('btn-calc-points');
    const gwId = document.getElementById('active-gw-id').value;
    if (!gwId) { showMsg('Nema aktivnog kola.', 'error'); return; }
    if (!confirm('Izračunati poene za aktivno kolo i zatvoriti ga?')) return;
    setLoading(btn, true);
    const res  = await fetch(`/admin/gameweeks/${gwId}/finish`, { method: 'POST' });
    const data = await res.json();
    setLoading(btn, false);
    showMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1500);
}