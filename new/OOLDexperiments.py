# from trueskill import Rating, quality_1vs1, rate_1vs1
from baselineTeam import ReflexCaptureAgent 
from new.myNaiveMCTS import myVanillaMCTSAgent
from myHeuristicMCTS import myHeuristicMCTSAgent
import capture
import os
import pandas as pd


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


def run_capture(red='baselineTeam', blue='baselineTeam', num_games=1, quiet=True, length=None, num_simulations=None, epsilon=None, exploration_constant=None):
    args = ['--red', red, '--blue', blue, '-n', str(num_games)]
    if quiet:
        args.append('-q')

    if red == 'myVanillaMCTS':
        args += ['--redOpts', f'length={length},num_simulations={num_simulations}']
    elif red == 'myUCBMCTS':
        if epsilon == None: 
            args += ['--redOpts', f'rollout_depth={length},simulations={num_simulations},exploration_constant={exploration_constant}']
        else: 
            print("EPSILON is NOT NONE")
            args += ['--redOpts', f'rollout_depth={length},simulations={num_simulations},exploration_constant={exploration_constant},epsilon={epsilon}']
    elif red == 'myHeuristicMCTS':
            args += ['--redOpts', f'length={length},num_simulations={num_simulations},exploration_constant={exploration_constant}']

    games = capture.runGames(**capture.readCommand(args))
    return games

def save_score(games, red, blue, length, number_simulations, file_name, epsilon=None, exploration_constant=None):
    game_data = []
    for i, game in enumerate(games):
        game_info = {
            "game_number": i + 1,
            "final_score": game.state.data.score,
            "red_agent": red,
            "blue_agent": blue,
            "length": length,
            "num_simulations": number_simulations,
            "epsilon": epsilon,
            "exploration_constant": exploration_constant
        }
        game_data.append(game_info)

    pd.DataFrame(game_data).to_csv(f"game_scores/{file_name}.csv", mode='a', index=False)


def compute_score_elo(df, length, number_simulations, file_name, epsilon, exploration_constant):
    rating_a = 0
    rating_b = 0

    for _, row in df.iterrows():
        score = int(row["final_score"])
        if score == 0:
            score_a = 0.5
        else:
            score_a = 0 if score < 0 else 1
        rating_a, rating_b = update_elo(rating_a, rating_b, score_a)

    with open(f"game_scores/elo_{file_name}.csv", "a") as f:
        print(f"Length={length}, num_simulations={number_simulations}, epsilon={epsilon}, exploration_constant={exploration_constant}", file=f)
        print(f"Final ratings: rating a = {rating_a}, rating b = {rating_b}", file=f)

    return rating_a


def hyperparameter_tuning_vanilla(num_games=10):
    # Run Vanilla MCTS vs Baseline Team
    red = 'myVanillaMCTS'
    blue = 'baselineTeam'
    file_name = f'r_{red}_b_{blue}_hpo'

    lengths = [2, 4, 8, 16]
    numbers_simulations = [10, 50, 80]
    best_score = float('-inf')
    best_param = None

    for length in lengths:
        for number_simulations in numbers_simulations:
            games = run_capture(red, blue, length=length, num_games=num_games, num_simulations=number_simulations, epsilon=None, exploration_constant=None)
            save_score(games, red=red, blue=blue, length=length, number_simulations=number_simulations, file_name=file_name, epsilon=None, exploration_constant=None)

    # After running all the games do ELO
    result_score_df = pd.read_csv(f"game_scores/{file_name}.csv")

    for length in lengths:
        for number_simulations in numbers_simulations:
            length_str = str(length)
            number_simulations_str = str(number_simulations)

            filtered = result_score_df[(result_score_df["length"] == length_str) & (result_score_df["num_simulations"] == number_simulations_str)]
            score_elo = compute_score_elo(df=filtered, length=length, number_simulations=number_simulations, file_name=file_name,exploration_constant=None, epsilon=None)

            # COMPUTE FINAL SCORE FOR HP TUNING - UPDATE BEST SCORE IF NECESSARY
            if best_score < score_elo:
                best_score = score_elo 
                best_param = [length, number_simulations]

    print(f"Best Vanilla MCTS hyperparameters: length={best_param[0]}, number of simulations={best_param[1]}")
    return best_param

def hyperparameter_tuning_ucb(num_games=10):
    # Run UCB MCTS vs Baseline Team
    red = 'myUCBMCTS'
    blue = 'baselineTeam'
    file_name = f'r_{red}_b_{blue}_hpo'

    lengths = [2, 4, 8, 16]
    numbers_simulations = [10, 50, 80]
    exploration_constants = [0.6, 0.5, 0.4, 0.1]
    epsilons = [0.1, 0.05, 0.01] # HERE 
    best_score = float('-inf')
    best_param = None

    for length in lengths:
        for number_simulations in numbers_simulations:
            for exploration_constant in exploration_constants: 
                for epsilon in epsilons:
                    games = run_capture(red, blue, length=length, num_games=num_games, num_simulations=number_simulations, epsilon=epsilon, exploration_constant=exploration_constant)
                    save_score(games, red=red, blue=blue, length=length, number_simulations=number_simulations, file_name=file_name, epsilon=epsilon, exploration_constant=exploration_constant)
        
    # After running all the games do ELO
    result_score_df = pd.read_csv(f"game_scores/{file_name}.csv")

    for length in lengths:
        for number_simulations in numbers_simulations:
            for exploration_constant in exploration_constants: 
                for epsilon in epsilons:
                    length_str = str(length)
                    number_simulations_str = str(number_simulations)
                    epsilon_str = str(epsilon)
                    exploration_constant_str = str(exploration_constant)

                    filtered = result_score_df[(result_score_df["length"] == length_str) & (result_score_df["num_simulations"] == number_simulations_str)
                                            & (result_score_df["epsilon"] == epsilon_str) & (result_score_df["exploration_constant"] == exploration_constant_str)]
                    score_elo = compute_score_elo(df=filtered, length=length, number_simulations=number_simulations, file_name=file_name, epsilon=epsilon, exploration_constant=exploration_constant)

                    # COMPUTE FINAL SCORE FOR HP TUNING - UPDATE BEST SCORE IF NECESSARY
                    if best_score < score_elo:
                        best_score = score_elo 
                        best_param = [length, number_simulations, epsilon, exploration_constant]

    print(f"Best UCB MCTS hyperparameters: length={best_param[0]}, number of simulations={best_param[1]}, epsilon={best_param[2]}, exploration_constant={best_param[3]}")
    return best_param

def hyperparameter_tuning_heuristic_mcts(num_games=10):
    # Run Heuristic MCTS vs Baseline Team
    red = 'myHeuristicMCTS'
    blue = 'baselineTeam'
    file_name = f'r_{red}_b_{blue}_hpo'

    lengths = [2, 4]#, 8, 16]
    numbers_simulations = [10, 50, 80]
    exploration_constants = [0.6, 0.5, 0.4, 0.1]
    best_score = float('-inf')
    best_param = None

    for length in lengths:
        print(f"----------- Length: {length} -----------")
        for number_simulations in numbers_simulations:
            print(f"----------- Number of Simulations: {number_simulations} -----------")
            for exploration_constant in exploration_constants:
                print(f"----------- Exploration Constant: {exploration_constant} -----------")
                games = run_capture(red, blue, length=length, num_games=num_games, num_simulations=number_simulations, epsilon=None, exploration_constant=exploration_constant)
                save_score(games, red=red, blue=blue, length=length, number_simulations=number_simulations, file_name=file_name, epsilon=None, exploration_constant=exploration_constant)

    # After running all the games do ELO
    result_score_df = pd.read_csv(f"game_scores/{file_name}.csv")

    for length in lengths:
        for number_simulations in numbers_simulations:
            for exploration_constant in exploration_constants:
                length_str = str(length)
                number_simulations_str = str(number_simulations)
                exploration_constant_str = str(exploration_constant)

                filtered = result_score_df[(result_score_df["length"] == length_str) & (result_score_df["num_simulations"] == number_simulations_str)
                                            & (result_score_df["exploration_constant"] == exploration_constant_str)]
                score_elo = compute_score_elo(df=filtered, length=length, number_simulations=number_simulations, file_name=file_name,exploration_constant=exploration_constant, epsilon=None)

            # COMPUTE FINAL SCORE FOR HP TUNING - UPDATE BEST SCORE IF NECESSARY
            if best_score < score_elo:
                best_score = score_elo 
                best_param = [length, number_simulations, exploration_constant]

    print(f"Best Heuristic-based MCTS hyperparameters: length={best_param[0]}, number of simulations={best_param[1]}, exploration_constant={best_param[2]}")
    return best_param

def run_tournament(red, blue, num_games, quiet):

    games = run_capture(red=red, blue=blue, num_games=num_games, quiet=quiet)
    for i, game in enumerate(games):
        save_score(i, game, red, blue, length=0, num_sim=0, epsilon=0)
        print(f"Game {i+1}: Final Score = {game.state.data.score}")

    rating_a = 0
    rating_b = 0
    with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts)>1:
                score = int(parts[1])
            
                if score == 0: score_a = 0.5
                else: score_a = 0 if score < 0 else 1

                rating_a, rating_b = update_elo(rating_a, rating_b, score_a)

    with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'a') as f:
        print(f'Final ratings: rating a = {rating_a}', file=f)


if __name__ == '__main__':

    # Hyperparameter tuning
    number_games=10
    # best_params_vanilla_mcts = hyperparameter_tuning_vanilla(number_games)
    # best_params_ucb_mcts = hyperparameter_tuning_ucb(number_games)
    best_params_heuristic_mcts = hyperparameter_tuning_heuristic_mcts(number_games)

    # Running tournaments 
    """
    Logic: first naive VS baseline, second - heuristic VS baseline, 
    (if heuristic wins, which it does) UCB VS heuristic, e-decay VS best so far
    red = 'myVanillaMCTS'
    blue = 'baselineTeam'
    print(f"Tournament: {red} VS {blue}")
    run_tournament(red, blue, quiet=True, num_games=2)

    red = 'heuristic_agent'
    blue = 'baselineTeam'
    print(f"Tournament: {red} VS {blue}")
    run_tournament(red, blue, quiet=True, num_games=2)

    red = 'myUCBMCTS'
    blue = 'heuristic_agent'
    print(f"Tournament: {red} VS {blue}")
    run_tournament(red, blue, quiet=True, num_games=2)
    """



