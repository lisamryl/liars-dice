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
    g3 = Game(num_players=4, difficulty='e')
    db.session.add_all([u, g, g2, g3])
    db.session.commit()
    p = HumanPlayer(name='Test', user_id=1, game_id=1, position=1)
    o_1 = AIPlayer(name="opponent_1", difficulty='h', game_id=1, position=2)
    o_2 = AIPlayer(name="opponent_2", difficulty='h', game_id=1, position=3)
    o_3 = AIPlayer(name="opponent_3", difficulty='h', game_id=1, position=4)
    p_2 = HumanPlayer(name='Test', user_id=1, game_id=2, position=1)
    o_1_2 = AIPlayer(name="opponent_1", difficulty='e', game_id=2, position=2)
    o_2_2 = AIPlayer(name="opponent_2", difficulty='e', game_id=2, position=3)
    o_3_2 = AIPlayer(name="opponent_3", difficulty='e', game_id=2, position=4)
    p_3 = HumanPlayer(name='Test', user_id=1, game_id=3, position=1)
    o_1_3 = AIPlayer(name="opponent_1", difficulty='e', game_id=3, position=2)
    o_2_3 = AIPlayer(name="opponent_2", difficulty='e', game_id=3, position=3)
    o_3_3 = AIPlayer(name="opponent_3", difficulty='e', game_id=3, position=4)
    db.session.add_all([p, o_1, o_2, o_3, p_2, o_1_2, o_2_2, o_3_2, p_3, o_1_3, o_2_3, o_3_3])
    db.session.commit()
    # can't have bid history without knowing who is starting...
    # b = BidHistory(game_id=1, player_id=1, die_choice=5, die_count=5)


class GamePlayUnitTests(unittest.TestCase):
    """Testing functions from game_play.py file"""

    print "running unit tests for game play"

    def setUp(self):
        """Do at start of every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app=app, uri="postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        self.players = (AbstractPlayer
                        .query
                        .filter(AbstractPlayer.game_id == 1)
                        .all())
        self.players2 = (AbstractPlayer
                         .query
                         .filter(AbstractPlayer.game_id == 2)
                         .all())
        self.players3 = (AbstractPlayer
                         .query
                         .filter(AbstractPlayer.game_id == 3)
                         .all())

    def tearDown(self):
        """Do at end of every test."""
        db.session.close()
        db.drop_all()

    def test_roll_player_dice(self):
        """Test random die rolling function"""
        players_with_dice = roll_player_dice(self.players)
        #function returns key value pairs of player ids to die rolls.

        for player_id in players_with_dice.keys():
            sample_roll = players_with_dice[player_id]
            #die roll counts should all be 5 at the start of the game
            assert len(sample_roll) == 5
            #die rolls are random, ensure they are in the right range (1-6)
            assert max(sample_roll) <= 6
            assert min(sample_roll) >= 1

    def test_check_for_game_over_when_false(self):
        """Create a loser and winner; test what check_for_game_over returns."""
        loser = self.players3[0]
        winner = self.players3[1]
        loser.die_count = 0

        #with 4 players left, when someone loses and has 0 dice, return false,
        #game is still active (there's a separate check for if human is out).
        assert not check_for_game_over(loser, winner)

    def test_check_for_game_over_when_true(self):
        """Create a loser and winner; test what check_for_game_over returns."""
        loser = self.players3[0]
        winner = self.players3[1]
        loser.die_count = 0

        self.players3[2].die_count = 0
        self.players3[2].final_place = 4
        self.players3[3].die_choice = 0
        self.players3[3].final_place = 3
        #with 2 players left, when someone loses and has 0 dice, return true
        assert check_for_game_over(loser, winner)

    def test_get_counts_of_dice(self):
        """Create specific die rolls and check that counts sums correctly.
        Die rolls need to be created manually because they're random."""
        self.players2[0].current_die_roll = [5, 5, 5, 5, 5]
        self.players2[1].current_die_roll = [1, 1, 2, 2, 2]
        self.players2[2].current_die_roll = [6, 6, 6, 6, 6]
        self.players2[3].current_die_roll = [3, 3, 3, 3, 3]

        counts = get_counts_of_dice(self.players2)

        assert counts.get(1, 0) == 2
        assert counts.get(2, 0) == 3
        assert counts.get(3, 0) == 5
        #no 4s, should not be in the dictionary, return 0 with a get
        assert counts.get(4, 0) == 0
        assert counts.get(5, 0) == 5
        assert counts.get(6, 0) == 5

    def test_create_new_game(self):
        """Create new game, verify rows were properly created in db tables."""
        num_players = 4
        difficulty = 'm'
        username = 'l@gmail.com'
        new_game = create_new_game(num_players, difficulty, username)
        new_game_id = new_game.id
        players = (AbstractPlayer
                   .query
                   .filter(AbstractPlayer.game_id == new_game_id)
                   .all())
        human = (HumanPlayer
                 .query
                 .filter(HumanPlayer.game_id == new_game_id)
                 .all())
        comps = AIPlayer.query.filter(AIPlayer.game_id == new_game_id).all()
        user = User.query.filter(User.username == username).first()
        #HumanPlayer table check
        assert human[0].user_id == user.id
        assert len(human) == 1
        #AbstractPlayer table check
        assert len(players) == num_players
        assert players[0].die_count == 5
        #AIPlayer table check
        assert len(comps) == num_players - 1
        assert comps[0].liar_factor
        #Game table check
        assert new_game.difficulty == 'm'

    def test_get_total_dice(self):
        """Given players, test that the total dice function is correct."""
        assert get_total_dice(self.players) == 20

    def test_get_players_in_game(self):
        """Test that the player objects returns from function is correct."""
        assert get_players_in_game(1) == self.players

    def test_get_active_players_in_game(self):
        """Test that the player objects returns from function is correct."""
        #remove player at index 0 from the game - check that the active players
        #do not include this player
        self.players2[0].final_place = 4
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0
        #one player (at index 0) should be out of the game
        assert get_active_players_in_game(2) == self.players2[1:]

    def test_get_inactive_players_positions(self):
        """Test that inactive player positions are returned"""
        #remove player at index 0 from the game - check that the list has
        #this player's position
        self.players2[0].final_place = 4
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0

        assert get_inactive_players_positions(2) == [self.players2[0].position]

    def test_get_current_turn_player(self):
        """Test function to return the player who's turn it is."""
        game = Game.query.filter(Game.id == 1).first()
        #turn marker is random, capture it here to check it properly.
        random_turn_marker = game.turn_marker
        next_player = (AbstractPlayer
                       .query
                       .filter(AbstractPlayer.position == random_turn_marker)
                       .first())

        assert get_current_turn_player(game) == next_player

    def test_update_turn_marker(self):
        """Test update turn marker with edge cases"""
        #Set up game and edge cases
        game = Game.query.filter(Game.id == 2).first()
        self.players2[0].final_place = 3
        self.players2[0].current_die_roll = []
        self.players2[0].die_count = 0
        self.players2[1].final_place = 4
        self.players2[1].current_die_roll = []
        self.players2[1].die_count = 0

        #edge case where players are out of game, including player who just lost
        #not setting turn marker here - random start, it should update to 3
        #next turn would be 1, who's, then 2, who's out, go to 3 (at index 2)
        assert update_turn_marker(game, losing_player=self.players2[0]) == 3
        #set turn marker to 4 for this edge case (last player to player 1)
        game.turn_marker = 4
        assert update_turn_marker(game) == 3
        #set turn marker to 3 to test usual case
        game.turn_marker = 3
        assert update_turn_marker(game) == 4

    def test_get_next_turn(self):
        """Test get next turn function with edge case."""
        #if next turn position is the max position, return position 1
        #as next turn
        assert get_next_turn(4, 4) == 1
        #usual case, was player 1's turn, next turn is player 2.
        assert get_next_turn(1, 4) == 2


class BiddingUnitTests(unittest.TestCase):
    """Testing functions from bidding.py file"""

    print "running unit tests for bidding"


    def setUp(self):
        """Do at start of every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app=app, uri="postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        self.players = (AbstractPlayer
                        .query
                        .filter(AbstractPlayer.game_id == 1)
                        .all())
        self.players2 = (AbstractPlayer
                         .query
                         .filter(AbstractPlayer.game_id == 2)
                         .all())
        self.players3 = (AbstractPlayer
                         .query
                         .filter(AbstractPlayer.game_id == 3)
                         .all())

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.session.close()
        db.drop_all()

    def test_get_prob_mapping(self):
        """Test to ensure given strings are in the prob mapping for a roll."""
        # probs returns a nested dictionary, converting to a string then
        # testing edge cases
        probs = str(get_prob_mapping(25, [6, 6, 3, 5, 4]))
        # since there are already 2 6s, 0, 1, and 2 should be at 100% chance
        # also gives the prob of 21 5s (almost 0), 22 5s would not be possible
        # with the die roll so it's not shown in the dictionary).
        expected_str = '21: 2.2686614437946558e-06}, 6: {0: 1, 1: 1, 2: 1.0'
        # since there are no 2s in the die roll given,
        # 1 has a slightly less than 100% chance (but almost 100%)
        expected_str_2 = '{2: {0: 1.0, 1: 0.99996039787195767, 2: 0.99946537127'
        # since there is already 1 3, prob should be 100% for 1)
        expected_str_3 = '3: {0: 1, 1: 1.0, 2: 0.99996039787195767'

        self.assertIn(expected_str, probs)
        self.assertIn(expected_str_2, probs)
        self.assertIn(expected_str_3, probs)

        #edge case where a wild 1 is included (will count as 1 for 2-6)
        probs2 = str(get_prob_mapping(25, [6, 6, 3, 5, 1]))
        # since there are already 3 6s (because 1 is wild), 0-4 should be at
        # 100% chance.
        # also gives the prob of 22 5s (almost 0), 23 5s would not be possible
        # with the die roll so it's not shown in the dictionary).
        expected_str = '22: 2.2686614437946558e-06}, 6: {0: 1, 1: 1, 2: 1, 3: 1'
        # since there is one 2 (because the 1 is wild) in the die roll given,
        # 1 has 100% chance (2 has almost 100% chance)
        expected_str_2 = '{2: {0: 1, 1: 1.0, 2: 0.99996039787195767'
        # since there is already 2 3s (1 is wild), prob should be 100% for 0-2)
        expected_str_3 = '3: {0: 1, 1: 1, 2: 1.0, 3: 0.99996039787195767'

        self.assertIn(expected_str, probs2)
        self.assertIn(expected_str_2, probs2)
        self.assertIn(expected_str_3, probs2)

    def test_get_total_dice(self):

        assert get_total_dice(self.players) == 20

    def test_get_initial_turn_bid(self):
        """This will return a random die choice and count based on bidding
        algorithm. Need to check that the numbers returns (as a tuple) are
        valid options."""

        roll_player_dice(self.players)

        rand_opp = (AbstractPlayer
                    .query
                    .filter(AbstractPlayer.game_id == 1,
                            AbstractPlayer.position != 1)
                    .first())

        #random die choice should always be between 2 and 6, inclusive
        assert get_initial_turn_bid(rand_opp)[0] <= 6
        assert get_initial_turn_bid(rand_opp)[0] > 1
        #die count
        assert get_initial_turn_bid(rand_opp)[1] in (1,
                                                     rand_opp.die_count - 1,
                                                     rand_opp.die_count - 2,
                                                     rand_opp.die_count - 3)
        assert get_initial_turn_bid(rand_opp)[1] >= 1


class ServerTests(unittest.TestCase):
    """Tests for my app."""

    print "running server tests"

    def setUp(self):
        """Do at start of every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app=app, uri='postgresql:///testdb')

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""
        db.session.close()
        db.drop_all()

    def testHomepage(self):
        """Testing homepage."""
        result = self.client.get("/")
        self.assertIn("Welcome to Liar's Dice!", result.data)

    def testRegister(self):
        """Testing Registration page."""
        result = self.client.get("/register")
        self.assertIn("Enter your email address", result.data)

    def testSignIn(self):
        """Testing Login page."""
        result = self.client.get("/login")
        self.assertIn("Username (email)", result.data)

    def testHomepageNoLogin(self):
        """Testing homepage when not logged in."""
        result = self.client.get("/")
        self.assertIn("Sign In", result.data)
        self.assertIn("New User?", result.data)
        self.assertNotIn("Log Out", result.data)
        self.assertNotIn("Create New", result.data)

    def testHomepageLogin(self):
        """Testing homepage when logged in."""
        login_info = {'username': 'l@gmail.com', 'password': 'test'}
        result = self.client.post("/signin", data=login_info,
                                  follow_redirects=True)
        self.assertNotIn("Sign In", result.data)
        self.assertNotIn("New User?", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Create New", result.data)
        self.assertIn("You have successfully logged in", result.data)

    def testHomepageLoginBadPassword(self):
        """Testing homepage when logged in - incorrect pass."""
        login_info = {'username': 'l@gmail.com', 'password': 'test2'}
        result = self.client.post("/signin", data=login_info,
                                  follow_redirects=True)
        self.assertIn("Sign In", result.data)
        self.assertIn("New User?", result.data)
        self.assertNotIn("Log Out", result.data)
        self.assertIn("That was not the correct password", result.data)
        self.assertIn("Username (email)", result.data)

    def testHomepageLoginBadUsername(self):
        """Testing homepage when logged in - incorrect username."""
        login_info = {'username': 'k@gmail.com', 'password': 'test'}
        result = self.client.post("/signin", data=login_info,
                                  follow_redirects=True)
        self.assertIn("Sign In", result.data)
        self.assertIn("New User?", result.data)
        self.assertNotIn("Log Out", result.data)
        self.assertIn("No one is registered at this email", result.data)
        self.assertIn("Enter your email address", result.data)

    def testHomepageSignUp(self):
        """Testing signing up successfully."""
        dob = dob = datetime.strptime('16Sep2012', '%d%b%Y')
        login_info = {'username': 'h@gmail.com', 'password': 'test', 'name': 'Tester', 'dob': dob}
        result = self.client.post("/signup", data=login_info,
                                  follow_redirects=True)
        self.assertNotIn("Sign In", result.data)
        self.assertNotIn("New User?", result.data)
        self.assertIn("Log Out", result.data)
        self.assertIn("Create New", result.data)
        self.assertIn("Congrats, Tester, you are now registered!", result.data)

    def testHomepageSignUpUnsuccessfully(self):
        """Testing signing up successfully - user already signed up."""
        dob = dob = datetime.strptime('16Sep2012', '%d%b%Y')
        login_info = {'username': 'l@gmail.com', 'password': 'test', 'name': 'Test', 'dob': dob}
        result = self.client.post("/signup", data=login_info,
                                  follow_redirects=True)
        self.assertIn("Sign In", result.data)
        self.assertIn("New User?", result.data)
        self.assertNotIn("Log Out", result.data)
        self.assertNotIn("Create New", result.data)
        self.assertIn("You already have an account", result.data)


class ServerAjaxRouteTests(unittest.TestCase):
    """Tests for my server page AJAX calls."""

    print "running AJAX tests"

    def setUp(self):
        """Do at start of every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app=app, uri='postgresql:///testdb')

        # Create tables and add sample data
        db.create_all()
        example_data()

        self.game = Game.query.filter(Game.id == 1).first()
        #set turn marker so it's never the human player's turn
        self.game.turn_marker = 2

        self.players = (AbstractPlayer
                        .query
                        .filter(AbstractPlayer.game_id == 1)
                        .all())

        roll_player_dice(self.players)

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = 'l@gmail.com'

    def tearDown(self):
        """Do at end of every test."""
        db.session.close()
        db.drop_all()

    def testLoadGames(self):
        """Testing load games AJAX request."""
        result = self.client.get("/loadgames.json")
        self.assertIn("games", result.data)
        self.assertIn("1", result.data)
        self.assertNotIn("5", result.data)

    def testGameDetails(self):
        """Testing game details AJAX request."""
        request_data = {'game_id': 1}
        result = self.client.get("/game_details.json", query_string=request_data)
        self.assertIn('"total_dice": 20', result.data)

    def testCompTurn(self):
        """Testing computer turn AJAX request."""
        request_data = {'game_id': 1}
        result = self.client.post("/compturn.json", data=request_data)
        self.assertIn('"total_dice": 20', result.data)

    def testFinishTurn(self):
        """Testing finish turn AJAX request."""
        request_data = {'game_id': 1}
        result = self.client.post("/finishturn.json", data=request_data)
        self.assertIn('"1": [', result.data)


class DatabaseTests(unittest.TestCase):
    """Flask tests that use the database."""

    print "running database tests"

    def setUp(self):
        """Do at start of every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app=app, uri='postgresql:///testdb')

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as sess:
                sess['username'] = 'l@gmail.com'

    def tearDown(self):
        """Do at end of every test."""
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
