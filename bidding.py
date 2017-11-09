from random import randint
from scipy.stats import binom

##functions
def get_prob_mapping(total_dice, current_die_roll):
    prob_mapping = {}
    for k in range(0, total_dice - len(current_die_roll) + 1):
        die_prob = float(1.0/3)  # die and 1 (wild) gives 2/6 chances, or 1/3
        #probability that there will be at least k dice (could be more)
        #cdf gives the cumulative density function (prob of k dice or less)
        #take 1 minus that number and get probability of more than that
        p_more_than_num = 1 - binom.cdf(k, total_dice, die_prob)
        #then add in the probability of exactly that number to get the prob of
        #k dice or more (using the probability mass function)
        p_num_or_more = p_more_than_num + binom.pmf(k, total_dice, die_prob)
        prob_mapping[k] = p_num_or_more

    #die count for current player's die roll are already given, need to factor
    #those into the calculation as given numbers. This returns a nested dict,
    #by die face value, with probabilities of every possible die count.
    prob_mapping_by_die = {}
    for die in range(2, 7):
        prob_mapping_by_die[die] = {}
        count = current_die_roll.count(die)
        for key in prob_mapping.keys():
            if count > key:
                #if count < key, fill in missing probabilities with 1 (since we
                #know there will be at least that many dice).
                prob_mapping_by_die[die][key] = 1
                prob_mapping_by_die[die][key + count] = prob_mapping[key]
            else:
                prob_mapping_by_die[die][key + count] = prob_mapping[key]
    return prob_mapping_by_die


# testing = get_prob_mapping(25, [6, 6, 3, 5, 4])
# print testing

# def next_turn(turn_marker, count):
#     """
#     Given the current turn, return the next turn.


#     Given the current turn, get the next turn. Return the index of the next
#     player/opponent's turn.
#     """
#     return (turn_marker + 1) % (count + 1)


# def get_current_bet(current_turn, previous_bet):
#     if current_turn == 0:
#         return player_turn(dice_rolls[current_turn], previous_bet, counts)
#     else:
#         return opponent_turn(dice_rolls[current_turn], previous_bet, counts)


# def player_turn(player_roll, current_bet):
#     """
#     Given the die that have been rolled, show the player the dice and ask them
#     for their bet. Return their bet as a tuple (die_choice, die_count).


#     Given the die that have been rolled, show the player the dice and ask them
#     for their bet. Return their bet as a tuple (die_count, die_choice).

#     Checks to make sure that a number was inputted, and that it is valid.
#     Gives player the option of resetting their bid if they don't like it.
#     """
#     current_bet = tuple((4, 5))  # for testing, (count, choice)
#     print "Here are the dice you rolled: {}".format(player_roll)
#     print "The current bid is for {} {}s.".format(current_bet[0], current_bet[1])
#     decision = raw_input("Enter 'B' to place a higher bid, 'C' to challenge, or 'E' for exact:\n")
#     while True:
#         if decision[0].lower() == 'c' or decision[0].lower() == 'e':
#             return [decision[0].lower(), current_bet]
#         elif decision[0].lower() != 'b':
#             decision = raw_input("Decision is not valid, please re-enter:\n")
#             continue
#         else:
#             while True:
#                 print "Enter in the dice face (from 2 to 6) you want to choose to bid on."
#                 print "Remember that 1s are wild (and count towards the number you select)."
#                 try:
#                     die_choice = int(raw_input("Enter the die number you want to bet on:\n"))
#                     while die_choice not in range(2, 7):
#                         die_choice = int(raw_input("You did not enter a number from 2, to 6, please try again: \n"))
#                     print "Please bet on the number of {}s you think all plays have (at a minimum).".format(die_choice)
#                     print "The number should be higher than {}, but not greater than the total dice available".format(5)  # this number is TBD, via a parameter that will need to be passed.
#                     die_count = int(raw_input("Enter your bet:\n"))
#                     while (die_count, die_choice) <= current_bet:
#                         print "You did not out bid the current bid, you need to bid more than {} {}s.".format(die_count, die_choice)
#                         die_count = int(raw_input("Enter a higher count: \n"))
#                     while die_count not in range(total_dice):
#                         die_count = int(raw_input("You did not enter a valid number: \n"))
#                     print "You bet that at least {} dice have a value of {} (or 1, the wild dice value).".format(die_count, die_choice)
#                     confirm = raw_input("Please enter C to confirm or R to reset.\n")
#                     if confirm[0].lower() == "r":
#                         continue
#                     else:
#                         break
#                 except ValueError:
#                     print "You need to enter in an integer, please try again!"
#             print "current bid {}, new bid dice count ({}, {})".format(current_bet, die_count, die_choice)  # remove later
#             return [decision, (die_count, die_choice)]


# def opponent_turn(opponent_roll, current_bet, counts):
#     current_bet = tuple((4, 5))  # for testing, (count, choice)
#     remaining_counts = get_counts_of_dice_except_opp(opponent_roll, counts)
#     # opponent_stats = get_opponent_stats(test, test, test, test)

# ##game
# count, difficulty = setup_game()
# num_opponents = count - 1

# #generates list of starting dice numbers for each player
# dice = [5] * count
# #random selection of who starts the game


# # for testing
# opponents = opponent_AI.make_opponents(num_opponents, difficulty)
# opponent_AI.print_opponents(opponents, num_opponents)

# # print "initial dice {}".format(dice)  # remove later
# # print "initial marker {}".format(initial_marker)  # remove later

# dice_rolls = roll_all_dice(dice)
# print "dice rolls {}".format(dice_rolls)
# total_dice = sum(list(dice))
# # print "Total dice {}".format(total_dice)
# # print "list of dice rolls {}".format(dice_rolls)
# counts = get_counts_of_dice(dice_rolls)
# print "dictionary of counts {}".format(counts)

# current_turn = next_turn(initial_marker, count)
# current_turn = 1  # for testing
# #print "next turn {}".format(current_turn) ## need to fix (should be baesd on who loses)

# previous_bet = (1, 1)  # initializing previous_bet (die, count)

# current_bet = get_current_bet(current_turn, previous_bet)
# current_turn = next_turn(initial_marker, count)

# # #die # selected
# # current_die_choice = None
# # #die # estimated count
# # current_die_count = None

# ##note need to handle when players are no longer in the game.









