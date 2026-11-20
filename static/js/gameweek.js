let currentFixtureId = null;
let liveRefreshInterval = null;

async function openMatch(fixtureId) {
    currentFixtureId = fixtureId;
    document.getElementById('match-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
    await loadMatchData(fixtureId);
}

async function loadMatchData(fixtureId) {
    try {
        const res  = await fetch(`/fantasy/match/${fixtureId}`);
        const data = await res.json();
        renderModal(data);

        if (data.is_live) {
            clearInterval(liveRefreshInterval);
            liveRefreshInterval = setInterval(() => loadMatchData(fixtureId), 60000);
        }
    } catch(e) {
        console.error('Could not load match data:', e);
    }
}

function renderModal(data) {
    document.getElementById('modal-home-name').textContent = data.home_team;
    document.getElementById('modal-away-name').textContent = data.away_team;

    const homeScore = data.home_score !== null ? data.home_score : '-';
    const awayScore = data.away_score !== null ? data.away_score : '-';
    document.getElementById('modal-score').textContent = `${homeScore} : ${awayScore}`;

    const statusEl = document.getElementById('modal-status');
    if (data.is_live) {
        statusEl.textContent = 'UŽIVO';
        statusEl.className = 'match-modal__status match-modal__status--live';
    } else if (data.is_finished) {
        statusEl.textContent = 'Završeno';
        statusEl.className = 'match-modal__status match-modal__status--finished';
    } else {
        statusEl.textContent = data.match_date || '';
        statusEl.className = 'match-modal__status';
    }

    //events
    const eventsList = document.getElementById('modal-events-list');
    if (data.events.length === 0) {
        eventsList.innerHTML = '<p class="text-muted" style="text-align:center;padding:24px;">Nema dostupnih događaja.</p>';
    } else {
        eventsList.innerHTML = data.events.map(ev => {
            const icon = ev.event_type === 'goal'   ? '<i class="fas fa-futbol" style="color:var(--gold)"></i>'
                       : ev.event_type === 'yellow' ? '<i class="fas fa-square" style="color:#f6c90e"></i>'
                       : ev.event_type === 'red'    ? '<i class="fas fa-square" style="color:#e53e3e"></i>'
                       : ev.event_type === 'sub'    ? '<i class="fas fa-right-left" style="color:#68d391"></i>'
                       : '<i class="fas fa-circle"></i>';

            const score = ev.score_home !== null
                ? `<span class="event-score">${ev.score_home}:${ev.score_away}</span>`
                : '';

            const isHome = ev.team_side === 'home';
            return `
            <div class="match-event ${isHome ? 'match-event--home' : 'match-event--away'}">
                ${isHome ? `
                    <div class="match-event__detail">
                        <span class="match-event__player">${ev.player || ''}</span>
                        ${ev.player2 ? `<span class="match-event__player2">${ev.player2}</span>` : ''}
                    </div>
                    ${score}
                    <div class="match-event__icon">${icon}</div>
                    <div class="match-event__minute">${ev.minute || ''}</div>
                ` : `
                    <div class="match-event__minute">${ev.minute || ''}</div>
                    <div class="match-event__icon">${icon}</div>
                    ${score}
                    <div class="match-event__detail">
                        <span class="match-event__player">${ev.player || ''}</span>
                        ${ev.player2 ? `<span class="match-event__player2">${ev.player2}</span>` : ''}
                    </div>
                `}
            </div>`;
        }).join('');
    }

    document.getElementById('lineup-home-label').textContent = data.home_team;
    document.getElementById('lineup-away-label').textContent = data.away_team;
    renderLineupPitch(data.lineups.home, data.lineups.away, data.home_team, data.away_team);
}

function showTab(tab) {
    document.getElementById('tab-events').style.display  = tab === 'events'  ? 'block' : 'none';
    document.getElementById('tab-lineups').style.display = tab === 'lineups' ? 'block' : 'none';
    document.querySelectorAll('.match-modal__tab').forEach((btn, i) => {
        btn.classList.toggle('active', (i === 0 && tab === 'events') || (i === 1 && tab === 'lineups'));
    });
}

function closeMatch(e) {
    if (e.target === document.getElementById('match-modal')) closeMatchBtn();
}

function closeMatchBtn() {
    document.getElementById('match-modal').style.display = 'none';
    document.body.style.overflow = '';
    clearInterval(liveRefreshInterval);
    currentFixtureId = null;
}

function renderLineupPitch(homePlayers, awayPlayers, homeTeam, awayTeam) {
    const pitch = document.getElementById('lineup-pitch');

    if (!homePlayers.length && !awayPlayers.length) {
        pitch.innerHTML = `
            <div style="position:absolute;inset:0;display:flex;flex-direction:column;
                        align-items:center;justify-content:center;gap:12px;">
                <i class="fas fa-users-slash" style="font-size:32px;color:rgba(255,255,255,0.3);"></i>
                <p style="color:rgba(255,255,255,0.5);font-size:13px;margin:0;text-align:center;">
                    Postave nisu dostupne za ovu utakmicu
                </p>
            </div>`;
        document.getElementById('lineup-subs').style.display = 'none';
        return;
    }

    function splitRows(players) {
        const s = players.filter(p => p.starting);
        return {
            gk:  s.slice(0, 1),
            def: s.slice(1, 5),
            mid: s.slice(5, 8),
            fwd: s.slice(8, 11),
        };
    }

    function playerBubble(p, side) {
        const capBadge = p.is_cap ? '<span class="lp-cap">C</span>' : '';
        return `
        <div class="lp-player lp-player--${side}">
            <div class="lp-player__circle">
                <span class="lp-player__num">${p.number || ''}</span>
                ${capBadge}
            </div>
            <span class="lp-player__name">${shortName(p.name)}</span>
        </div>`;
    }

    function colHtml(players, side) {
        return `<div class="lp-col">${players.map(p => playerBubble(p, side)).join('')}</div>`;
    }

    const home = splitRows(homePlayers);
    const away = splitRows(awayPlayers);

    //"postave" screen
    const pitchHTML = `
        <div class="lp-field">
            <div class="lp-half-field lp-half-field--home">
                ${colHtml(home.gk,  'home')}
                ${colHtml(home.def, 'home')}
                ${colHtml(home.mid, 'home')}
                ${colHtml(home.fwd, 'home')}
            </div>
            <div class="lp-half-field lp-half-field--away">
                ${colHtml(away.fwd, 'away')}
                ${colHtml(away.mid, 'away')}
                ${colHtml(away.def, 'away')}
                ${colHtml(away.gk,  'away')}
            </div>
        </div>
    `;

    pitch.querySelectorAll('.lp-field').forEach(r => r.remove());
    pitch.insertAdjacentHTML('beforeend', pitchHTML);

    //substitutes
    const homeSubs = homePlayers.filter(p => !p.starting);
    const awaySubs = awayPlayers.filter(p => !p.starting);
    const subsSection = document.getElementById('lineup-subs');

    if (homeSubs.length || awaySubs.length) {
        subsSection.style.display = 'block';
        document.getElementById('subs-home-title').textContent = homeTeam;
        document.getElementById('subs-away-title').textContent = awayTeam;
        const subItem = p => `<div class="sub-player">
            <span class="sub-player__num">${p.number || ''}</span>
            <span class="sub-player__name">${p.name}</span>
        </div>`;
        document.getElementById('subs-home').innerHTML = homeSubs.map(subItem).join('');
        document.getElementById('subs-away').innerHTML = awaySubs.map(subItem).join('');
    } else {
        subsSection.style.display = 'none';
    }
}

function shortName(name) {
    return name.length > 10 ? name.split(' ')[0] : name;
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMatchBtn(); });