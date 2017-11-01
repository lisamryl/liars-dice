import numpy
from random import randint
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


################################################################################
#Model definitions


class User(db.Model):
    """User class"""

    __tablename__ = "user"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, password, fname, lname, email, date_of_birth):
        pass


class AbstractPlayer(object):
    """Abstract player object. Subclasses are: Human and AI"""

    __tablename__ = "player"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    position = db.Column(db.Integer)
    final_place = db.Column(db.Integer)
    #will need if no current die roll but die count
    die_count = db.Column(db.Integer)
    #if turn is in progress
    die_roll = db.Column()


    def __init__(self, name, player_type):
        self.name = name
        self.die_count = 5
        self.player_type = player_type

    def roll_dice(self):
        """
        Roll dice for player or opponent object  (based on the number of dice),
        and returns the roll as a list.


        Creates a list of rolled dice for the remaining dice of the object.
        Returns a list of the dice rolled (for instance, if there are 5 dice,
        it returns a roll of 5 dice, where each is a random number from 1-6).
        """
        roll = []
        for x in range(0, self.num_dice):
            roll.append(randint(1, 6))
        return roll


class HumanPlayer(AbstractPlayer):
    """Human player in the game (controlled by user)."""

    def __init__(self, name):
        return super(HumanPlayer, self).__init__(name, "human")


class AIPlayer(AbstractPlayer):
    "Opponent in the game (controlled by AI)"

    def __init__(self, name, difficulty):
        # set liar stats (based on normal dist, 12.5% ave, 2.5% var)
        self.liar_stats = min(max(numpy.random.normal(.125, .025), 0), 1)
        # set aggressive stats (based on normal dist, 40% ave, 14% var
        # plus additional mean bump for liar (aka. bigger liar, more aggression)
        self.aggressive_stats = min(max(numpy.random.normal(
            .4 + self.liar_stats, .14), 0), 1)
        # set intelligence stats (based on normal dist with mean
        # based on difficulty: E: 35%, M: 60%, H: 85%, less aggr. factor
        # (aka. more aggr, less intell)). Var is 3%.
        if difficulty == 'e':
            self.intelligence_mean = .35
        elif difficulty == 'm':
            self.intelligence_mean = .6
        else:
            self.intelligence_mean = .85
        self.intelligence_stats = min(max(numpy.random.normal(
            self.intelligence_mean - self.aggressive_stats/10, .03), 0), 1)

        # #for testing without numpy
        # self.liar_stats = .3
        # self.aggressive_stats = .4
        # self.intelligence_stats = .5
        # return super(AIPlayer, self).__init__(name, "AI")


def make_players(num_players, difficulty):
    """Make players from Player/Opponent class, based on player num and difficulty"""
    all_players = []

    #need to change name after buiding front end
    all_players.append(HumanPlayer("Test Name"))

    for i in range(1, num_players):
        all_players.append(AIPlayer("opponent_" + str(i), difficulty))

    return all_players


def print_players(players):
    """for testing"""

    for i in range(len(players)):
        print players[i].__dict__

##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///game'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    #connect to db and create all tables
    from server import app
    connect_to_db(app)
    print "Connected to DB."
    db.create_all()

    #### for testing ####
    m = make_players(5, 'e')
    print_players(m)
