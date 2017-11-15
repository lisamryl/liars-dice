from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify, url_for)
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
    del session['username']
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
            session['username'] = username
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
        session['username'] = username
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
    username = session['username']  # if none, don't allow saving...

    game = create_new_game(num_players, difficulty, username)

    url = '/game/{id}'.format(id=game.id)
    return redirect(url)


@app.route('/game/<game_id>')
def play_game(game_id):
    """Page for game play."""
    game = Game.query.filter(Game.id == game_id).first()
    players = get_active_players_in_game(game.id)
    # if this is the first time the page ever loads, roll dice
    if players[0].current_die_roll is None and players[0].die_count == 5:
        roll_player_dice(players)

    print "game details: {}".format(game)
    total_dice = get_total_dice(players)
    current_turn_player = get_current_turn_player(game)

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


@app.route('/game_over/<game_id>')
def game_over(game_id):
    """Display end game to user"""
    print "enter end game route"
    game = Game.query.filter(Game.id == game_id).first()
    human_player = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id,
                                               AbstractPlayer.position == 1).first()
    return render_template("game_over.html", game=game, human_player=human_player)


#AJAX routes
@app.route('/rolldice.json', methods=['POST'])
def roll_dice():
    """Get list of players by game id, and roll dice for all players."""
    game_id = request.form.get('game_id')
    players = get_players_in_game(game_id)
    player_info = roll_player_dice(players)

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
    current_turn_player = get_current_turn_player(game)
    if bid == "Challenge" or bid == "Exact":
        request_items = {'bid': bid.lower(), 'game_id': game_id}
        return jsonify(request_items)
    else:
        update_turn_marker(game)
        requests = {'name': player.name,
                    'die_choice': bid.die_choice,
                    'die_count': bid.die_count,
                    'turn_marker_name': current_turn_player.name,
                    'turn_marker': game.turn_marker,
                    'game_id': game.id}
    return jsonify(requests)


@app.route('/endturn.json', methods=['POST'])
def end_turn():
    """End the turn when challenged - check who won and adjust game accordingly.
    Remove bids from DB, check bid, remove a die, next turn."""
    game_id = request.form.get('game_id')
    bid_type = request.form.get('bid')
    print "game id {}".format(game_id)
    print "bid type {}".format(bid_type)
    game = Game.query.filter(Game.id == game_id).first()
    p_query = AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id)
    players = p_query.all()
    human_player = p_query.filter(AbstractPlayer.position == 1).first()
    #determine number of players who are already out of the game (and have a final place)
    players_out_of_game = p_query.filter(AbstractPlayer.final_place != None).count()
    print "players out {}".format(players_out_of_game)
    num_players = len(players)
    players_left = num_players - players_out_of_game
    last_bid = (BidHistory.query
                          .filter(BidHistory.game_id == game_id)
                          .order_by(BidHistory.created_at.desc())
                          .first())
    print last_bid
    # print "last bid {} {}".format(last_bid.die_choice, last_bid.die_count)
    print "game turn marker {}".format(game.turn_marker)
    challenger = p_query.filter(AbstractPlayer.position == game.turn_marker).first()
    print "challenger {}".format(challenger)
    last_bidder = p_query.filter(AbstractPlayer.id == last_bid.player_id).first()
    print "last bidder {}".format(last_bidder)

    #pull the final bid that was challenged (or called exact on)
    counts = get_counts_of_dice(players)
    #sum of die bid on, plus wilds
    print "die choice {}".format(last_bid.die_choice)
    actual_die_count = counts.get(last_bid.die_choice, 0) + counts.get(1, 0)

    #make these "and" if statements (flat versus nested)
    if bid_type.lower() == 'challenge':
        print "actual count {}".format(actual_die_count)
        print "final bid count {}".format(last_bid.die_count)
        if actual_die_count < last_bid.die_count:
            print "challenger wins"
            #challenger wins, last bidder loses a die
            # message = """{challenger} challenged the bid and was correct!
            # {last_bidder} loses a die""".format(challenger=challenger.name,
            #                                     last_bidder=last_bidder.name)
            last_bidder.die_count -= 1
            loser = last_bidder
            winner = challenger
        else:
            print "challenger loses"
            #challenger loses
            challenger.die_count -= 1
            loser = challenger
            winner = last_bidder
    else:
        print "exacted"
        if actual_die_count == last_bid.die_count:
            print "exact correct"
            #exact bidder wins
            #check if there is an extra die to give (total dice < starting dice)
            if sum(counts.values()) < num_players * 5:
                challenger.die_count += 1
            loser = last_bidder
            winner = challenger

        else:
            print "exact incorrect"
            #exact bidder is wrong, loses a die
            challenger.die_count -= 1
            loser = challenger
            winner = last_bidder
    db.session.commit()
    print "loser {}".format(loser)
    print "winner {}".format(winner)
    is_game_over = check_for_game_over(loser, winner, players_left)
    next_player_position = update_turn_marker(game, loser)
    next_player = AbstractPlayer.query.filter(AbstractPlayer.position == next_player_position).first()
    did_human_lose = human_player.final_place
    print "did human lose: {}".format(did_human_lose)

    if did_human_lose or is_game_over:
        print "got to game over"
        # url = '/game_over/' + str(game_id)
        # print url
        # return redirect(url)
        requests = {'game_id': game_id,
                    'bid': "game_over"}
        return jsonify(requests)
    requests = {'turn_marker_name': next_player.name,
                'turn_marker': game.turn_marker,
                'bid': bid_type.lower(),
                'game_id': game_id}
    #Clear bid history after round
    BidHistory.query.filter(BidHistory.game_id == game_id).delete()
    roll_player_dice(players)
    db.session.commit()
    print requests
    return jsonify(requests)


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

    current_turn_player = get_current_turn_player(game)

    requests = {'name': player.name,
                'die_choice': die_choice,
                'die_count': die_count,
                'turn_marker': game.turn_marker,
                'turn_marker_name': current_turn_player.name,
                'game_id': game.id}

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
