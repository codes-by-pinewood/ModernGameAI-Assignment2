
import matplotlib.pyplot as plt 
import subprocess

def run_capture():
    result = subprocess.run(['python3', 'capture.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print("Return code: ", result.returncode)
    print("result: ", result)
    output = result.stdout.strip()
    print("Output: ", output)
    if "The Blue team has returned at least 18 of the opponents' dots" in output:
        return -18
    elif "Tie game!" in output:
        return 0
    else: 
        return 0
 
def main():
    num_runs = 50
    scores = []

    # Run capture.py 50 times and store the scores
    for _ in range(num_runs):
        score = run_capture()
        if score is not None:
            scores.append(score)

    print("Scores: ", scores)
    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=10, edgecolor='black')
    plt.title("Distribution of Scores from 50 Runs of capture.py")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()