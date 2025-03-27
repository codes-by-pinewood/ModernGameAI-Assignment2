from trueskill import Rating, quality_1vs1, rate_1vs1
from baselineTeam import ReflexCaptureAgent 
from myVanillaMCTS import myVanillaMCTSAgent
from myHeuristicMCTS import myHeuristicMCTSAgent
import capture


def expected_score_elo(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_elo(rating_a, rating_b, score_a, k=32):
    """
    rating_a, rating_b: current Elo ratings
    score_a: actual result for A (1 = win, 0 = loss, 0.5 = draw)
    """
    expected_a = expected_score_elo(rating_a,  rating_b)
    expected_b = 1 - expected_a
    rating_a_new = rating_a + k * (score_a - expected_a)
    rating_b_new = rating_b + k * ((1 - score_a) - expected_b)
    return rating_a_new, rating_b_new


def run_capture(red='baselineTeam', blue='baselineTeam', num_games=2, quiet=True, length=None, num_simulations=None, epsilon=None):
    args = ['--red', red, '--blue', blue, '-n', str(num_games)]
    if quiet:
        args.append('-q')

    if red == 'myVanillaMCTS':
        args += ['--redOpts', f'length={length},num_simulations={num_simulations}']
    # if red == # TODO
    #     args += ['--redOpts', f'length={length},num_simulations={num_simulations}, epsilon={epsilon}']

    games = capture.runGames(**capture.readCommand(args))
    return games


def save_score(i, game, red, blue):
    with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'a') as f:
        print(f'{i+1},{game.state.data.score}', file=f)


def hyperparameter_tuning_vanilla():
    # Run Vanilla MCTS vs Baseline Team
    red = 'myVanillaMCTS'
    blue = 'baselineTeam'

    lengths = [2, 4, 8, 16, 32]
    numbers_simulations = [10, 50, 100]
    best_score = float('-inf')
    best_param = None

    for length in lengths:
        for number_simulations in numbers_simulations:
            print(f'length: {length}')
            print(f'numbers_simulations: {number_simulations}')

            games = run_capture(red, blue, length=length, num_simulations=number_simulations)
            for i, game in enumerate(games):
                save_score(i, game, red, blue)
                print(f"Game {i+1}: Final Score = {game.state.data.score}")

            # After running all the games do ELO
            rating_a = 0
            rating_b = 0
            with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    score = int(parts[1])
                    
                    if score == 0: score_a = 0.5
                    else: score_a = 0 if score < 0 else 1

                    rating_a, rating_b = update_elo(rating_a, rating_b, score_a)

            with open(f'game_scores/elo_r_{red}_b_{blue}.csv', 'a') as f:
                print(f'Length={length}, num_simulations={number_simulations}', file=f)
                print(f"Final ratings: rating a = {rating_a}, rating b = {rating_b}", file=f)

            # Save to reuse for HP evaluation
            score_elo = rating_a
            
            # HERE ADD TRUESKILL
            score_trueskill = 0

            # COMPUTE FINAL SCORE FOR HP TUNING - UPDATE BEST SCORE IF NECESSARY
            final_score = score_elo + score_trueskill
            if best_score < final_score:
                best_score = final_score 
                best_param = [length, number_simulations]

    return best_param

# def hyperparameter_tuning_ucb():
#     # Run UCB MCTS vs Baseline Team
#     red = '' #TODO
#     blue = 'baselineTeam'

#     lengths = [2, 4, 8, 16, 32]
#     numbers_simulations = [10, 50, 100]
#     epsilons = [] #TODO
#     best_score = float('-inf')
#     best_param = None

#     for length in lengths:
#         for number_simulations in numbers_simulations:
#             for epsilon in epsilons:
#                 print(f'length: {length}')
#                 print(f'numbers_simulations: {number_simulations}')
#                 print(f'epsilon: {epsilon}')

#                 games = run_capture(red, blue, length=length, num_simulations=number_simulations, epsilon=epsilon)
#                 for i, game in enumerate(games):
#                     save_score(i, game, red, blue)
#                     print(f"Game {i+1}: Final Score = {game.state.data.score}")

#                 # After running all the games do ELO
#                 rating_a = 0
#                 rating_b = 0
#                 with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'r') as f:
#                     for line in f:
#                         parts = line.strip().split(',')
#                         score = int(parts[1])
                        
#                         if score == 0: score_a = 0.5
#                         else: score_a = 0 if score < 0 else 1

#                         rating_a, rating_b = update_elo(rating_a, rating_b, score_a)

#                 with open(f'game_scores/elo_r_{red}_b_{blue}.csv', 'a') as f:
#                     print(f'Length={length}, num_simulations={number_simulations}', file=f)
#                     print(f"Final ratings: rating a = {rating_a}, rating b = {rating_b}", file=f)

#                 # Save to reuse for HP evaluation
#                 score_elo = rating_a
                
#                 # HERE ADD TRUESKILL
#                 score_trueskill = 0

#                 # COMPUTE FINAL SCORE FOR HP TUNING - UPDATE BEST SCORE IF NECESSARY
#                 final_score = score_elo + score_trueskill
#                 if best_score < final_score:
#                     best_score = final_score 
#                     best_param = [length, number_simulations]

#     return best_param


if __name__ == '__main__':

    # HYPERPARAMETER TUNING
    # For Vanilla MCTS: length and number of simulations
    best_params_vanilla_mcts = hyperparameter_tuning_vanilla()

    # best_params_ucb_mcts = hyperparameter_tuning_ucb()
    
   