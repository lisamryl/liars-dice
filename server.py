from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

from model import User, Game, AbstractPlayer, Human, AI, db, connect_to_db


app = Flask(__name__)
# app.config['JSON_SORT_KEYS'] = False

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


def get_players_in_game(game_id):
    """Get player objects for all players associated with game_id."""

    return AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id).all()


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

    total_dice = 0
    for player in players:
        total_dice += player.die_count  # eventually change to sqlalchemy query (with sum)

    return render_template("play_game.html",
                           game=game,
                           players=players,
                           total_dice=total_dice)  # note eventually want the game to be played in the /game_id link


#AJAX routes
@app.route('/rolldice', methods=['POST'])
def roll_dice():
    game_id = request.form.get('game_id')
    print game_id
    """Get list of players by game id, and roll dice for all players."""
    players = get_players_in_game(game_id)

    for player in players:
        player.roll_dice()
        
    return jsonify(players)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
