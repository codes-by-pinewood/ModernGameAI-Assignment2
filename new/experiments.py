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


def run_capture(red='myVanillaMCTS', blue='baselineTeam', num_games=3, quiet=True):
    args = ['--red', red, '--blue', blue, '-n', str(num_games)]
    if quiet:
        args.append('-q')
    games = capture.runGames(**capture.readCommand(args))
    return games

def save_score(game, red, blue):
    with open(f'score_r_{red}_b_{blue}', 'a') as f:
        print(game.state.data.score,file=f)


if __name__ == '__main__':
    # Run Vanilla MCTS vs Baseline Team
    red = 'myVanillaMCTS'
    blue = 'baselineTeam'
    games = run_capture(red, blue)

    for game in games:
        save_score(game, red, blue)

    for i, g in enumerate(games):
        print(f"Game {i+1}: Final Score = {g.state.data.score}")
        

