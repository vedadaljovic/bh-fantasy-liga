let selectedOut = null;

const myPlayers = {
    gk: [
        { id: 1, name: "Kenan Pirić", club: "ŽEL", price: "5.5m", points: 65 }
    ],
    def: [
        { id: 2, name: "Adnan Kovačević", club: "SAR", price: "6.0m", points: 72 },
        { id: 3, name: "Tarik Muharemović", club: "ZRI", price: "5.5m", points: 60 },
        { id: 4, name: "Haris Bećirović", club: "VEL", price: "5.0m", points: 48 },
        { id: 5, name: "Damir Šunjić", club: "BOA", price: "5.0m", points: 45 }
    ],
    mid: [
        { id: 6, name: "Emir Hadžić", club: "ŽEL", price: "7.0m", points: 84 },
        { id: 7, name: "Haris Handžić", club: "SAR", price: "6.5m", points: 71 },
        { id: 8, name: "Bojan Pavlović", club: "RAD", price: "5.5m", points: 55 },
        { id: 9, name: "Semir Štilić", club: "ŽEL", price: "6.0m", points: 62 },
        { id: 10, name: "Amar Rahimić", club: "VEL", price: "5.5m", points: 50 }
    ],
    fwd: [
        { id: 11, name: "Nemanja Bilbija", club: "BOA", price: "8.5m", points: 98 },
        { id: 12, name: "Damir Kojašević", club: "VEL", price: "7.5m", points: 79 },
        { id: 13, name: "Amer Dupovac", club: "RUD", price: "5.0m", points: 50 }
    ]
};

const availablePlayers = [
    { id: 101, name: "Ivan Lučić", club: "ŠIR", position: "GK", price: "5.0m", points: 58 },
    { id: 102, name: "Stipe Vukelja", club: "ZRI", position: "GK", price: "5.0m", points: 52 },
    { id: 103, name: "Đorđe Jovanović", club: "RAD", position: "DEF", price: "4.5m", points: 40 },
    { id: 104, name: "Kenan Karić", club: "TUZ", position: "DEF", price: "4.5m", points: 38 },
    { id: 105, name: "Anel Hebibović", club: "ŽEL", position: "MID", price: "6.0m", points: 66 },
    { id: 106, name: "Jasmin Mešanović", club: "BOA", position: "MID", price: "5.5m", points: 59 },
    { id: 107, name: "Elvedin Džinić", club: "SAR", position: "FWD", price: "6.5m", points: 70 },
    { id: 108, name: "Dženis Beganović", club: "VEL", position: "FWD", price: "6.0m", points: 64 },
];

function selectPlayerOut(playerId, playerName, position) {
    if (selectedOut && selectedOut.id === playerId) {
        selectedOut = null;
        document.querySelectorAll('.pitch-player').forEach(el => el.classList.remove('selected'));
        hideReplacements();
        return;
    }

    selectedOut = { id: playerId, name: playerName, position: position };

    document.querySelectorAll('.pitch-player').forEach(el => el.classList.remove('selected'));
    document.getElementById('player-' + playerId).classList.add('selected');

    showReplacements(position);
}

function showReplacements(position) {
    const panel = document.getElementById('replacements-panel');
    const list = document.getElementById('replacements-list');
    const title = document.getElementById('replacements-title');

    const posMap = { gk: 'GK', def: 'DEF', mid: 'MID', fwd: 'FWD' };
    const posLabel = posMap[position];

    title.textContent = 'Dostupni ' + posLabel + ' igrači';

    const filtered = availablePlayers.filter(p => p.position === posLabel);

    list.innerHTML = filtered.map(p => `
        <div class="replacement-card" onclick="confirmTransfer(${p.id}, '${p.name}')">
            <div class="replacement-card__avatar">${p.name.split(' ').map(n => n[0]).join('').slice(0,2)}</div>
            <div class="replacement-card__info">
                <p class="replacement-card__name">${p.name}</p>
                <p class="replacement-card__club">${p.club} · ${p.position}</p>
            </div>
            <div class="replacement-card__stats">
                <span class="replacement-card__price">${p.price}</span>
                <span class="replacement-card__points text-gold">${p.points} pts</span>
            </div>
        </div>
    `).join('');

    panel.classList.add('active');
}

function hideReplacements() {
    document.getElementById('replacements-panel').classList.remove('active');
}

function confirmTransfer(inId, inName) {
    if (!selectedOut) return;
    alert(`Transfer: ${selectedOut.name} → ${inName}`);
    hideReplacements();
    selectedOut = null;
    document.querySelectorAll('.pitch-player').forEach(el => el.classList.remove('selected'));
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('close-replacements').addEventListener('click', () => {
        hideReplacements();
        selectedOut = null;
        document.querySelectorAll('.pitch-player').forEach(el => el.classList.remove('selected'));
    });
});