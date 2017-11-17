from random import randint
from scipy.stats import binom, expon
from collections import Counter  # remove import after AI logic is changed
import math

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


def bid_for_opp(opponent, current_bid, game, players):
    """Bidding process for AI."""
    #Get current bid for this AI by looking for most recent bid for the game
    #return none if there's no current bid
    current_die_roll = opponent.current_die_roll
    total_dice = get_total_dice(players)

    prob_map = get_prob_mapping(total_dice, current_die_roll)

    print opponent.name

    print "current bid die choice {}".format(current_bid.die_choice)
    print "current bid die count {}".format(current_bid.die_count)

    #check if should challenge (add exact later on)
    if opponent.to_challenge(current_bid, total_dice):
        return tuple(["Challenge", "Challenge"])
    if opponent.to_call_exact(current_bid, total_dice):
        return tuple(["Exact", "Exact"])

    choice = current_bid.die_choice
    count = current_bid.die_count

    # prob this bid will be good
    bid_prob = prob_map[choice][count]

    # prob challenge will work
    challenge_prob = int((1 - bid_prob)*100)

    #prob exact will work
    exact_prob = int((prob_map[choice][count] - prob_map[choice][count + 1])*100)

    print "challenge prob {}".format(challenge_prob)
    print "exact prob {}".format(exact_prob)

    # key: tuples of (die choice, die count) value: prob of occurrance
    options_map = {}

    for k in prob_map:
        for k2 in prob_map[k]:
            # never skip more than 2 bids
            if k > choice and k2 >= count and k2 < count + 2:
                options_map[tuple([k, k2])] = int(prob_map[k][k2] * 100)
            if k <= choice and k2 > count and k2 < count + 3:
                options_map[tuple([k, k2])] = int(prob_map[k][k2] * 100)

    print options_map

    #adjust map for lying factor
    #increase bottom die choices by factor
    #(not for skipping a die, just for bidding it)
    #for instance, if the player has no 2s and last bid was 5 4s, increase prob
    #(2, 5), but not (2, 6)
    missing_list = []
    for x in range(2, 6):
        if x not in opponent.current_die_roll:
            missing_list.append(x)

    for k in prob_map:
        if k in missing_list and k > choice:
            options_map[tuple([k, count])] = min(int(options_map[tuple([k, count])] * (1 + opponent.liar_factor)), 100)
        if k in missing_list and k <= choice:
            options_map[tuple([k, count + 1])] = min(int(options_map[tuple([k, count + 1])] * (1 + opponent.liar_factor)), 100)

    #adjust map for agg factor
    #increase chances for jumping a bid (for a die that the aggresser has)
    #follow an exponential distribution of mean .5 to bump up agg factor
    #i.e. (factor -> %): .1 -> 5%, .2 -> 9.5%, .5 -> 22%, .8 -> 33%, .9 -> 36%

    #mean of .5 is 1/lambda, so lambda is 2
    agg_factor = expon.cdf(opponent.aggressive_factor, 0, 2)

    for k in prob_map:
        if k not in missing_list and k > choice:
            options_map[tuple([k, count + 1])] = min(int(options_map[tuple([k, count + 1])] * (1 + agg_factor)), 100)
        if k not in missing_list and k <= choice:
            options_map[tuple([k, count + 2])] = min(int(options_map[tuple([k, count + 2])] * (1 + agg_factor)), 100)

    #for aggressive bidders, bump up probability of challenge and exact
    #by smaller factor
    challenge_prob = min(challenge_prob * (1 + agg_factor/2), 100)
    exact_prob = min(exact_prob * (1 + agg_factor/2), 100)

    #Add exact and challenge into the options
    options_map["(Challenge, Challenge)"] = challenge_prob
    options_map["(Exact, Exact)"] = exact_prob

    #adjust map for intel factor
    #eliminate the bottom choices based on intelligence (note these may not
    #necessarily be the worst choices, due to liar and agg factors, but are more
    #likely to be).
    #20% intel, 12 options, eliminate .20/.11 (round down) (or 0)
    #50% intel, 12 options, eliminate .50/.11 (round down) (or 4 options)
    #80% intel, 12 options, eliminate .80/.11 (round down) (or 7 options)
    number_to_remove = math.floor((opponent.intelligence_factor)/.11)
    print "number to remove {}".format(number_to_remove)

    #convert to a dictionary of probs, remove bottom probs
    prob_dictionary = {}

    for k in options_map:
        if options_map[k] in prob_dictionary.keys():
            prob_dictionary[options_map[k]].append(k)
        else:
            prob_dictionary[options_map[k]] = [k]

    print prob_dictionary

    num_removed = 0
    #check through keys of dictionary, if there are enough values to remove
    #remove them and update the num_removed count. else, exit and stop
    #removing values.
    for item in sorted(prob_dictionary):
        value = prob_dictionary[item]
        count = len(value)
        if count < (number_to_remove - num_removed):
            del prob_dictionary[item]
            num_removed += count
        else:
            break

    print prob_dictionary


    #choose random option from dictionary based on odds
    #get sum of all prob values of a dictionary
    sum_probs = 0
    for item in sorted(prob_dictionary):
        value = prob_dictionary[item]
        #value of the key * number of options = total value for that key
        sum_probs += (len(value) * int(item))

    print sum_probs

    random_prob = randint(0, sum_probs)

    print random_prob
    for item in sorted(prob_dictionary):
        value = prob_dictionary[item]


    # new_bid = tuple([die_choice, die_count])

    # return new_bid