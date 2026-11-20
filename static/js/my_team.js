function openChipGuide() {
    document.getElementById('chip-guide-modal').style.display = 'flex';
}

function closeChipGuide(e) {
    const modal = document.getElementById('chip-guide-modal');
    if (!e || e.target === modal) modal.style.display = 'none';
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeChipGuide();
});

function showChipMsg(msg, type) {
    const el = document.getElementById('chip-msg');
    el.className = `alert alert--${type}`;
    el.textContent = msg;
    el.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (type === 'success') setTimeout(() => el.style.display = 'none', 4000);
}

async function activateChip(chip) {
    const names = { triple_captain: 'Trostruki kapiten', bench_boost: 'Klupa boost', wildcard: 'Džoker' };
    if (!confirm(`Aktivirati ${names[chip]}? Možete ga poništiti prije zatvaranja kola.`)) return;

    const res  = await fetch('/fantasy/activate-chip', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ chip }),
    });
    const data = await res.json();
    showChipMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}

async function deactivateChip() {
    if (!confirm('Poništiti aktivan čip?')) return;

    const res  = await fetch('/fantasy/deactivate-chip', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    showChipMsg(data.message, data.success ? 'success' : 'error');
    if (data.success) setTimeout(() => location.reload(), 1000);
}