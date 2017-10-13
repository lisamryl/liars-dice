import numpy


class Opponent(object):  # eventually make this a subclass
    "Opponent in the game"
    die_count = 5

    def __init__(self, difficulty, name):
        if difficulty == 'e':
            self.intelligence_mean = .35
        elif difficulty == 'm':
            self.intelligence_mean = .6
        else:
            self.intelligence_mean = .85
        self.liar_stats = min(max(numpy.random.normal(.125, .025), 0), 1)
        self.aggressive_stats = min(max(numpy.random.normal(.4 + self.liar_stats, .14), 0), 1)  # bigger liar -> bigger aggression
        self.intelligence_stats = min(max(numpy.random.normal(self.intelligence_mean - self.aggressive_stats/10, .03), 0), 1)  # more aggressive -> lower intel
        self.name = name

def make_opponents(num_players, difficulty):
    """Make opponents from Opponent class, based on # of opps and difficulty"""
    all_opponents = []

    for i in range(num_players):
        all_opponents.append(Opponent(difficulty, "opponent_" + str(i + 1)))

    return all_opponents


def print_opponents(opponents, num_players):
    """for testing"""

    for i in range(num_players):
        print opponents[i].name
        print opponents[i].liar_stats
        print opponents[i].aggressive_stats
        print opponents[i].intelligence_stats
        print opponents[i].die_count
