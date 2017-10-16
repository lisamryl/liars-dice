import numpy
from random import randint


class AbstractPlayer(object):
    """Abstract player object. Subclasses are: Human and AI"""

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


#### for testing ####
if __name__ == "__main__":
    m = make_players(5, 'e')
    print_players(m)
