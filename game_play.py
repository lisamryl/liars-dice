from datetime import datetime

from model import User, Game, AbstractPlayer, HumanPlayer, AIPlayer, BidHistory, db


###functions
def roll_player_dice(players):
    """For player objects, roll dice for each player and return player info
    Arg: player objects (all player objects in the game)
    Return dict of die rolls key: player id, value: list of dice rolled"""
    player_info = {}
    for player in players:
        player.roll_dice()
        player_info[player.id] = player.current_die_roll
    db.session.commit()

    return player_info


def check_for_game_over(loser, winner, players_left):
    """Check if player is done and update db, return true if game over.

    Given player objects for the person who lost the round and person who won
    the round, determine if the loser is out of the game, and if the winner won
    the entire game (aka no players remain). Update db with results"""
    game = Game.query.filter(Game.id == loser.game_id).first()
    if loser.die_count == 0:
        loser.final_place = players_left
        if loser.final_place == 2:
            #last_bidder won, assign final place as 1
            winner.final_place == 1
            game.is_finished = True
            db.session.commit()
            return True
    db.session.commit()
    return False


def get_counts_of_dice(players):
    """
    Count the number of times each die number appears in player die rolls.
    Arg: player objects (all player objects in the game)
    Return: dict of counts of each die face value in player rolls.

    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary of dice
    counts from 1 to 6 that have at least 1 die).
    """
    counts = {}
    for player in players:
        for item in player.current_die_roll:
            counts[item] = counts.get(item, 0) + 1
    return counts


def create_new_game(num_players, difficulty, username):
    """Create new game, create players, and save to DB. Return new game obj.
    Args: number of players in game, difficulty, and username of player creating
    the game
    Returns the new game object"""
    #Create new Game object
    new_game = Game(num_players=num_players, difficulty=difficulty)
    db.session.add(new_game)
    db.session.commit()

    game_id = new_game.id

    #Create new Player object (based on signed in user information)
    user_info = User.query.filter(User.username == username).first()
    player = HumanPlayer(user_info.name, user_info.id, game_id, 1)
    db.session.add(player)

    #Create new AI objects
    for i in range(1, num_players):
        AI_i = AIPlayer("opponent_" + str(i), difficulty, game_id, i + 1)  # eventually randomly generate an Opp name
        db.session.add(AI_i)
    db.session.commit()

    return new_game


def get_total_dice(players):
    """Get total # of dice left in the game.
    Arg: player objects (all player objects in the game)
    Returns the total number of dice the players have (int)."""
    total_dice = 0
    for player in players:
        total_dice += player.die_count  # eventually change to sqlalchemy query (with sum)
    return total_dice


def get_players_in_game(game_id):
    """Get player objects for all players associated with game_id.
    Args: game id
    Returns: list of player objects for all players in that game."""

    return AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id).all()


def get_active_players_in_game(game_id):
    """Get player objects for all active players associated with game_id.
    Args: game id
    Returns: list of active player objects for all players in that game."""

    return (AbstractPlayer
            .query
            .filter(AbstractPlayer.game_id == game_id,
                    AbstractPlayer.final_place.is_(None))
            .order_by(AbstractPlayer.id)
            .all())


def get_inactive_players_positions(game_id):
    """Get player positions for all inactive players associated with game_id.
    Args: game id
    Returns: list of player positions for all players that are no longer active
    in that game."""
    positions = []
    inactive_player_list = (AbstractPlayer
                            .query
                            .filter(AbstractPlayer.game_id == game_id,
                                    AbstractPlayer.final_place != None)
                            .order_by(AbstractPlayer.id)
                            .all())

    for player in inactive_player_list:
        positions.append(player.position)

    return positions


def get_current_turn_player(game):
    """Given a game object, returns the player object of the current turn.
    Args: game object
    Returns: the player object of the player who's turn it is."""
    current_turn_player = (AbstractPlayer
                           .query
                           .filter(AbstractPlayer.position == game.turn_marker)
                           .first())
    return current_turn_player


def get_next_turn(turn_marker, num_players):
    """
    Given the current turn and the number of game players, return the next turn.

    Return the position of the next player's turn.
    """
    if turn_marker == num_players:
        return 1
    else:
        return turn_marker + 1


def update_turn_marker(game, losing_player=None):
    """Given current turn and game object, update marker for new player turn.
    Args: game object, optional losing player (in cases where the turn marker
        is getting updated after bidding took place)
    Returns: the position of the player who has the next turn."""
    positions_out_of_game = get_inactive_players_positions(game.id)
    all_players = get_players_in_game(game.id)
    if losing_player is None:
        next_turn = get_next_turn(game.turn_marker, len(all_players))
        game.turn_marker = next_turn
    else:
        game.turn_marker = losing_player.position
        next_turn = game.turn_marker
    while next_turn in positions_out_of_game:
        next_turn = get_next_turn(game.turn_marker, len(all_players))
        game.turn_marker = next_turn
    game.last_saved = datetime.now()
    db.session.commit()
    return next_turn