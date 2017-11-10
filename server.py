from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from model import User, Game, AbstractPlayer, Human, AI, BidHistory, db, connect_to_db
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


@app.route('/startbid.json', methods=['POST'])
def comp_bidding():
    """Start the bidding for a computer"""

    ### add while loop to keep processing turns...

    #if human, show form on front end and get bid information, if computer, calc
    #bid odds and determine resulting bid
    game_id = request.form.get('game_id')
    game = Game.query.filter(Game.id == game_id).first()
    # players = get_players_in_game(game_id)
    player = (AbstractPlayer
              .query
              .filter(AbstractPlayer.game_id == game_id,
                      AbstractPlayer.position == game.turn_marker)
              .first())

    bid = player.comp.bidding()
    print bid
    current_turn_player = get_name_of_current_turn_player(game)
    if bid == "Challenge" or bid == "Exact":
        requests = {'name': player.name,
                    'die_choice': bid,
                    'die_count': bid,
                    'player_turn': None,
                    'turn_marker': None}
    else:
        requests = {'name': player.name,
                    'die_choice': bid.die_choice,
                    'die_count': bid.die_count,
                    'turn_marker_name': current_turn_player.name,
                    'turn_marker': game.turn_marker}

    return jsonify(requests)


@app.route('/endturn', methods=['POST'])
def end_turn():
    """End the turn: remove bids from DB, check bid, remove a die, next turn."""
    pass

@app.route('/playerturn.json', methods=['POST'])
def player_turn():
    """When it's a human player turn, render form to complete bid."""
    die_choice = request.form.get('die_choice')
    die_count = request.form.get('die_count')
    game_id = request.form.get('game_id')

    player = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id,
                                         AbstractPlayer.position == 1).first()
    game = Game.query.filter(Game.id == game_id).first()
    #save bid ##make function
    new_bid = BidHistory(game_id, player.id, die_choice, die_count)
    db.session.add(new_bid)
    db.session.commit()

    #update turn marker ###make function
    game.turn_marker = 2  # player is always position 1
    game.last_saved = datetime.now()
    db.session.commit()
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
