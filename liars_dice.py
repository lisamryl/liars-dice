from random import randint

import opponent_AI

##input
print "Welcome to Liar's Dice!"
#add instructions


##functions
def setup_game():
    """
    Asks user for the number of players for the game and returns the number of
    players chosen. This sets up the initial game.

    Arg:
    None

    Return:
    Count of players chosen

    Asks player for the number of players from 2-6 (inclusive). If the player
    does not enter a number or enters a number that's out of range, error
    handing asks the user to try again. Returns the number of players selected.
    """
    print "What difficulty would you like to play at?"
    difficulty = raw_input("Easy (E), Medium (M), or Hard (H)\n")
    if difficulty[0].lower() not in ('e', 'm', 'h'):
        print "Choice not properly given, defaulting to hard!"
    difficulty = 'h'
    print "How many players would you like to play with (including yourself)?"
    while True:
        try:
            count = int(raw_input("Please enter a number from 2 to 6: \n"))
            while count not in range(2, 7):
                print "You did not enter a number from 2 to 6"
                count = int(raw_input("Please try again: \n"))
            break
        except ValueError:
            print "You did not enter an integer, please try again."
    return [count, difficulty[0].lower()]


def roll_dice(num_dice):
    """
    Roll dice for one player or opponent (based on the number of dice inputted,
    and returns the roll as a list.


    Creates a list of rolled dice for the remaining dice of the player/opponent.
    Returns a list of the dice rolled (for instance, if there are 5 dice,
    it returns a roll of 5 dice, where each is a random number from 1-6).
    """
    roll = []
    for x in range(0, num_dice):
        roll.append(randint(1, 6))
    return roll


def roll_all_dice(num_dice_list):
    # adds the player roll, plus rolls the dice for all opponents and adds all to
    # a list
    """
    Using the list of the number of active dice by player, create a list of all
    dice roll lists by player. Returns the list of all dice.


    Using the list of the number of active dice by player, create a list of all
    dice roll lists by player. Returns the list of all dice. For opponents 2-5,
    checks to make sure that they were selected to be players.
    """
    count = len(num_dice_list)
    all_dice = []
    all_dice.append(roll_dice(dice[0]))  # player dice roll
    opponent1_roll = roll_dice(dice[1])
    all_dice.append(opponent1_roll)
    if count > 2:
        opponent2_roll = roll_dice(dice[2])
        all_dice.append(opponent2_roll)
        if count > 3:
            opponent3_roll = roll_dice(dice[3])
            all_dice.append(opponent3_roll)
            if count > 4:
                opponent4_roll = roll_dice(dice[4])
                all_dice.append(opponent4_roll)
                if count > 5:
                    opponent5_roll = roll_dice(dice[5])
                    all_dice.append(opponent5_roll)
    return all_dice


def get_counts_of_dice(all_dice):
    """
    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary.


    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary of dice
    counts from 1 to 6 that have at least 1 die).
    """
    counts = {}
    for die in all_dice:
        for item in die:
            counts[item] = counts.get(item, 0) + 1
    return counts


def get_counts_of_dice_except_opp(opponent_roll, all_dice):
    """
    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary.


    Store the list of dice for each player into a dictionary, and count the
    number of times each die number appears. Return the dictionary of dice
    counts from 1 to 6 that have at least 1 die). (This does NOT include what
    the opponent rolled)
    """
    counts = all_dice
    for item in opponent_roll:
        counts[item] = counts.get(item, 0) - 1
    return counts


def next_turn(turn_marker, count):
    """
    Given the current turn, return the next turn.


    Given the current turn, get the next turn. Return the index of the next
    player/opponent's turn.
    """
    return (turn_marker + 1) % (count + 1)


def get_current_bet(current_turn, previous_bet):
    if current_turn == 0:
        return player_turn(dice_rolls[current_turn], previous_bet, counts)
    else:
        return opponent_turn(dice_rolls[current_turn], previous_bet, counts)


def player_turn(player_roll, current_bet):
    """
    Given the die that have been rolled, show the player the dice and ask them
    for their bet. Return their bet as a tuple (die_choice, die_count).


    Given the die that have been rolled, show the player the dice and ask them
    for their bet. Return their bet as a tuple (die_count, die_choice).

    Checks to make sure that a number was inputted, and that it is valid.
    Gives player the option of resetting their bid if they don't like it.
    """
    current_bet = tuple((4, 5))  # for testing, (count, choice)
    print "Here are the dice you rolled: {}".format(player_roll)
    print "The current bid is for {} {}s.".format(current_bet[0], current_bet[1])
    decision = raw_input("Enter 'B' to place a higher bid, 'C' to challenge, or 'E' for exact:\n")
    while True:
        if decision[0].lower() == 'c' or decision[0].lower() == 'e':
            return [decision[0].lower(), current_bet]
        elif decision[0].lower() != 'b':
            decision = raw_input("Decision is not valid, please re-enter:\n")
            continue
        else:
            while True:
                print "Enter in the dice face (from 2 to 6) you want to choose to bid on."
                print "Remember that 1s are wild (and count towards the number you select)."
                try:
                    die_choice = int(raw_input("Enter the die number you want to bet on:\n"))
                    while die_choice not in range(2, 7):
                        die_choice = int(raw_input("You did not enter a number from 2, to 6, please try again: \n"))
                    print "Please bet on the number of {}s you think all plays have (at a minimum).".format(die_choice)
                    print "The number should be higher than {}, but not greater than the total dice available".format(5)  # this number is TBD, via a parameter that will need to be passed.
                    die_count = int(raw_input("Enter your bet:\n"))
                    while (die_count, die_choice) <= current_bet:
                        print "You did not out bid the current bid, you need to bid more than {} {}s.".format(die_count, die_choice)
                        die_count = int(raw_input("Enter a higher count: \n"))
                    while die_count not in range(total_dice):
                        die_count = int(raw_input("You did not enter a valid number: \n"))
                    print "You bet that at least {} dice have a value of {} (or 1, the wild dice value).".format(die_count, die_choice)
                    confirm = raw_input("Please enter C to confirm or R to reset.\n")
                    if confirm[0].lower() == "r":
                        continue
                    else:
                        break
                except ValueError:
                    print "You need to enter in an integer, please try again!"
            print "current bid {}, new bid dice count ({}, {})".format(current_bet, die_count, die_choice)  # remove later
            return [decision, (die_count, die_choice)]


def opponent_turn(opponent_roll, current_bet, counts):
    current_bet = tuple((4, 5))  # for testing, (count, choice)
    remaining_counts = get_counts_of_dice_except_opp(opponent_roll, counts)
    # opponent_stats = get_opponent_stats(test, test, test, test)

##game
count, difficulty = setup_game()

#generates list of starting dice numbers for each player
dice = [5] * count
#random selection of who starts the game
initial_marker = randint(0, len(dice))
opponent_1 = get_opponent_stats(difficulty)
opponent_2 = get_opponent_stats(difficulty)  # check if this opp exists
opponent_3 = get_opponent_stats(difficulty)  # check if this opp exists
opponent_4 = get_opponent_stats(difficulty)  # check if this opp exists
opponent_5 = get_opponent_stats(difficulty)  # check if this opp exists
# print "initial dice {}".format(dice)  # remove later
# print "initial marker {}".format(initial_marker)  # remove later

dice_rolls = roll_all_dice(dice)
print "dice rolls {}".format(dice_rolls)
total_dice = sum(list(dice))
# print "Total dice {}".format(total_dice)
# print "list of dice rolls {}".format(dice_rolls)
counts = get_counts_of_dice(dice_rolls)
print "dictionary of counts {}".format(counts)

current_turn = next_turn(initial_marker, count)
current_turn = 1  # for testing
#print "next turn {}".format(current_turn) ## need to fix (should be baesd on who loses)

previous_bet = (1, 1)  # initializing previous_bet (die, count)

current_bet = get_current_bet(current_turn, previous_bet)
current_turn = next_turn(initial_marker, count)

# #die # selected
# current_die_choice = None
# #die # estimated count
# current_die_count = None

##note need to handle when players are no longer in the game.









