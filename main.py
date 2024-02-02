import operator
import os
import shutil, shlex
import requests
from config import Configuration
import subprocess
import stat
import re
import xlsxwriter
from collections import defaultdict
from tqdm import tqdm


def execute(cmd):
    env = os.environ.copy()
    env["GIT_DIR"] = Configuration.TEMP_DIR
    env["GIT_WORK_TREE"] = Configuration.TEMP_DIR
    output = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.DEVNULL, env=env)
    return output.decode().splitlines()


def rmdir(path):
    if os.path.exists(path):
        def forceremove(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(path, onerror=forceremove)


def fetchrepos():
    page = 1
    done = False
    repos = []
    fetchbar = tqdm(range(1, int(Configuration.REPO_COUNT/100)), desc="Fetching repo metadata", colour="#FF7F50", bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|")
    for page in fetchbar:
        if not done:
            url = f"https://api.github.com/{Configuration.ACCOUNT}/{Configuration.GITHUB_ORG}/repos?page={page}&per_page=100"
            response = requests.get(
                url, headers={"Authorization": f"Bearer {Configuration.GITHUB_TOKEN}"})
            if response.status_code != 200:
                print(f"\n\n{response.json()['message']}")
            if response.status_code != 200 or len(response.json()) == 0:
                done = True
            repos += response.json()
    return repos


def main():
    repos = fetchrepos()
    workbook = xlsxwriter.Workbook(os.path.join(os.getcwd(), "summary.xlsx"))
    repobar = tqdm(range(
        len(repos)), bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|", position=0)
    total_count = {}
    for reprogress in repobar:
        repo = repos[reprogress]
        if Configuration.REPO_FILTER and not repo['name'].upper() in map(str.upper, Configuration.REPO_FILTER):
            continue
        repobar.set_description_str(f"Processing {repo['name']}")
        worksheet = workbook.add_worksheet(f"{repo['name']}")
        worksheet.set_column(0, 5, 50)
        bold = workbook.add_format({"bold": True, "bg_color": "#FFC7CE"})
        worksheet.write_row(0, 0, ["Author", "Files changed",
                            "Lines Added", "Lines Removed", "Output", "Commit"], bold)
        rmdir(Configuration.TEMP_DIR)
        execute(
            f"git clone --no-checkout https://{Configuration.GITHUB_TOKEN}@github.com/{Configuration.GITHUB_ORG}/{repo['name']}.git {Configuration.TEMP_DIR}")
        aggregate = defaultdict(lambda: (0, 0, 0, 0))
        commits = execute(
            f"git log --oneline --all --date=local --since='{Configuration.SINCE}' --until='{Configuration.UNTILL}' --branches='master' --no-merges")
        commitbar = tqdm(range(len(commits)), desc="Parsing commits", leave=False,
                         bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|", position=1, colour="green")
        for index in commitbar:
            c = commits[index]
            shortlog = c.split(" ")[0]
            author = execute(f"git show {shortlog} -s --pretty='%an <%ae>'")[0]
            stats = execute(f"git show --shortstat {shortlog}")
            if len(stats) > 0:
                summary = [0, 0, 0]
                summary[0] = re.findall(
                    "(\d+) files* changed|$", stats[-1])[0] or '0'
                summary[1] = re.findall(
                    "(\d+) insertions*|$", stats[-1])[0] or '0'
                summary[2] = re.findall(
                    "(\d+) deletions*|$", stats[-1])[0] or '0'
                aggregate[author] = (aggregate[author][0] + int(summary[0]), aggregate[author]
                                     [1] + int(summary[1]), aggregate[author][2] + int(summary[2]), aggregate[author][3] + 1)
                worksheet.write_row(
                    index + 1, 0, [author, summary[0], summary[1], summary[2], stats[-1], shortlog])
        index = len(commits) + 5
        worksheet.write_row(index - 1, 0, ["Totals", "", "", "", "count", ""], bold)
        for author in aggregate:
            row = [author] + list(map(int, aggregate[author]))
            if author not in total_count:
                total_count[author] = list(map(int, aggregate[author]))
            else:
                total_count[author] = list(map(operator.add, total_count[author], list(map(int, aggregate[author]))))
            worksheet.write_row(index, 0, row)
            index += 1
        commitbar.close()
    repobar.close()
    worksheet = workbook.add_worksheet("Aggregate")
    worksheet.set_column(0, 5, 50)
    bold = workbook.add_format({"bold": True, "bg_color": "#FFC7CE"})
    worksheet.write_row(0, 0, ["Author", "Files changed",
                               "Lines Added", "Lines Removed", "Count", ""], bold)
    index = 1
    for author, lines in total_count.items():
        row = [author] + list(map(int, lines))
        worksheet.write_row(index, 0, row)
        index += 1
    commitbar = tqdm(total=10.0, initial=10.0, desc="Parsing commits", bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|", colour="green")
    rmdir(Configuration.TEMP_DIR)
    workbook.close()


main()
