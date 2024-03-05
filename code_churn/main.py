import csv
import json
import subprocess

from code_churn.config import Config


def clone_repository(repo_url, folder_path):
    try:
        subprocess.run(["git", "clone", repo_url, folder_path], check=True)
        print(f"Repository cloned successfully to {folder_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def get_commits_in_month(folder_path, since, until):
    # Get the first and last day of the specified month

    # Execute git log command to get commit hashes within the specified date range
    git_log_command = ["git", "log", "--pretty=format:%H", f"--since={since}", f"--until={until}"]
    result = subprocess.run(git_log_command, cwd=folder_path, capture_output=True, text=True)

    if result.returncode == 0:
        commit_hashes = result.stdout.strip().split('\n')
        if commit_hashes:
            return commit_hashes
        else:
            return None
    else:
        print(f"Error getting commits: {result.stderr}")
        return None


def run_cloc(folder_path, commit1, commit2):
    # Execute cloc command to get lines of code difference between two commits
    cloc_command = ["bash", "/tmp/script.sh", commit1, commit2, "PYTHON,HTML,Javascript,Typescript,CSS,SCSS,Java"]
    print(" ".join(cloc_command))
    result = subprocess.run(cloc_command, cwd=folder_path, capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
        print(json.dumps(json.loads(result.stdout)))
        return json.loads(result.stdout)
    else:
        print(f"Error running cloc: {result.stderr}")
        return None


with open('summary_raw.csv', 'w', newline='') as csvfile:
    fieldnames = ['repo', 'TLOC', 'files', 'added', 'deleted', 'modified']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for repo in Config.REPO_FILTER:
        # Replace 'your_repo_url' with the URL of the repository you want to clone
        repo_url = f'https://github.com/livspaceeng/{repo}'

        # Replace 'your_folder_path' with the desired folder path where you want to clone the repository
        folder_path = f'/tmp/{repo}'

        clone_repository(repo_url, folder_path)
        commit_hashes = get_commits_in_month(folder_path, Config.start, Config.end)

        if commit_hashes and len(commit_hashes) >= 2:
            commit1 = commit_hashes[0]
            commit2 = commit_hashes[-1]
            print(f"First commit in the month: {commit1}")
            print(f"Last commit in the month: {commit2}")

            cloc_result = run_cloc(folder_path, commit1, commit2)
            if cloc_result:
                print(f"\nLines of code difference between {commit1} and {commit2}:\n{cloc_result}")
                writer.writerow({'repo': repo, 'TLOC': cloc_result["header"]["n_lines"],
                                 'files': cloc_result["header"]["n_files"],
                                 'added': cloc_result["SUM"]["added"]["code"],
                                 'modified': cloc_result["SUM"]["modified"]["code"],
                                 'deleted': cloc_result["SUM"]["removed"]["code"],

                                 })


        else:
            print(f"No commits in the specified strat and end {Config.start}..{Config.end}.")
            writer.writerow(
                {'repo': repo, 'TLOC': 'NA',
                 'files': 'NA',
                 'added': 'NA',
                 'modified': 'NA',
                 'deleted': 'NA'
                 }
            )
