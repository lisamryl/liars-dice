import numpy
from scipy.stats import binom
from random import randint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from collections import Counter  # remove import after AI logic is changed

from bidding import get_prob_mapping, get_next_turn

db = SQLAlchemy()


################################################################################
#Model definitions

def get_total_dice(players):
    """Get total # of dice left in the game."""
    total_dice = 0
    for player in players:
        total_dice += player.die_count  # eventually change to sqlalchemy query (with sum)
    return total_dice


def get_players_in_game(game_id):
    """Get player objects for all players associated with game_id."""

    return AbstractPlayer.query.filter(AbstractPlayer.game_id == game_id).all()


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

    __tablename__ = "abstract_players"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    final_place = db.Column(db.Integer)
    #will need if no current die roll but die count
    die_count = db.Column(db.Integer, nullable=False)
    #if turn is in progress
    current_die_roll = db.Column(db.ARRAY(db.Integer))
    created_at = db.Column(db.DateTime, nullable=False)
    last_played = db.Column(db.DateTime, nullable=False)

    ## store most recent bid or a new table......

    game = db.relationship("Game", backref=db.backref("players"), order_by=position)

    def __init__(self, name, game_id, position):
        self.game_id = game_id
        self.name = name
        self.position = position
        self.final_place = None
        self.die_count = 5
        self.created_at = datetime.now()
        self.last_played = datetime.now()

    def roll_dice(self):
        """
        Roll dice for player or opponent object  (based on the number of dice),
        and returns the roll as a list.


        Creates a list of rolled dice for the remaining dice of the object.
        Stores list of dice rolled in the db (for instance, if there are 5 dice,
        it returns a roll of 5 dice, where each is a random number from 1-6).
        """
        roll = []
        for x in range(0, self.die_count):
            roll.append(randint(1, 6))
        self.current_die_roll = roll
        self.last_saved = datetime.now()
        db.session.commit()


class HumanPlayer(AbstractPlayer):
    """Human player in the game (controlled by user)."""

    __tablename__ = "humans"

    id = db.Column(db.Integer,
                   db.ForeignKey('abstract_players.id'),
                   primary_key=True)

    __table_args__ = {'extend_existing': True}

    #make nullable = true for users who don't log in
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", backref=db.backref("humans"), order_by=id)

    player = db.relationship("AbstractPlayer",
                             backref=db.backref("human", uselist=False),
                             order_by=id)

    def __init__(self, name, user_id, game_id, position):
        AbstractPlayer.__init__(self, name, game_id, position)
        self.user_id = user_id

    def __repr__(self):
        return '<id {} username {} die_count {} >'.format(
            self.id, self.user.username, self.players.die_count)


class AIPlayer(AbstractPlayer):
    """Opponent in the game (controlled by AI)"""

    __tablename__ = "computers"

    id = db.Column(db.Integer,
                   db.ForeignKey('abstract_players.id'),
                   primary_key=True)

    __table_args__ = {'extend_existing': True}

    player = db.relationship("AbstractPlayer",
                             backref=db.backref("comp", uselist=False),
                             order_by=id)

    liar_factor = db.Column(db.Float, nullable=False)
    aggressive_factor = db.Column(db.Float, nullable=False)
    intelligence_factor = db.Column(db.Float, nullable=False)

    def __init__(self, name, difficulty, game_id, position):
        AbstractPlayer.__init__(self, name, game_id, position)
        # set liar stats (based on normal dist, 12.5% ave, 2.5% var)
        self.liar_factor = round(min(max(numpy.random.normal(.125, .025),
                                         0), 1), 3)
        # set aggressive factor (based on normal dist, 40% ave, 14% var
        # plus additional mean bump for liar (aka. bigger liar, more aggression)
        self.aggressive_factor = round(min(max(numpy.random.normal(
            .4 + self.liar_factor, .14), 0), 1), 3)
        # set intelligence factor (based on normal dist with mean
        # based on difficulty: E: 35%, M: 60%, H: 85%, less aggr. factor
        # (aka. more aggr, less intell)). Var is 3%.
        if difficulty == 'e':
            self.intelligence_mean = .35
        elif difficulty == 'm':
            self.intelligence_mean = .6
        else:
            self.intelligence_mean = .85
        self.intelligence_factor = round(min(max(numpy.random.normal(
            self.intelligence_mean - self.aggressive_factor/10, .03), 0), 1), 3)

    def to_challenge(self, current_bid, total_dice):
        """Determine if AI should challenge the bid or not."""
        #logic change after MVP
        if current_bid is not None:
            prob_mapping = get_prob_mapping(total_dice, self.current_die_roll)
            if prob_mapping[current_bid.die_choice][current_bid.die_count] < 0.05:  # 5% for now
                return True
        return False

    def to_call_exact(self, current_bid, total_dice):
        """Determine if AI should call exact on the bid or not."""
        #logic change after MVP, for now, use false
        return False

    def bidding(self):
        """Bidding process for AI."""
        #Get current bid for this AI by looking for most recent bid for the game
        #return none if there's no current bid
        current_bid = (BidHistory.query
                                 .filter(BidHistory.game_id == self.game_id)
                                 .order_by(BidHistory.created_at.desc())
                                 .first())
        game = Game.query.filter(Game.id == self.game_id).first()
        players = get_players_in_game(self.game_id)

        current_die_roll = self.current_die_roll
        total_dice = get_total_dice(players)

        #check if should challenge (add exact later on)
        if self.to_challenge(current_bid, total_dice) is True:
            return "Challenge"
        if self.to_call_exact(current_bid, total_dice) is True:
            return "Exact"

        #note the below logic will change after MVP is complete!!!!!
        # syntax from Stack Overflow search
        count = Counter(current_die_roll)
        die_choice = max(current_die_roll, key=count.get)
        if die_choice == 1:
            die_choice = 2
        if current_bid is None:
            die_count = total_dice / len(players)
        else:
            die_count = current_bid.die_count + 1
        #end MVP logic

        #save bid
        new_bid = BidHistory(self.game_id, self.id, die_choice, die_count)
        db.session.add(new_bid)
        db.session.commit()

        return new_bid

    def __repr__(self):
        return '<id {} l stat {} a stat {} i stat {} die_count {} >'.format(
            self.id,
            self.liar_factor,
            self.aggressive_factor,
            self.intelligence_factor,
            self.player.die_count)


class BidHistory(db.Model):
    """Class for keeping track of current game bid history."""

    __tablename__ = "bids"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    player_id = db.Column(db.Integer,
                          db.ForeignKey('abstract_players.id'),
                          nullable=False)
    die_choice = db.Column(db.Integer, nullable=False)
    die_count = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    game = db.relationship("Game", backref=db.backref("bids"), order_by=id)
    player = db.relationship("AbstractPlayer", backref=db.backref("bids"), order_by=id)

    def __init__(self, game_id, player_id, die_choice, die_count):
        self.game_id = game_id
        self.player_id = player_id
        self.die_choice = die_choice
        self.die_count = die_count
        self.created_at = datetime.now()

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
