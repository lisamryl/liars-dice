import numpy
from random import randint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


################################################################################
#Model definitions


class User(db.Model):
    """User class"""

    __tablename__ = "users"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), nullable=False)  # username will be email
    password = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, password, name, date_of_birth):
        self.username = username
        self.password = password
        self.name = name
        self.date_of_birth = date_of_birth
        self.created_at = datetime.now()
        self.last_login = datetime.now()

    def __repr__(self):
        return '<id {} username {} created_at {} >'.format(
            self.id, self.username, self.created_at)


class Game(db.Model):
    """User class"""

    __tablename__ = "games"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    num_players = db.Column(db.Integer, nullable=False)
    turn_marker = db.Column(db.Integer, nullable=False)
    is_finished = db.Column(db.Boolean, nullable=False)
    #bid_history = db.Column(db.ARRAY)  ### note: check  with katie on this
    difficulty = db.Column(db.String(1), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_saved = db.Column(db.DateTime, nullable=False)

    def __init__(self, num_players, difficulty):
        self.num_players = num_players
        self.turn_marker = randint(1, num_players)
        self.is_finished = False
        self.difficulty = difficulty
        self.created_at = datetime.now()
        self.last_saved = datetime.now()

    def __repr__(self):
        return '<id {} turn_marker {} created_at {} >'.format(
            self.id, self.turn_marker, self.created_at)


class AbstractPlayer(db.Model):
    """Abstract player object. Subclasses are: Human and AI
    For DB, this table has a joined table inheritance with Human/AI tables
    link to details: http://docs.sqlalchemy.org/en/latest/orm/inheritance.html"""

    __tablename__ = "players"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    final_place = db.Column(db.Integer)
    #will need if no current die roll but die count
    die_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_played = db.Column(db.DateTime, nullable=False)

    #if turn is in progress
    #current_die_roll = db.Column(db.ARRAY(Integer)) ### note: check  with katie on this

    game = db.relationship("Game", backref=db.backref("players"))

    #For joined table inheritance
    # __mapper_args__ = {'polymorphic_identity': 'player', 'polymorphic_on': type}

    def __init__(self, name, player_type):
        self.name = name
        self.die_count = 5
        self.player_type = player_type
        self.created_at = datetime.now()
        self.last_played = datetime.now()

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


class Human(AbstractPlayer):
    """Human player in the game (controlled by user)."""

    __tablename__ = "humans"

    id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)

    # __mapper_args__ = {'polymorphic_identity': 'human'}
    __table_args__ = {'extend_existing': True}

    #make nullable = true for users who don't log in
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", backref=db.backref("humans"))

    def __init__(self, name):
        return super(Human, self).__init__(name, "human")

    def __repr__(self):
        # return '<id {} username {} die_count {} >'.format(
        #     self.id, self.user.username, self.players.die_count)
        return '<id {} >'.format(self.id)


class AI(AbstractPlayer):
    "Opponent in the game (controlled by AI)"

    __tablename__ = "computers"

    id = db.Column(db.Integer, db.ForeignKey('players.id'), primary_key=True)

    # __mapper_args__ = {'polymorphic_identity': 'computer'}
    __table_args__ = {'extend_existing': True}

    liar_factor = db.Column(db.Float, nullable=False)
    aggressive_factor = db.Column(db.Float, nullable=False)
    intelligence_factor = db.Column(db.Float, nullable=False)

    def __init__(self, name, difficulty):
        # set liar stats (based on normal dist, 12.5% ave, 2.5% var)
        self.liar_factor = min(max(numpy.random.normal(.125, .025), 0), 1)
        # set aggressive factor (based on normal dist, 40% ave, 14% var
        # plus additional mean bump for liar (aka. bigger liar, more aggression)
        self.aggressive_factor = min(max(numpy.random.normal(
            .4 + self.liar_factor, .14), 0), 1)
        # set intelligence factor (based on normal dist with mean
        # based on difficulty: E: 35%, M: 60%, H: 85%, less aggr. factor
        # (aka. more aggr, less intell)). Var is 3%.
        if difficulty == 'e':
            self.intelligence_mean = .35
        elif difficulty == 'm':
            self.intelligence_mean = .6
        else:
            self.intelligence_mean = .85
        self.intelligence_factor = min(max(numpy.random.normal(
            self.intelligence_mean - self.aggressive_factor/10, .03), 0), 1)

    def __repr__(self):
        return '<id {} l stat {} a stat {} i stat {} die_count {} >'.format(
            self.id,
            self.liar_factor,
            self.aggressive_factor,
            self.intelligence_factor,
            self.players.die_count)

        # #for testing without numpy
        # self.liar_factor = .3
        # self.aggressive_factor = .4
        # self.intelligence_factor = .5
        # return super(AI, self).__init__(name, "AI")


def make_players(num_players, difficulty):
    """Make players from Player/Opponent class, based on player num and difficulty"""
    all_players = []

    #need to change name after buiding front end
    all_players.append(Human("Test Name"))

    for i in range(1, num_players):
        all_players.append(AI("opponent_" + str(i), difficulty))

    return all_players

##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///liarsdice'
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
    # m = make_players(5, 'e')
    # a = Human('a')
    # b = Human('b')
    # c = Human('c')

    # d = AI('d', 'e')
    # e = AI('e', 'm')
    # f = AI('f', 'h')

    # db.session.add_all([a, b, c, d, e, f])
    # db.session.commit()
