from random import randint
from scipy.stats import binom

# for a 6 sided die where 1 is wild, each die face value has a 1/3 probability
# for instance, for a 6, you can roll a 6 or 1 (or 2 of 6 die face values (1/3
#probability))
DIE_PROB = float(1.0/3)

# 6 sided die
DIE_MIN = 1
DIE_MAX = 6

WILD_DIE = 1  # 1 is wild
DIE_MIN_BID = 2  # 1s are wild and cannot be bid on


##functions
def get_prob_mapping(total_dice, current_die_roll):
    """Get the probability mapping for all outcomes given a die roll in a game.
    Args: total dice left in the game, current die roll for a player.
    Returns: a nested dictionary (keys: die face value, secondary keys:
        die counts, value: probability of outcome)

    Given the total number of dice in the game, and the current die roll
    of a player, get the probability mapping for every possible player bid (aka
    the probability that a bid will be successful if challenged, for each
    possibility)"""
    prob_mapping = {}
    for k in range(0, total_dice - len(current_die_roll) + 1):
        #probability that there will be at least k dice (could be more)
        #cdf gives the cumulative density function (prob of k dice or less)
        #take 1 minus that number and get probability of more than that
        p_more_than_num = 1 - binom.cdf(k, total_dice, DIE_PROB)
        #then add in the probability of exactly that number to get the prob of
        #k dice or more (using the probability mass function)
        p_num_or_more = p_more_than_num + binom.pmf(k, total_dice, DIE_PROB)
        prob_mapping[k] = p_num_or_more

    #die count for current player's die roll are already given, need to factor
    #those into the calculation as given numbers. This returns a nested dict,
    #by die face value, with probabilities of every possible die count.
    prob_mapping_by_die = {}
    for die in range(DIE_MIN_BID, DIE_MAX + 1):
        prob_mapping_by_die[die] = {}
        count = current_die_roll.count(die) + current_die_roll.count(WILD_DIE)
        for key in prob_mapping.keys():
            if count > key:
                #if count < key, fill in missing probabilities with 1 (since we
                #know there will be at least that many dice).
                prob_mapping_by_die[die][key] = 1
                prob_mapping_by_die[die][key + count] = prob_mapping[key]
            else:
                prob_mapping_by_die[die][key + count] = prob_mapping[key]
    return prob_mapping_by_die


def get_total_dice(players):
    """Get total # of dice left in the game.
    Arg: player objects (all player objects in the game)
    Returns the total number of dice the players have (int)."""
    total_dice = 0
    for player in players:
        total_dice += player.die_count  # eventually change to sqlalchemy query (with sum)
    return total_dice


# testing = get_prob_mapping(25, [6, 6, 3, 5, 4])
# print testing
# testing2 = get_prob_mapping(25, [6, 6, 3, 5, 1])
# print testing2
