def calculate_player_points(stats, position):
    points = 0

    # Minutes
    if stats['minutes_played'] >= 60:
        points += 2
    elif stats['minutes_played'] > 0:
        points += 1

    # Goals
    if position == 'GK':
        points += stats['goals'] * 10
    elif position == 'DEF':
        points += stats['goals'] * 7
    elif position == 'MID':
        points += stats['goals'] * 6
    elif position == 'FWD':
        points += stats['goals'] * 5

    # Assists
    if position in ('GK', 'DEF'):
        points += stats['assists'] * 5
    else:
        points += stats['assists'] * 4

    # Clean sheet
    if stats['minutes_played'] >= 60 and stats['clean_sheet']:
        if position == 'GK':
            points += 5
        elif position == 'DEF':
            points += 5
        elif position == 'MID':
            points += 2

    # Saves
    if position == 'GK':
        points += (stats['saves'] // 3) * 2

    # Red cards
    if stats['red_cards'] > 0:
        points -= 3

    return points


def calculate_fantasy_team_points(fantasy_players, gameweek_stats):
    total_points = 0

    captain = next((p for p in fantasy_players if p['is_captain']), None)
    vice_captain = next((p for p in fantasy_players if p['is_vice_captain']), None)

    captain_played = False
    if captain:
        captain_stats = gameweek_stats.get(captain['player_id'])
        if captain_stats and captain_stats['minutes_played'] > 0:
            captain_played = True

    vice_captain_played = False
    if vice_captain:
        vice_stats = gameweek_stats.get(vice_captain['player_id'])
        if vice_stats and vice_stats['minutes_played'] > 0:
            vice_captain_played = True

    for fp in fantasy_players:
        if not fp['is_starting']:
            continue

        player_id = fp['player_id']
        position = fp['position']
        stats = gameweek_stats.get(player_id)

        if not stats or stats['minutes_played'] == 0:
                continue

        player_points = calculate_player_points(stats, position)

        if fp['is_captain']:
            if captain_played:
                player_points *= 2
            else:
                player_points = 0

        elif fp['is_vice_captain']:
            if not captain_played:
                if vice_captain_played:
                    player_points *= 2
                else:
                    player_points = 0
        
        total_points += player_points

    return total_points