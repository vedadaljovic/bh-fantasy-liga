from dao import user_dao, fantasy_dao
from werkzeug.security import generate_password_hash


class UserService:

    @staticmethod
    def get_profile_data(user_id):
        user         = user_dao.get_user_by_id(user_id)
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)

        if not fantasy_team:
            return {
                'user':          user,
                'fantasy_team':  None,
                'captain':       None,
                'vice_captain':  None,
                'rank':          None,
                'gw_history':    [],
                'transfer_count': 0,
            }

        # Captain / vice captain
        rows    = fantasy_dao.get_team_players(fantasy_team.id)
        captain = vice_captain = None
        for ftp, player, team in rows:
            if ftp.is_captain:
                captain = player
            if ftp.is_vice_captain:
                vice_captain = player

        # Rank
        rank = fantasy_dao.get_team_rank(fantasy_team.id)

        # Gameweek history
        history_rows = fantasy_dao.get_team_gameweek_history(fantasy_team.id)
        gw_history = [
            {
                'gameweek_number': gw.number,
                'gameweek_name':   gw.name,
                'points':          ftg.points,
                'is_active':       gw.is_active,
            }
            for ftg, gw in history_rows
        ]

        # Total transfers made
        active_gw      = fantasy_dao.get_active_gameweek()
        transfer_count = 0
        if active_gw:
            transfer_count = fantasy_dao.count_transfers_this_gameweek(
                fantasy_team.id, active_gw.id
            )

        return {
            'user':           user,
            'fantasy_team':   fantasy_team,
            'captain':        captain,
            'vice_captain':   vice_captain,
            'rank':           rank,
            'gw_history':     gw_history,
            'transfer_count': transfer_count,
            'active_gameweek': active_gw,
        }

    @staticmethod
    def update_team_name(user_id, new_name):
        if not new_name or len(new_name.strip()) < 3:
            return False, "Naziv tima mora imati najmanje 3 karaktera"
        fantasy_team = fantasy_dao.get_fantasy_team_by_user(user_id)
        if not fantasy_team:
            return False, "Nemate fantasy tim"
        user_dao.update_team_name(fantasy_team, new_name.strip())
        return True, "Naziv tima uspješno promijenjen"

    @staticmethod
    def change_password(user_id, current_password, new_password, confirm_password):
        user = user_dao.get_user_by_id(user_id)
        if not user:
            return False, "Korisnik nije pronađen"
        if not user.check_password(current_password):
            return False, "Trenutna lozinka nije ispravna"
        if len(new_password) < 6:
            return False, "Nova lozinka mora imati najmanje 6 karaktera"
        if new_password != confirm_password:
            return False, "Lozinke se ne podudaraju"
        user_dao.update_password(user, generate_password_hash(new_password))
        return True, "Lozinka uspješno promijenjena"

    @staticmethod
    def delete_account(user_id, password):
        user = user_dao.get_user_by_id(user_id)
        if not user:
            return False, "Korisnik nije pronađen"
        if not user.check_password(password):
            return False, "Lozinka nije ispravna"
        user_dao.delete_user(user_id)
        return True, "Nalog uspješno obrisan"