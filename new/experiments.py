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


def run_capture(red='baselineTeam', blue='baselineTeam', num_games=2, quiet=True):
    args = ['--red', red, '--blue', blue, '-n', str(num_games)]
    if quiet:
        args.append('-q')
    games = capture.runGames(**capture.readCommand(args))
    return games

def save_score(i, game, red, blue):
    with open(f'game_scores/score_r_{red}_b_{blue}.csv', 'a') as f:
        print(f'{i+1},{game.state.data.score}', file=f)


if __name__ == '__main__':

    # Run Vanilla MCTS vs Baseline Team
    red = 'myVanillaMCTS'
    blue = 'baselineTeam'
    games = run_capture(red, blue)

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

    with open(f'game_scores/elo_r_{red}_b_{blue}.csv', 'r') as f:
        print(f"Final ratings: rating a = {rating_a}, rating b = {rating_b}")

