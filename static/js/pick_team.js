const BUDGET = 100.0;
let remainingBudget = BUDGET;
let selectedPlayers = {};
let activeSlot = null;

const slots = {
    gk1: { pos: 'GK', player: null },
    gk2: { pos: 'GK', player: null },
    def1: { pos: 'DEF', player: null },
    def2: { pos: 'DEF', player: null },
    def3: { pos: 'DEF', player: null },
    def4: { pos: 'DEF', player: null },
    def5: { pos: 'DEF', player: null },
    mid1: { pos: 'MID', player: null },
    mid2: { pos: 'MID', player: null },
    mid3: { pos: 'MID', player: null },
    mid4: { pos: 'MID', player: null },
    mid5: { pos: 'MID', player: null },
    fwd1: { pos: 'FWD', player: null },
    fwd2: { pos: 'FWD', player: null },
    fwd3: { pos: 'FWD', player: null },
};

const availablePlayers = [
    { id: 1, name: "Kenan Pirić", club: "ŽEL", position: "GK", price: 5.5 },
    { id: 2, name: "Ivan Lučić", club: "ŠIR", position: "GK", price: 5.0 },
    { id: 3, name: "Stipe Vukelja", club: "ZRI", position: "GK", price: 5.0 },
    { id: 4, name: "Adnan Kovačević", club: "SAR", position: "DEF", price: 6.0 },
    { id: 5, name: "Tarik Muharemović", club: "ZRI", position: "DEF", price: 5.5 },
    { id: 6, name: "Haris Bećirović", club: "VEL", position: "DEF", price: 5.0 },
    { id: 7, name: "Damir Šunjić", club: "BOA", position: "DEF", price: 5.0 },
    { id: 8, name: "Đorđe Jovanović", club: "RAD", position: "DEF", price: 4.5 },
    { id: 9, name: "Kenan Karić", club: "TUZ", position: "DEF", price: 4.5 },
    { id: 10, name: "Emir Hadžić", club: "ŽEL", position: "MID", price: 7.0 },
    { id: 11, name: "Haris Handžić", club: "SAR", position: "MID", price: 6.5 },
    { id: 12, name: "Bojan Pavlović", club: "RAD", position: "MID", price: 5.5 },
    { id: 13, name: "Semir Štilić", club: "ŽEL", position: "MID", price: 6.0 },
    { id: 14, name: "Amar Rahimić", club: "VEL", position: "MID", price: 5.5 },
    { id: 15, name: "Anel Hebibović", club: "ŽEL", position: "MID", price: 6.0 },
    { id: 16, name: "Nemanja Bilbija", club: "BOA", position: "FWD", price: 8.5 },
    { id: 17, name: "Damir Kojašević", club: "VEL", position: "FWD", price: 7.5 },
    { id: 18, name: "Amer Dupovac", club: "RUD", position: "FWD", price: 5.0 },
    { id: 19, name: "Elvedin Džinić", club: "SAR", position: "FWD", price: 6.5 },
    { id: 20, name: "Dženis Beganović", club: "VEL", position: "FWD", price: 6.0 },
];

function selectSlot(slotKey) {
    activeSlot = slotKey;
    const pos = slots[slotKey].pos;

    document.querySelectorAll('.pitch-slot').forEach(s => s.classList.remove('active'));
    document.getElementById('slot-' + slotKey).classList.add('active');

    showAvailable(pos);
}

function showAvailable(pos) {
    const panel = document.getElementById('available-panel');
    const list = document.getElementById('available-list');
    const title = document.getElementById('available-title');

    title.textContent = 'Dostupni ' + pos + ' igrači';

    const alreadyPicked = Object.values(slots).filter(s => s.player).map(s => s.player.id);
    const filtered = availablePlayers.filter(p => p.position === pos && !alreadyPicked.includes(p.id));

    list.innerHTML = filtered.map(p => `
        <div class="replacement-card ${p.price > remainingBudget ? 'replacement-card--disabled' : ''}"
             onclick="${p.price <= remainingBudget ? `pickPlayer(${p.id})` : ''}">
            <div class="replacement-card__avatar">${p.name.split(' ').map(n => n[0]).join('').slice(0,2)}</div>
            <div class="replacement-card__info">
                <p class="replacement-card__name">${p.name}</p>
                <p class="replacement-card__club">${p.club} · ${p.position}</p>
            </div>
            <div class="replacement-card__stats">
                <span class="replacement-card__price ${p.price > remainingBudget ? 'text-danger' : 'text-gold'}">${p.price.toFixed(1)}m</span>
            </div>
        </div>
    `).join('');

    panel.classList.add('active');
}

function pickPlayer(playerId) {
    if (!activeSlot) return;

    const player = availablePlayers.find(p => p.id === playerId);
    if (!player) return;

    if (slots[activeSlot].player) {
        remainingBudget += slots[activeSlot].player.price;
    }

    slots[activeSlot].player = player;
    remainingBudget -= player.price;

    updateSlotUI(activeSlot, player);
    updateBudget();
    updateProgress();

    document.getElementById('available-panel').classList.remove('active');
    document.querySelectorAll('.pitch-slot').forEach(s => s.classList.remove('active'));
    activeSlot = null;
}

function removePlayer(slotKey) {
    if (!slots[slotKey].player) return;
    remainingBudget += slots[slotKey].player.price;
    slots[slotKey].player = null;
    resetSlotUI(slotKey);
    updateBudget();
    updateProgress();
}

function updateSlotUI(slotKey, player) {
    const el = document.getElementById('slot-' + slotKey);
    const initials = player.name.split(' ').map(n => n[0]).join('').slice(0, 2);
    el.innerHTML = `
        <div class="pitch-slot__avatar pitch-slot__avatar--filled">${initials}</div>
        <p class="pitch-slot__name">${player.name.split(' ').slice(-1)[0]}</p>
        <p class="pitch-slot__club">${player.club}</p>
        <p class="pitch-slot__price">${player.price.toFixed(1)}m</p>
        <button class="pitch-slot__remove" onclick="event.stopPropagation(); removePlayer('${slotKey}')">
            <i class="fas fa-times"></i>
        </button>
    `;
}

function resetSlotUI(slotKey) {
    const pos = slots[slotKey].pos;
    const el = document.getElementById('slot-' + slotKey);
    el.innerHTML = `
        <div class="pitch-slot__avatar">
            <i class="fas fa-plus"></i>
        </div>
        <p class="pitch-slot__pos">${pos}</p>
    `;
}

function updateBudget() {
    document.getElementById('remaining-budget').textContent = remainingBudget.toFixed(1) + 'm';
    document.getElementById('spent-budget').textContent = (BUDGET - remainingBudget).toFixed(1) + 'm';
}

function updateProgress() {
    const filled = Object.values(slots).filter(s => s.player).length;
    document.getElementById('progress-count').textContent = filled + ' / 15';
    document.getElementById('progress-bar-fill').style.width = (filled / 15 * 100) + '%';

    const saveBtn = document.getElementById('save-btn');
    if (filled === 15) {
        saveBtn.classList.remove('btn--ghost');
        saveBtn.classList.add('btn--primary');
        saveBtn.disabled = false;
    } else {
        saveBtn.classList.remove('btn--primary');
        saveBtn.classList.add('btn--ghost');
        saveBtn.disabled = true;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('close-available').addEventListener('click', () => {
        document.getElementById('available-panel').classList.remove('active');
        document.querySelectorAll('.pitch-slot').forEach(s => s.classList.remove('active'));
        activeSlot = null;
    });
});