from dao import fantasy_dao, player_dao

# Squad composition rules
SQUAD_SIZE = 15
POSITION_LIMITS = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
MAX_PER_CLUB = 3
BUDGET = 100.0
FREE_TRANSFERS = 2
TRANSFER_PENALTY = -2


class FantasyService:

    # ─────────────────────────────────────────────
    #  TEAM CREATION
    # ─────────────────────────────────────────────

    @staticmethod
    def create_team(user_id, team_name):
        if not team_name or len(team_name.strip()) < 3:
            return False, "Naziv tima mora imati najmanje 3 karaktera", None

        existing = fantasy_dao.get_fantasy_team_by_user(user_id)
        if existing:
            return False, "Već imate fantasy tim", None

        team = fantasy_dao.create_fantasy_team(user_id, team_name.strip())
        return True, "Tim uspješno kreiran", team

    # ─────────────────────────────────────────────
    #  MY TEAM
    # ─────────────────────────────────────────────

    @staticmethod
    def get_my_team(user_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim", None

        rows = fantasy_dao.get_team_players(fantasy_team.id)

        starting = []
        bench    = []
        captain = vice_captain = None

        for ftp, player, team in rows:
            entry = {
                'ftp_id':          ftp.id,
                'player_id':       player.id,
                'first_name':      player.first_name,
                'last_name':       player.last_name,
                'position':        player.position,
                'price':           float(player.price),
                'total_points':    player.total_points,
                'photo_url':       player.photo_url,
                'is_available':    player.is_available,
                'team_name':       team.name,
                'team_short':      team.short_name,
                'is_starting':     ftp.is_starting,
                'is_captain':      ftp.is_captain,
                'is_vice_captain': ftp.is_vice_captain,
                'bench_order':     ftp.bench_order,
            }
            if ftp.is_captain:
                captain = entry
            if ftp.is_vice_captain:
                vice_captain = entry
            if ftp.is_starting:
                starting.append(entry)
            else:
                bench.append(entry)

        active_gw = fantasy_dao.get_active_gameweek()
        gw_record = None
        if active_gw:
            gw_record = fantasy_dao.get_team_gameweek_record(fantasy_team.id, active_gw.id)

        def_count = sum(1 for p in starting if p['position'] == 'DEF')
        mid_count = sum(1 for p in starting if p['position'] == 'MID')
        fwd_count = sum(1 for p in starting if p['position'] == 'FWD')
        formation = f"{def_count}-{mid_count}-{fwd_count}"

        data = {
            'fantasy_team':    fantasy_team,
            'starting':        starting,
            'bench':           bench,
            'captain':         captain,
            'vice_captain':    vice_captain,
            'active_gameweek': active_gw,
            'gameweek_points': gw_record.points if gw_record else 0,
            'formation':       formation,
            'chip_used':       fantasy_team.chip_used,
            'triple_captain_used': fantasy_team.triple_captain_used,
            'bench_boost_used':    fantasy_team.bench_boost_used,
            'wildcard_used':       fantasy_team.wildcard_used,
        }
        return True, "OK", data

    # ─────────────────────────────────────────────
    #  PICK TEAM
    # ─────────────────────────────────────────────

    @staticmethod
    def save_squad(user_id, player_ids, captain_id, vice_captain_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"

        if len(player_ids) != SQUAD_SIZE:
            return False, f"Morate odabrati točno {SQUAD_SIZE} igrača"

        if len(set(player_ids)) != SQUAD_SIZE:
            return False, "Ne možete odabrati istog igrača dva puta"

        if captain_id not in player_ids:
            return False, "Kapiten mora biti u vašem timu"

        if vice_captain_id not in player_ids:
            return False, "Potkapiten mora biti u vašem timu"

        if captain_id == vice_captain_id:
            return False, "Kapiten i potkapiten moraju biti različiti igrači"

        players = {}
        for pid in player_ids:
            result = player_dao.get_player_by_id(pid)
            if not result:
                return False, f"Igrač s ID {pid} ne postoji"
            player, team = result
            if not player.is_available:
                return False, f"{player.first_name} {player.last_name} nije dostupan"
            players[pid] = (player, team)

        position_count = {}
        for player, _ in players.values():
            position_count[player.position] = position_count.get(player.position, 0) + 1

        for pos, limit in POSITION_LIMITS.items():
            if position_count.get(pos, 0) != limit:
                return False, f"Morate imati točno {limit} igrača na poziciji {pos}"

        club_count = {}
        for player, team in players.values():
            club_count[team.id] = club_count.get(team.id, 0) + 1
            if club_count[team.id] > MAX_PER_CLUB:
                return False, f"Ne možete imati više od {MAX_PER_CLUB} igrača iz {team.name}"

        total_cost = sum(float(p.price) for p, _ in players.values())
        if total_cost > BUDGET:
            return False, f"Prekoračili ste budžet. Cijena: {total_cost:.1f}m / {BUDGET}m"

        existing = fantasy_dao.get_team_players(fantasy_team.id)
        for ftp, _, _ in existing:
            fantasy_dao.remove_player_from_team(fantasy_team.id, ftp.player_id)

        for i, pid in enumerate(player_ids):
            is_starting  = i < 11
            bench_order  = (i - 11) if not is_starting else None
            fantasy_dao.add_player_to_team(
                fantasy_team_id=fantasy_team.id,
                player_id=pid,
                is_starting=is_starting,
                is_captain=(pid == captain_id),
                is_vice_captain=(pid == vice_captain_id),
                bench_order=bench_order
            )

        fantasy_dao.update_fantasy_team_budget(fantasy_team.id, round(BUDGET - total_cost, 1))

        return True, "Tim uspješno sačuvan"

    # ─────────────────────────────────────────────
    #  CAPTAIN
    # ─────────────────────────────────────────────

    @staticmethod
    def update_captain(user_id, captain_id, vice_captain_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"

        if captain_id == vice_captain_id:
            return False, "Kapiten i potkapiten moraju biti različiti igrači"

        if not fantasy_dao.player_already_in_team(fantasy_team.id, captain_id):
            return False, "Kapiten nije u vašem timu"

        if not fantasy_dao.player_already_in_team(fantasy_team.id, vice_captain_id):
            return False, "Potkapiten nije u vašem timu"

        fantasy_dao.set_captain(fantasy_team.id, captain_id, vice_captain_id)
        return True, "Kapiten ažuriran"

    # ─────────────────────────────────────────────
    #  TRANSFERS
    # ─────────────────────────────────────────────

    @staticmethod
    def make_transfer(user_id, player_out_id, player_in_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim", 0

        active_gw = fantasy_dao.get_active_gameweek()
        if not active_gw:
            return False, "Nema aktivnog kola", 0

        if not fantasy_dao.player_already_in_team(fantasy_team.id, player_out_id):
            return False, "Igrač kojeg želite prodati nije u vašem timu", 0

        if fantasy_dao.player_already_in_team(fantasy_team.id, player_in_id):
            return False, "Igrač kojeg želite kupiti već je u vašem timu", 0

        result = player_dao.get_player_by_id(player_in_id)
        if not result:
            return False, "Igrač ne postoji", 0
        player_in, team_in = result

        if not player_in.is_available:
            return False, f"{player_in.first_name} {player_in.last_name} nije dostupan", 0

        result_out = player_dao.get_player_by_id(player_out_id)
        if not result_out:
            return False, "Igrač kojeg prodajete ne postoji", 0
        player_out, _ = result_out

        if player_in.position != player_out.position:
            return False, "Igrači moraju biti iste pozicije", 0

        club_count = fantasy_dao.count_players_from_same_club(fantasy_team.id, team_in.id)
        result_out_team = player_dao.get_player_by_id(player_out_id)
        _, team_out = result_out_team
        if team_out.id != team_in.id and club_count >= MAX_PER_CLUB:
            return False, f"Već imate {MAX_PER_CLUB} igrača iz {team_in.name}", 0

        price_diff = float(player_in.price) - float(player_out.price)
        new_budget = float(fantasy_team.budget_remaining) - price_diff
        if new_budget < 0:
            return False, (
                f"Nedovoljno sredstava. Potrebno još: {abs(new_budget):.1f}m"
            ), 0

        transfers_made = fantasy_dao.count_transfers_this_gameweek(fantasy_team.id, active_gw.id)
        wildcard_active = fantasy_team.chip_used == 'wildcard'
        penalty = 0 if wildcard_active else (TRANSFER_PENALTY if transfers_made >= FREE_TRANSFERS else 0)

        rows = fantasy_dao.get_team_players(fantasy_team.id)
        out_ftp = next((ftp for ftp, p, _ in rows if p.id == player_out_id), None)
        is_starting    = out_ftp.is_starting    if out_ftp else True
        is_captain     = out_ftp.is_captain     if out_ftp else False
        is_vice_captain = out_ftp.is_vice_captain if out_ftp else False
        bench_order    = out_ftp.bench_order    if out_ftp else None

        fantasy_dao.remove_player_from_team(fantasy_team.id, player_out_id)
        fantasy_dao.add_player_to_team(
            fantasy_team_id=fantasy_team.id,
            player_id=player_in_id,
            is_starting=is_starting,
            is_captain=is_captain,
            is_vice_captain=is_vice_captain,
            bench_order=bench_order
        )
        fantasy_dao.record_transfer(fantasy_team.id, active_gw.id, player_out_id, player_in_id)
        fantasy_dao.update_fantasy_team_budget(fantasy_team.id, round(new_budget, 1))

        msg = "Transfer uspješan"
        if penalty < 0:
            msg += f" ({abs(penalty)} kaznena boda)"

        return True, msg, penalty

    @staticmethod
    def get_transfers_info(user_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim", None

        active_gw = fantasy_dao.get_active_gameweek()
        transfers_made = 0
        transfers_this_gw = []

        if active_gw:
            transfers_made = fantasy_dao.count_transfers_this_gameweek(
                fantasy_team.id, active_gw.id
            )
            transfers_this_gw = fantasy_dao.get_transfers_this_gameweek(
                fantasy_team.id, active_gw.id
            )

        wildcard_active = fantasy_team.chip_used == 'wildcard'
        free_left = 99 if wildcard_active else max(0, FREE_TRANSFERS - transfers_made)
        extra     = 0  if wildcard_active else max(0, transfers_made - FREE_TRANSFERS)

        rows = fantasy_dao.get_team_players(fantasy_team.id)
        my_squad = []
        for ftp, player, team in rows:
            my_squad.append({
                'player_id':       player.id,
                'first_name':      player.first_name,
                'last_name':       player.last_name,
                'position':        player.position,
                'price':           float(player.price),
                'total_points':    player.total_points,
                'team_name':       team.name,
                'team_short':      team.short_name,
                'is_starting':     ftp.is_starting,
                'is_captain':      ftp.is_captain,
                'is_vice_captain': ftp.is_vice_captain,
                'bench_order':     ftp.bench_order,
            })

        data = {
            'fantasy_team':        fantasy_team,
            'active_gameweek':     active_gw,
            'transfers_made':      transfers_made,
            'free_transfers_left': free_left,
            'extra_transfers':     extra,
            'penalty_points':      0 if fantasy_team.chip_used == 'wildcard' else extra * TRANSFER_PENALTY,
            'transfers_this_gw':   transfers_this_gw,
            'all_players':         my_squad,
        }
        return True, "OK", data

    # ─────────────────────────────────────────────
    #  PLAYERS LIST
    # ─────────────────────────────────────────────

    @staticmethod
    def get_all_players(position=None):
        if position:
            rows = player_dao.get_players_by_position(position)
        else:
            rows = player_dao.get_all_players()

        result = []
        for player, team in rows:
            stats = player_dao.get_player_season_stats(player.id)
            result.append({
                'player_id':    player.id,
                'first_name':   player.first_name,
                'last_name':    player.last_name,
                'position':     player.position,
                'price':        float(player.price),
                'total_points': player.total_points,
                'photo_url':    player.photo_url,
                'is_available': player.is_available,
                'team_name':    team.name,
                'team_short':   team.short_name,
                'goals':        stats['goals'],
                'assists':      stats['assists'],
                'minutes':      stats['minutes'],
                'clean_sheets': stats['clean_sheets'],
                'yellow_cards': stats['yellow_cards'],
                'red_cards':    stats['red_cards'],
            })
        return result

    # ─────────────────────────────────────────────
    #  LEADERBOARD
    # ─────────────────────────────────────────────

    @staticmethod
    def get_leaderboard(user_id=None, limit=50):
        rows = fantasy_dao.get_leaderboard(limit)
        leaderboard = []
        for i, (ft, user) in enumerate(rows, start=1):
            leaderboard.append({
                'rank':             i,
                'team_name':        ft.team_name,
                'username':         user.username,
                'total_points':     ft.total_points,
                'gameweek_points':  ft.gameweek_points,
                'is_current_user':  (user.id == user_id) if user_id else False,
            })

        my_rank = None
        if user_id:
            ft = fantasy_dao.get_fantasy_team_by_user(user_id)
            if ft:
                my_rank = fantasy_dao.get_team_rank(ft.id)

        return {
            'leaderboard': leaderboard,
            'my_rank':     my_rank,
        }

    # ─────────────────────────────────────────────
    #  GAMEWEEK VIEW
    # ─────────────────────────────────────────────

    @staticmethod
    def get_gameweek_data(user_id, gameweek_id=None):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim", None

        if gameweek_id:
            gw = fantasy_dao.get_gameweek_by_id(gameweek_id)
        else:
            gw = fantasy_dao.get_active_gameweek()

        if not gw:
            return False, "Kolo nije pronađeno", None

        gw_record = fantasy_dao.get_team_gameweek_record(fantasy_team.id, gw.id)
        history   = fantasy_dao.get_team_gameweek_history(fantasy_team.id)

        data = {
            'fantasy_team':    fantasy_team,
            'gameweek':        gw,
            'gameweek_points': gw_record.points if gw_record else 0,
            'history':         [
                {
                    'gameweek_number': g.number,
                    'gameweek_name':   g.name,
                    'points':          ftg.points,
                }
                for ftg, g in history
            ],
        }
        return True, "OK", data

    # ─────────────────────────────────────────────
    #  SUBSTITUTION
    # ─────────────────────────────────────────────

    @staticmethod
    def swap_players(user_id, player_a_id, player_b_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim", None

        # Fetch both players
        result_a = player_dao.get_player_by_id(player_a_id)
        result_b = player_dao.get_player_by_id(player_b_id)
        if not result_a or not result_b:
            return False, "Igrač nije pronađen", None

        player_a, _ = result_a
        player_b, _ = result_b

        if (player_a.position == 'GK') != (player_b.position == 'GK'):
            return False, "Golman se može zamijeniti samo s drugim golmanom", None

        rows = fantasy_dao.get_team_players(fantasy_team.id)
        entry_a = next((ftp for ftp, p, _ in rows if p.id == player_a_id), None)
        entry_b = next((ftp for ftp, p, _ in rows if p.id == player_b_id), None)

        if not entry_a or not entry_b:
            return False, "Igrači nisu u vašem timu", None

        a_starting    = entry_a.is_starting
        a_bench_order = entry_a.bench_order
        b_starting    = entry_b.is_starting
        b_bench_order = entry_b.bench_order

        fantasy_dao.update_player_role(
            fantasy_team.id, player_a_id,
            is_starting=b_starting, bench_order=b_bench_order
        )
        fantasy_dao.update_player_role(
            fantasy_team.id, player_b_id,
            is_starting=a_starting, bench_order=a_bench_order
        )

        new_rows = fantasy_dao.get_team_players(fantasy_team.id)
        def_count = sum(1 for ftp, p, _ in new_rows if ftp.is_starting and p.position == 'DEF')
        mid_count = sum(1 for ftp, p, _ in new_rows if ftp.is_starting and p.position == 'MID')
        fwd_count = sum(1 for ftp, p, _ in new_rows if ftp.is_starting and p.position == 'FWD')
        new_formation = f"{def_count}-{mid_count}-{fwd_count}"

        from models.database import FantasyTeam as FT
        FT.query.filter_by(id=fantasy_team.id).update({'formation': new_formation})
        from models.database import db
        db.session.commit()

        return True, "Zamjena uspješna", new_formation



    # ─────────────────────────────────────────────
    #  CHIPS
    # ─────────────────────────────────────────────

    @staticmethod
    def activate_chip(user_id, chip):
        from models.database import db, FantasyTeam
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"

        active_gw = fantasy_dao.get_active_gameweek()
        if not active_gw:
            return False, "Nema aktivnog kola"

        if fantasy_team.chip_used:
            return False, "Već imate aktivan čip u ovom kolu"

        already_used = {
            'triple_captain': fantasy_team.triple_captain_used,
            'bench_boost':    fantasy_team.bench_boost_used,
            'wildcard':       fantasy_team.wildcard_used,
        }
        if already_used.get(chip):
            names = {'triple_captain': 'Trostruki kapiten', 'bench_boost': 'Klupa boost', 'wildcard': 'Wildcard'}
            return False, f"{names[chip]} je već iskorišten u ovoj sezoni"

        fantasy_team.chip_used = chip
        db.session.commit()

        names = {'triple_captain': 'Trostruki kapiten', 'bench_boost': 'Klupa boost', 'wildcard': 'Wildcard'}
        return True, f"{names[chip]} aktiviran"

    @staticmethod
    def deactivate_chip(user_id):
        from models.database import db
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"

        if not fantasy_team.chip_used:
            return False, "Nemate aktivan čip"

        fantasy_team.chip_used = None
        db.session.commit()
        return True, "Čip deaktiviran"

    @staticmethod
    def set_captain(user_id, captain_id, vice_captain_id):
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"

        if captain_id == vice_captain_id:
            return False, "Kapiten i potkapiten moraju biti različiti igrači"

        if not fantasy_dao.player_already_in_team(fantasy_team.id, captain_id):
            return False, "Kapiten nije u vašem timu"

        if not fantasy_dao.player_already_in_team(fantasy_team.id, vice_captain_id):
            return False, "Potkapiten nije u vašem timu"

        fantasy_dao.set_captain(fantasy_team.id, captain_id, vice_captain_id)
        return True, "Kapiten ažuriran"