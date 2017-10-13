import numpy

def get_opponent_stats(difficulty):
    if difficulty == 'e':
        intelligence_mean = .35
    elif difficulty == 'm':
        intelligence_mean = .6
    else:
        intelligence_mean = .85

    liar_stats = min(max(numpy.random.normal(.125, .025), 0), 1)
    aggressive_stats = min(max(numpy.random.normal(.4 + liar_stats, .14), 0), 1)  # bigger liar -> bigger aggression
    intelligence_stats = min(max(numpy.random.normal(intelligence_mean - aggressive_stats/10, .03), 0), 1)  # more aggressive -> lower intel
    return [liar_stats, aggressive_stats, intelligence_stats]
