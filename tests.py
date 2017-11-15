import unittest
from datetime import datetime


from server import app
from model import User, Game, AbstractPlayer, HumanPlayer, AIPlayer, BidHistory
from model import connect_to_db
from game_play import *
from bidding import *


def example_data():
    """Create example data for the test database."""
    dob = datetime.strptime('16Sep2012', '%d%b%Y')
    u = User(username='l@gmail.com', password='test', name='Test', date_of_birth=dob)
    g = Game(num_players=4, difficulty='h')
    g2 = Game(num_players=4, difficulty='e')
    db.session.add_all([u, g, g2])
    db.session.commit()
    p = HumanPlayer(name='Test', user_id=1, game_id=1, position=1)
    o_1 = AIPlayer(name="opponent_1", difficulty='h', game_id=1, position=2)
    o_2 = AIPlayer(name="opponent_2", difficulty='h', game_id=1, position=3)
    o_3 = AIPlayer(name="opponent_3", difficulty='h', game_id=1, position=4)
    p_2 = HumanPlayer(name='Test', user_id=1, game_id=2, position=1)
    o_1_2 = AIPlayer(name="opponent_1", difficulty='e', game_id=2, position=2)
    o_2_2 = AIPlayer(name="opponent_2", difficulty='e', game_id=2, position=3)
    o_3_2 = AIPlayer(name="opponent_3", difficulty='e', game_id=2, position=4)
    db.session.add_all([p, o_1, o_2, o_3, p_2, o_1_2, o_2_2, o_3_2])
    db.session.commit()
    # can't have bid history without knowing who is starting...
    # b = BidHistory(game_id=1, player_id=1, die_choice=5, die_count=5)


class GamePlayUnitTests(unittest.TestCase):
    """Testing functions from game_play.py file"""

    print "running unit tests for game play"

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app=app, uri="postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        self.players = AbstractPlayer.query.filter(AbstractPlayer.game_id == 1).all()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_roll_player_dice(self):
        """Test random function"""
        players_with_dice = roll_player_dice(self.players)
        #function returns key value pairs of player ids to die rolls.
        for player_id in players_with_dice.keys():
            sample_roll = players_with_dice[player_id]
            assert len(sample_roll) == 5
            assert max(sample_roll) <= 6
            assert min(sample_roll) >= 1

    def test_check_for_game_over(self):
        loser = self.players[0]
        winner = self.players[1]
        loser.die_count = 0

        assert check_for_game_over(loser, winner, 2)
        assert not check_for_game_over(loser, winner, 4)

    def test_get_counts_of_dice(self):

        self.players2 = AbstractPlayer.query.filter(AbstractPlayer.game_id == 2).all()
        self.players2[0].current_die_roll = [5, 5, 5, 5, 5]
        self.players2[1].current_die_roll = [1, 1, 2, 2, 2]
        self.players2[2].current_die_roll = [6, 6, 6, 6, 6]
        self.players2[3].current_die_roll = [3, 3, 3, 3, 3]

        counts = get_counts_of_dice(self.players2)

        assert counts.get(1, 0) == 2
        assert counts.get(2, 0) == 3
        assert counts.get(3, 0) == 5
        assert counts.get(4, 0) == 0
        assert counts.get(5, 0) == 5
        assert counts.get(6, 0) == 5

    def test_create_new_game(self):
        num_players = 4
        difficulty = 'm'
        username = 'l@gmail.com'
        new_game = create_new_game(num_players, difficulty, username)
        new_game_id = new_game.id
        players = AbstractPlayer.query.filter(AbstractPlayer.game_id == new_game_id).all()
        human = HumanPlayer.query.filter(HumanPlayer.game_id == new_game_id).all()
        comps = AIPlayer.query.filter(AIPlayer.game_id == new_game_id).all()
        user = User.query.filter(User.username == username).first()
        assert human[0].user_id == user.id
        assert len(human) == 1
        assert len(players) == num_players
        assert len(comps) == num_players - 1
        assert comps[0].liar_factor
        assert players[0].die_count == 5

    def test_get_total_dice(self):

        assert get_total_dice(self.players) == 20

    def test_get_players_in_game(self):

        assert get_players_in_game(1) == self.players

    def test_get_active_players_in_game(self):

        self.players2 = AbstractPlayer.query.filter(AbstractPlayer.game_id == 2).all()
        self.players2[0].final_place = 4
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0
        #one player (at index 0) should be out of the game
        assert get_active_players_in_game(2) == self.players2[1:]

    def test_get_inactive_players_positions(self):
        self.players2 = AbstractPlayer.query.filter(AbstractPlayer.game_id == 2).all()
        self.players2[0].final_place = 4
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0

        assert get_inactive_players_positions(2) == [self.players2[0].position]

    def test_get_current_turn_player(self):
        game = Game.query.filter(Game.id == 1).first()
        random_turn_marker = game.turn_marker
        next_player = AbstractPlayer.query.filter(AbstractPlayer.position == random_turn_marker).first()

        assert get_current_turn_player(game) == next_player

    def test_update_turn_marker(self):
        game = Game.query.filter(Game.id == 2).first()
        self.players2 = AbstractPlayer.query.filter(AbstractPlayer.game_id == 2).all()
        self.players2[0].final_place = 3
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0
        self.players2[1].final_place = 4
        self.players2[1].current_die_roll = []
        self.players2[1].die_count = 0

        #not setting turn marker here - no matter what it starts at, it should update to 3
        #next turn would be 1, but 1 is out, then 2, but 2 is out, go to 3 (index 2)
        assert update_turn_marker(game, losing_player=self.players2[0]) == 3
        #set turn marker to 4 for this case
        game.turn_marker = 4
        assert update_turn_marker(game) == 3
        #set turn marker to 3 to test usual case
        game.turn_marker = 3
        assert update_turn_marker(game) == 4


class BiddingUnitTests(unittest.TestCase):
    """Testing functions"""

    print "running unit tests for bidding"

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app=app, uri="postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        self.players = AbstractPlayer.query.filter(AbstractPlayer.game_id == 1).all()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_get_prob_mapping(self):

        #### to be fixed ###
        probs = {2: {0: 1.0, 1: 0.99996039787195767, 2: 0.99946537127142809, 3: 0.9964952116682505, 4: 0.98510959985607005, 5: 0.95379916737257431, 6: 0.88804725915723326, 7: 0.77846074546499799, 8: 0.62973619116839319, 9: 0.46242106758471335, 10: 0.30440122864457064, 11: 0.17798535749245717, 12: 0.091792718070562121, 13: 0.04151367840778962, 14: 0.016374158576403286, 15: 0.005600078648666326, 16: 0.0016495826751628524, 17: 0.00041505268344294455, 18: 8.8265332693646513e-05, 19: 1.5645921416012717e-05, 20: 2.2686614437946558e-06}, 3: {0: 1, 1: 1.0, 2: 0.99996039787195767, 3: 0.99946537127142809, 4: 0.9964952116682505, 5: 0.98510959985607005, 6: 0.95379916737257431, 7: 0.88804725915723326, 8: 0.77846074546499799, 9: 0.62973619116839319, 10: 0.46242106758471335, 11: 0.30440122864457064, 12: 0.17798535749245717, 13: 0.091792718070562121, 14: 0.04151367840778962, 15: 0.016374158576403286, 16: 0.005600078648666326, 17: 0.0016495826751628524, 18: 0.00041505268344294455, 19: 8.8265332693646513e-05, 20: 1.5645921416012717e-05, 21: 2.2686614437946558e-06}, 4: {0: 1, 1: 1.0, 2: 0.99996039787195767, 3: 0.99946537127142809, 4: 0.9964952116682505, 5: 0.98510959985607005, 6: 0.95379916737257431, 7: 0.88804725915723326, 8: 0.77846074546499799, 9: 0.62973619116839319, 10: 0.46242106758471335, 11: 0.30440122864457064, 12: 0.17798535749245717, 13: 0.091792718070562121, 14: 0.04151367840778962, 15: 0.016374158576403286, 16: 0.005600078648666326, 17: 0.0016495826751628524, 18: 0.00041505268344294455, 19: 8.8265332693646513e-05, 20: 1.5645921416012717e-05, 21: 2.2686614437946558e-06}, 5: {0: 1, 1: 1.0, 2: 0.99996039787195767, 3: 0.99946537127142809, 4: 0.9964952116682505, 5: 0.98510959985607005, 6: 0.95379916737257431, 7: 0.88804725915723326, 8: 0.77846074546499799, 9: 0.62973619116839319, 10: 0.46242106758471335, 11: 0.30440122864457064, 12: 0.17798535749245717, 13: 0.091792718070562121, 14: 0.04151367840778962, 15: 0.016374158576403286, 16: 0.005600078648666326, 17: 0.0016495826751628524, 18: 0.00041505268344294455, 19: 8.8265332693646513e-05, 20: 1.5645921416012717e-05, 21: 2.2686614437946558e-06}, 6: {0: 1, 1: 1, 2: 1.0, 3: 0.99996039787195767, 4: 0.99946537127142809, 5: 0.9964952116682505, 6: 0.98510959985607005, 7: 0.95379916737257431, 8: 0.88804725915723326, 9: 0.77846074546499799, 10: 0.62973619116839319, 11: 0.46242106758471335, 12: 0.30440122864457064, 13: 0.17798535749245717, 14: 0.091792718070562121, 15: 0.04151367840778962, 16: 0.016374158576403286, 17: 0.005600078648666326, 18: 0.0016495826751628524, 19: 0.00041505268344294455, 20: 8.8265332693646513e-05, 21: 1.5645921416012717e-05, 22: 2.2686614437946558e-06}}

        assert get_prob_mapping(25, [6, 6, 3, 5, 4]) == probs

    def test_get_next_turn(self):

        assert get_next_turn(4, 4) == 1
        assert get_next_turn(1, 4) == 2


class ModelUnitTests(unittest.TestCase):
    """Testing functions"""

    print "running unit tests for model"

    def setUp(self):

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app=app, uri="postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        self.players = AbstractPlayer.query.filter(AbstractPlayer.game_id == 1).all()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_get_total_dice(self):

        assert get_total_dice(self.players) == 20

    def test_get_players_in_game(self):

        assert get_players_in_game(1) == self.players


class ServerTests(unittest.TestCase):
    """Tests for my app."""

    print "running server tests"

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app=app, uri='postgresql:///testdb')

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def testHomepage(self):
        result = self.client.get("/")
        self.assertIn("Welcome to Liar's Dice!", result.data)

    def testInstructions(self):
        result = self.client.get("/instructions")
        self.assertIn("Initial Setup", result.data)

    def testRegister(self):
        result = self.client.get("/register")
        self.assertIn("Enter your email address", result.data)

    def testSignIn(self):
        result = self.client.get("/login")
        self.assertIn("Username (email)", result.data)

    def testHomepageNoLogin(self):
        result = self.client.get("/")
        self.assertIn("Sign In", result.data)
        self.assertIn("New User?", result.data)
        self.assertNotIn("Log Out", result.data)
        self.assertNotIn("Create New", result.data)

    def testHomepageLogin(self):
        login_info = {'username': 'l@gmail.com', 'password': 'test'}
        result = self.client.post("/signin", data=login_info,
                                  follow_redirects=True)
        self.assertNotIn("Sign In", result.data)
        self.assertNotIn("New User?", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Create New", result.data)

    def testHomepageSignUp(self):
        dob = dob = datetime.strptime('16Sep2012', '%d%b%Y')
        login_info = {'username': 'h@gmail.com', 'password': 'test', 'name': 'Tester', 'dob': dob}
        result = self.client.post("/signup", data=login_info,
                                  follow_redirects=True)
        self.assertNotIn("Sign In", result.data)
        self.assertNotIn("New User?", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Create New", result.data)
        self.assertIn("Congrats, Tester, you are now registered!", result.data)

    def testCreateGame(self):
        game_info = {'difficulty': 'h', 'num_players': 4}
        result = self.client.post("/creategame", data=game_info,
                                  follow_redirects=True)
        self.assertNotIn("Let's Play Liar's", result.data)


class DatabaseTests(unittest.TestCase):
    """Flask tests that use the database."""

    print "running database tests"

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database (uncomment when testing database)
        connect_to_db(app=app, uri='postgresql:///testdb')

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = 'l@gmail.com'

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def checkGamePage(self):
        """Check game page."""
        result = self.client.get("/game/1")
        self.assertIn("Let's Play Liar's Dice", result.data)
        self.assertIn("Bidding Action", result.data)

    def testLogOut(self):
        result = self.client.get("/logout", follow_redirects=True)
        self.assertIn("You have successfully logged out", result.data)
        self.assertNotIn("Create New", result.data)


if __name__ == "__main__":
    unittest.main()
