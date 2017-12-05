from selenium import webdriver
import unittest
from datetime import datetime

from server import app
from model import User, Game, AbstractPlayer, HumanPlayer, AIPlayer, BidHistory
from model import connect_to_db
from game_play import *
from bidding import *
import time


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


def log_user_in(self):
    """Log in the user while testing"""
    self.browser.get('http://localhost:5000/login')
    username = self.browser.find_element_by_id('username-login')
    username.send_keys("l@gmail.com")
    password = self.browser.find_element_by_id('password-login')
    password.send_keys("test")
    btn = self.browser.find_element_by_id('login-submit-button')
    btn.click()


class TestLiarsDice(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.PhantomJS()

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
        self.browser.quit()
        db.session.close()
        db.drop_all()

    def test_title(self):
        """Tests that the title is displayed properly."""
        self.browser.get('http://localhost:5000/')
        self.assertEqual(self.browser.title, "Play Liar's Dice")

    def test_instructions_modal(self):
        """Tests that the instructions modal loads properly."""
        self.browser.get('http://localhost:5000/')
        btn = self.browser.find_element_by_id('instructions-button')
        btn.click()
        time.sleep(1)
        result = self.browser.find_element_by_tag_name('html')
        self.assertIn("Initial Setup", result.text)

    def test_create_new_game_when_not_logged_in(self):
        """Tests that the create new game modal is hidden when not logged in."""
        self.browser.get('http://localhost:5000/')
        result = self.browser.find_element_by_tag_name('html')
        self.assertNotIn("Create New Liar's Dice Game", result.text)

    def test_check_page_after_login(self):
        """Tests that the create new game modal loads properly."""
        ## need to have user sign in to get this to work
        log_user_in(self)
        result = self.browser.find_element_by_tag_name('html')
        time.sleep(1)
        self.assertIn("Create New Liar's Dice Game", result.text)

    def test_check_create_new_game(self):
        """Tests that the create new game modal loads properly."""
        ## need to have user sign in to get this to work
        log_user_in(self)
        btn = self.browser.find_element_by_id('create-game-button')
        btn.click()
        time.sleep(1)
        result = self.browser.find_element_by_tag_name('html')
        self.assertIn("Please select a difficulty", result.text)

    def test_check_load_new_game(self):
        """Tests that the create new game modal loads properly."""
        ## need to have user sign in to get this to work
        log_user_in(self)
        btn = self.browser.find_element_by_id('load-inprogress-games')
        btn.click()
        time.sleep(1)
        result = self.browser.find_element_by_tag_name('html')
        self.assertIn("Game ", result.text)

    def test_check_create_new_game_load_game(self):
        """Tests that the create new game modal loads properly."""
        ## need to have user sign in to get this to work
        log_user_in(self)
        btn = self.browser.find_element_by_id('create-game-button')
        btn.click()
        time.sleep(1)
        difficulty = self.browser.find_element_by_id('testing-radio-button')
        difficulty.click()
        num_players = self.browser.find_element_by_id('testing-option-selection')
        num_players.click()

        btn = self.browser.find_element_by_id('submit-create-new')
        btn.click()
        time.sleep(1)
        result = self.browser.find_element_by_tag_name('html')
        self.assertIn("Let's Play Liar's Dice", result.text)

if __name__ == "__main__":
    unittest.main()
