from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from model import User, Game, AbstractPlayer, HumanPlayer, AIPlayer, BidHistory
from model import db, connect_to_db
from game_play import *

app = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/register')
def register_form():
    """Prompts user to register"""

    return render_template("register.html")


@app.route('/instructions')
def instructions():
    """Provides the user instructions on how to play"""

    return render_template("instructions.html")


@app.route('/login')
def login():
    """Prompt user to log in"""

    return render_template("login.html")


@app.route('/logout')
def logout():
    """Logs a user out"""
    del session['user_id']
    flash("You have successfully logged out!")

    return redirect("/")


@app.route('/signin', methods=['POST'])
def signin():
    """Sign user in"""

    username = request.form.get('username')  # use email as username
    password = request.form.get('password')

    user = User.query.filter(User.username == username).first()

    if user:
        if user.password == password:
            session['user_id'] = username
            flash("You have successfully logged in!")
            return redirect('/')
        else:
            flash("That was not the correct password, please try again.")
            return redirect('/login')
    else:
        flash("No one is regiestered at this email, please create a new account.")
        return redirect('/register')


@app.route('/signup', methods=['POST'])
def signup():
    """Sign up new user"""

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    dob = request.form.get('dob')

    user = User.query.filter(User.username == username).first()

    #Check if username already exists, if so, redirect to signup. Else, register!
    if user:
        flash("You already have an account associated with that email. Please log in.")
        return redirect('/login')
    else:
        session['user_id'] = username
        new_user = User(username=username,
                        password=password,
                        name=name,
                        date_of_birth=dob)
        db.session.add(new_user)
        db.session.commit()
        flash("Congrats, " + name + ", you are now registered!")
        return redirect('/')


@app.route('/creategame')
def create_game():
    """Create a New Liar's Dice Game - prompt user for options"""

    return render_template("create_game.html")


@app.route('/game', methods=['POST'])
def setup_game():
    """Setup the liar's dice game and players, and render the game page."""

    num_players = int(request.form.get("num-players"))
    difficulty = request.form.get("difficulty")
    user_id = session['user_id']  # if none, don't allow saving...

    game = create_new_game(num_players, difficulty, user_id)

    url = '/game/{id}'.format(id=game.id)
    return redirect(url)


@app.route('/game/<game_id>')
def play_game(game_id):
    """Page for game play."""
    game = Game.query.filter(Game.id == game_id).first()
    players = get_players_in_game(game.id)
    total_dice = get_total_dice(players)
    current_turn_player = get_name_of_current_turn_player(game)

    #pass current bids into table on game page...
    bids = (BidHistory.query
                      .filter(BidHistory.game_id == game_id)
                      .order_by(BidHistory.id)
                      .all())

    return render_template("play_game.html",
                           game=game,
                           players=players,
                           total_dice=total_dice,
                           bids=bids,
                           current_turn_name=current_turn_player.name)


#AJAX routes
@app.route('/rolldice.json', methods=['POST'])
def roll_dice():
    """Get list of players by game id, and roll dice for all players."""
    game_id = request.form.get('game_id')
    players = get_players_in_game(game_id)
    player_info = {}
    for player in players:
        player.roll_dice()
        player_info[player.id] = player.current_die_roll

    return jsonify(player_info)


@app.route('/compturn.json', methods=['POST'])
def comp_bidding():
    """Start the bidding for a computer"""

    ### add while loop to keep processing turns...

    #if human, show form on front end and get bid information, if computer, calc
    #bid odds and determine resulting bid
    game_id = int(request.form.get('game_id'))
    game = Game.query.filter(Game.id == game_id).first()
    # players = get_players_in_game(game_id)
    player = (AbstractPlayer
              .query
              .filter(AbstractPlayer.game_id == game_id,
                      AbstractPlayer.position == game.turn_marker)
              .first())
    #have comp make a bid, save to db, and set turn marker
    bid = player.comp.bidding()
    current_turn_player = get_name_of_current_turn_player(game)
    if bid == "Challenge" or bid == "Exact":
        request_items = {'bid': bid, 'game_id': game_id}
        request_items = jsonify(request_items)
        url = '/endturn/' + bid + '/' + str(game_id) + '.json'
        print url ###need to fix this to be a post
        return redirect(url)
    else:
        update_turn_marker(game)
        requests = {'name': player.name,
                    'die_choice': bid.die_choice,
                    'die_count': bid.die_count,
                    'turn_marker_name': current_turn_player.name,
                    'turn_marker': game.turn_marker}
    return jsonify(requests)

###need to change method to post only, and edit redirected from the compturn section
@app.route('/endturn/<bid_type>/<game_id>.json', methods=['GET', 'POST'])
def end_turn(bid_type, game_id):
    """End the turn when challenged - check who won and adjust game accordingly.
    Remove bids from DB, check bid, remove a die, next turn."""
    # game_id = request.form.get('game_id')
    # bid_type = request.form.get('bid')
    game = Game.query.filter(Game.id == game_id).first()
    p_query = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id)
    players = p_query.all()
    #determine number of players who are already out of the game (and have a final place)
    players_out_of_game = p_query.filter(AbstractPlayer.final_place is None).count()
    num_players = len(players)
    players_left = num_players - players_out_of_game
    challenger = p_query.filter(AbstractPlayer.position == game.turn_marker).first()
    if challenger.position == 1:
        last_bidder_position = num_players
    else:
        last_bidder_position = challenger.position - 1
    last_bidder = (AbstractPlayer
                   .query
                   .filter(AbstractPlayer.game_id == game_id,
                           AbstractPlayer.position == last_bidder_position)
                   .first())
    #pull the final bid that was challenged (or called exact on)
    final_bid = (BidHistory.query
                           .filter(BidHistory.game_id == game_id,
                                   BidHistory.player_id == last_bidder.id)
                           .order_by(BidHistory.created_at.desc())
                           .first())
    counts = get_counts_of_dice(players)
    actual_die_count = counts.get(final_bid.die_choice, 0)

    if bid_type == 'challenge':
        if actual_die_count >= final_bid.die_count:
            #challenger wins, last bidder loses a die
            # message = """{challenger} challenged the bid and was correct!
            # {last_bidder} loses a die""".format(challenger=challenger.name,
            #                                     last_bidder=last_bidder.name)
            last_bidder.die_count -= 1
            db.session.commit()
            is_game_over = check_for_game_over(loser=last_bidder,
                                               winner=challenger,
                                               players_left=players_left)
            next_player = update_turn_after_results(game=game,
                                                    losing_player=last_bidder)
        else:
            #challenger loses
            challenger.die_count -= 1
            db.session.commit()
            is_game_over = check_for_game_over(loser=challenger,
                                               winner=last_bidder,
                                               players_left=players_left)
            next_player = update_turn_after_results(game=game,
                                                    losing_player=challenger)
    else:
        if actual_die_count == final_bid.die_count:
            #exact bidder wins
            #check if there is an extra die to give (total dice < starting dice)
            if sum(counts.values()) < num_players * 5:
                flash(challenger.name + "gains a die!")
                challenger.die_count += 1
                db.session.commit()
            is_game_over = check_for_game_over(loser=last_bidder,
                                               winner=challenger,
                                               players_left=players_left)
            next_player = update_turn_after_results(game=game,
                                                    losing_player=last_bidder)
        else:
            #exact bidder is wrong, loses a die
            challenger.die_count -= 1
            db.session.commit()
            is_game_over = check_for_game_over(loser=challenger,
                                               winner=last_bidder,
                                               players_left=players_left)
            next_player = update_turn_after_results(game=game,
                                                    losing_player=challenger)

    #Clear bid history after round
    BidHistory.query.filter(BidHistory.game_id == game_id).delete()
    db.session.commit()

    if is_game_over:
        human_player = p_query.filter(AbstractPlayer.position == 1).first()
        render_template("game_over.html", game=game, human_player=human_player)

    requests = {'turn_marker_name': next_player.name,
                'turn_marker': game.turn_marker}

    return requests

@app.route('/playerturn.json', methods=['POST'])
def player_turn():
    """When it's a human player turn, render form to complete bid."""
    die_choice = request.form.get('die_choice')
    die_count = request.form.get('die_count')
    game_id = request.form.get('game_id')

    player = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id,
                                         AbstractPlayer.position == 1).first()
    game = Game.query.filter(Game.id == game_id).first()
    #save bid ##make function?
    new_bid = BidHistory(game_id, player.id, die_choice, die_count)
    db.session.add(new_bid)
    db.session.commit()

    #update turn marker
    update_turn_marker(game)

    current_turn_player = get_name_of_current_turn_player(game)

    requests = {'name': player.name,
                'die_choice': die_choice,
                'die_count': die_count,
                'turn_marker': game.turn_marker,
                'turn_marker_name': current_turn_player.name}

    return jsonify(requests)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
