from model import User, Game, AbstractPlayer, Human, AI, BidHistory, db


###functions
def get_counts_of_dice(players):
    """
    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary.


    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary of dice
    counts from 1 to 6 that have at least 1 die).
    """
    counts = {}
    for player in players:
        for item in player.die_count:
            counts[item] = counts.get(item, 0) + 1
    return counts


def create_new_game(num_players, difficulty, user_id):
    """Create new game, create players, and save to DB. Return new game object"""
    #Create new Game object
    new_game = Game(num_players=num_players, difficulty=difficulty)
    db.session.add(new_game)
    db.session.commit()

    game = Game.query.order_by('created_at desc').first()
    game_id = game.id
    #Create new Player object (based on signed in user information)
    user_info = User.query.filter(User.username == user_id).first()
    player = Human(user_info.name, user_info.id, game_id, 1)
    db.session.add(player)

    #Create new AI objects
    for i in range(1, num_players):
        AI_i = AI("opponent_" + str(i), difficulty, game_id, i + 1)  # eventually randomly generate an Opp name
        db.session.add(AI_i)
    db.session.commit()

    return game


def get_total_dice(players):
    """Get total # of dice left in the game."""
    total_dice = 0
    for player in players:
        total_dice += player.die_count  # eventually change to sqlalchemy query (with sum)
    return total_dice


def get_players_in_game(game_id):
    """Get player objects for all players associated with game_id."""

    return AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id).all()

def get_name_of_current_turn_player(game):
    """Given a game object, returns the player object of the current turn."""
    current_turn_player = (AbstractPlayer
                           .query
                           .filter(AbstractPlayer.position == game.turn_marker)
                           .first())
    return current_turn_player
