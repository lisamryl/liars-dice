from datetime import datetime
from flask import flash

from model import User, Game, AbstractPlayer, HumanPlayer, AIPlayer, BidHistory, db
from bidding import get_total_dice, get_prob_mapping


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
    inactive_player_list = (AbstractPlayer
                            .query
                            .filter(AbstractPlayer.game_id == game_id,
                                    AbstractPlayer.final_place != None)
                            .order_by(AbstractPlayer.id)
                            .all())

    positions = [player.position for player in inactive_player_list]

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


###END TURN FUNCTIONS
def determine_loser_and_winner(game_id, bid_type, challenger,
                               last_bidder, counts, last_bid):
    """Return a tuple with the winner and loser from the last bid made for round.
    Also, flash messages to inform the user of the outcome.
    Args: game_id, bid_type, challenger object, last_bidder object,
    counts (dictionary of counts of each die value for all players),
    last_bid object.

    Shows flash messages informing the player of what was bid and if it
    was challenged or if exact was called (and which user made the call).
    Then flashes who was correct and what the outcome was (i.e. a die was lost).
    Returns the loser and winner player objects as a tuple"""
    messages = []
    #get actual count of die for the die chosen
    actual_die_count = counts.get(last_bid.die_choice, 0) + counts.get(1, 0)
    num_players = (AbstractPlayer
                   .query
                   .filter(AbstractPlayer.game_id == game_id)
                   .count())

    #flash who challenged/called exact, and what bid was challenged
    if bid_type == "challenge":
        messages.append(challenger.name.title() + " challenged the bid of " +
                        str(last_bid.die_count) + " " +
                        str(last_bid.die_choice) + "s.")
        messages.append("The correct bid was " + str(actual_die_count) +
                        " (or less) " + str(last_bid.die_choice) + "s.")
    else:
        messages.append(challenger.name.title() + " bid exact on " +
                        str(last_bid.die_count) + " " +
                        str(last_bid.die_choice) + "s.")
        messages.append("The correct bid was exactly " + str(actual_die_count) +
                        " " + str(last_bid.die_choice) + "s.")

    #determine winner and loser of the challenge/exact bid
    if actual_die_count < last_bid.die_count and bid_type == "challenge":
        #bid challenged, challenger wins
        last_bidder.die_count -= 1
        loser = last_bidder
        winner = challenger
        messages.append(challenger.name.title() + " was correct, so " +
                        loser.name.title() + " loses a die!")
    elif actual_die_count >= last_bid.die_count and bid_type == "challenge":
        #bid challenged, challenger loses
        challenger.die_count -= 1
        loser = challenger
        winner = last_bidder
        messages.append(challenger.name.title() + " was wrong and loses a die!")
    elif actual_die_count == last_bid.die_count and bid_type == "exact":
        #exact bidder wins
        #check if there is an extra die to give (total dice < starting dice)
        if sum(counts.values()) < num_players * 5:
            challenger.die_count += 1
            messages.append(challenger.name.title() +
                            " was correct and gains a die!")
        else:
            messages.append(challenger.name.title() +
                            " was correct, but there are no dice to gain!")
        loser = last_bidder
        winner = challenger
    else:
        messages.append(challenger.name.title() +
                        " was not correct and loses a die!")
        #exact bidder is wrong, loses a die
        challenger.die_count -= 1
        loser = challenger
        winner = last_bidder
    db.session.commit()

    round_results = tuple([loser, winner, messages])

    return round_results


def is_loser_out(loser):
    """Checks if loser is out of dice and flashes messages."""
    if loser.die_count == 0:
        return True
    return False


def check_for_game_over(loser, winner):
    """Check if player is done and update db, return true if game over.

    Given player objects for the person who lost the round and person who won
    the round, determine if the loser is out of the game, and if the winner won
    the entire game (aka no players remain). Update db with results"""
    game = Game.query.filter(Game.id == loser.game_id).first()
    p_query = AbstractPlayer.query.filter(AbstractPlayer.game_id == game.id)
    players = p_query.all()
    players_out_of_game = (p_query
                           .filter(AbstractPlayer.final_place != None)
                           .count())
    num_players = len(players)
    players_left = num_players - players_out_of_game
    if loser.die_count == 0:
        loser.final_place = players_left
        if loser.final_place == 2:
            #last_bidder won, assign final place as 1 and mark game as finished
            winner.final_place = 1
            game.is_finished = True
            db.session.commit()
            return True
    db.session.commit()
    return False


def get_bidding_result(game_id, bid_type):
    """Given game id and bid type, determine who won the bid and what happens."""
    game = Game.query.filter(Game.id == game_id).first()
    p_query = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id)
    players = p_query.all()
    human_player = p_query.filter(AbstractPlayer.position == 1).first()
    #determine number of players who are already out of the game (and have a final place)

    last_bid = (BidHistory.query
                          .filter(BidHistory.game_id == game_id)
                          .order_by(BidHistory.created_at.desc())
                          .first())
    # print "last bid {} {}".format(last_bid.die_choice, last_bid.die_count)
    challenger = p_query.filter(AbstractPlayer.position == game.turn_marker).first()
    last_bidder = p_query.filter(AbstractPlayer.id == last_bid.player_id).first()

    #pull the final bid that was challenged (or called exact on)
    counts = get_counts_of_dice(players)
    #sum of die bid on, plus wilds

    loser, winner, messages = determine_loser_and_winner(game.id,
                                                         bid_type,
                                                         challenger,
                                                         last_bidder,
                                                         counts,
                                                         last_bid)

    if is_loser_out(loser):
        messages.append(loser.name.title() + " is out of the game!")
        is_game_over = check_for_game_over(loser, winner)
        #database would now be updated, check if player is out
        did_human_lose = human_player.final_place
        if did_human_lose or is_game_over:
            print "got to game over"
            requests = {'game_id': game_id,
                        'bid': "game_over"}
            return requests

    next_player_position = update_turn_marker(game, loser)
    next_player = (AbstractPlayer
                   .query
                   .filter(AbstractPlayer.position == next_player_position)
                   .first())
    print messages
    requests = {'turn_marker_name': next_player.name,
                'turn_marker': game.turn_marker,
                'bid': bid_type,
                'game_id': game_id,
                'messages': messages}
    return requests


def get_player_probs(game_id, die_choice, die_count):
    """Return the probabilities of all possible actions for a player.
    Given a game id, and the current bid die choice and die count, determine
    the probability of a successful challenge, exact call. Also, give the
    probability of all possible bids a player can make.
    Return the prob_map dictionary"""
    human_player = (AbstractPlayer.query
                                  .filter(AbstractPlayer.game_id == game_id,
                                          AbstractPlayer.position == 1)
                                  .first())
    players = get_active_players_in_game(game_id)
    total_dice = get_total_dice(players)
    prob_map = get_prob_mapping(get_total_dice(players),
                                human_player.current_die_roll)
    print prob_map

    #get challenge and exact probs (before deleting keys)
    try:
        challenge_prob = 1 - prob_map[die_choice][die_count]
    except KeyError:
        #if it's not in the map, it's not a possible bid based on player's dice.
        challenge_prob = 1
    try:
        exact_prob = (prob_map[die_choice][die_count] -
                      prob_map[die_choice][die_count + 1])
    except KeyError:
        #if it's not in the map, it's not a possible bid based on player's dice.
        exact_prob = 0

    #only keep valid bids in the map for a player to choose from.
    for k in prob_map:
        if k > die_choice:
            #delete keys (where k <= choice) up to (not including)
            #the current die count (since those are not possible to bid on)
            for i in range(die_count):
                del prob_map[k][i]
            #delete keys for bigger numbers, which are less likely to be bid on
            for i in range(die_count + 2, total_dice):
                try:
                    del prob_map[k][i]
                #key may not exist
                except KeyError:
                    continue
        else:
            #delete keys (where k <= choice) up to and including
            #the current die count (since those are not possibl to bid on)
            for i in range(die_count + 1):
                del prob_map[k][i]
            #delete keys for bigger numbers, which are less likely to be bid on
            for i in range(die_count + 3, total_dice):
                try:
                    del prob_map[k][i]
                #key may not exist
                except KeyError:
                    continue

    #add challenge/exact probs to map
    prob_map['Challenge'] = {}
    prob_map['Exact'] = {}
    prob_map['Challenge']['Challenge'] = challenge_prob
    prob_map['Exact']['Exact'] = exact_prob

    print prob_map

    return prob_map
