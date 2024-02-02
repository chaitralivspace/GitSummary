import requests

from github_pr.config import Config

host = "https://api.github.com"
headers = {
    'Authorization': f'token {Config.token}',
    'Accept': 'application/vnd.github.v3+json'
}


def get_team_id(team_slug):
    url = f"{host}/orgs/{Config.org}/teams"
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    response = response.json()
    team = list(filter(lambda x: x["slug"] == team_slug, response))
    if len(team) > 0:
        return team[0]["id"]
    raise ValueError(f"Team slug {team_slug} doesn't exist in org: {Config.org}")

def get_team_members_user_names(team_id):
    url = f"{host}/teams/{team_id}/members"
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()
    response = response.json()
    return [user["login"] for user in response]

def get_pr_count_for_repo(repo, start, end):
    url = f"{host}/search/issues?q=is:pr+repo:livspaceeng/{repo}+is:merged+merged:{start}..{end}"
    response = requests.request("GET", url, headers=headers,)
    response.raise_for_status()
    response = response.json()
    items = response["items"]
    print([item["html_url"] for item in items])
    for item in items:
        user = item["user"]["login"]
        base_branch = get_pr_base_branch(item['pull_request']['url'])
        if base_branch not in Config.allowed_base_bracnches:
            print("Base branch %s not allowed" %base_branch)
            continue
        if user in pr_count["count"]:
            pr_count["count"][user] += 1
        else:
            pr_count["count"][user] = 1
        update_pr_comments(item['pull_request']['url'])
        update_pr_approvals(item['pull_request']['url'], item['pull_request']['html_url'], user)

def get_pr_base_branch(pr_url):
    print("Fetching base branch for PR: ", pr_url)
    pr_data = requests.get(pr_url, headers=headers).json()
    return pr_data['base']['ref']

def update_pr_comments(pr_url):
    reviews_url = f"{pr_url}/comments"
    print("Fetching commments for PR: ", pr_url)
    reviews_response = requests.get(reviews_url, headers=headers)
    reviews_data = reviews_response.json()
    for review in reviews_data:
        user = review["user"]["login"]
        if user in pr_count["comments"]:
            pr_count["comments"][user] += 1
        else:
            pr_count["comments"][user] = 1

def update_pr_approvals(pr_url, html_url, pr_owner):
    reviews_url = f"{pr_url}/reviews"
    print("Fetching reviews for PR: ", pr_url)
    reviews_response = requests.get(reviews_url, headers=headers)
    reviews_data = reviews_response.json()
    if len(reviews_data) > 0:
        if pr_owner in pr_count["approved"]:
            pr_count["approved"][pr_owner] += 1
        else:
            pr_count["approved"][pr_owner] = 1
        if pr_owner not in prs:
            prs[pr_owner] = {"approved": [html_url], "unapproved": []}
        else:
            prs[pr_owner]["approved"].append(html_url)
    else:
        if pr_owner not in prs:
            prs[pr_owner] = {"approved": [], "unapproved": [html_url]}
        else:
            prs[pr_owner]["unapproved"].append(html_url)
    for review in reviews_data:
        user = review["user"]["login"]
        if user in pr_count["approver"]:
            pr_count["approver"][user] += 1
        else:
            pr_count["approver"][user] = 1


prs = {}
pr_count = {"count": {}, "approved": {}, "approver": {}, "comments": {}}
for i, repo in enumerate(Config.REPO_FILTER):
    print(repo)
    get_pr_count_for_repo(repo, Config.start, Config.end)
    print(prs)


combined = {}
for user, count in pr_count["count"].items():
    combined[user] = [count,0,0,0]

for user, count in pr_count["approved"].items():
    if user not in combined:
        combined[user] = [0,count,0,0]
    else:
        combined[user][1] = count

for user, count in pr_count["approver"].items():
    if user not in combined:
        combined[user] = [0,0,count,0]
    else:
        combined[user][2] = count

for user, count in pr_count["comments"].items():
    if user not in combined:
        combined[user] = [0,0,0,count]
    else:
        combined[user][3] = count

import csv

with open('summary.csv', 'w', newline='') as csvfile:
    fieldnames = ['username', 'pr', 'approved', 'approvals', 'comments']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for user, data in combined.items():
        writer.writerow({'username': user, 'pr': data[0], 'approved': data[1], 'approvals': data[2], 'comments': data[3]})
with open('summary_raw.csv', 'w', newline='') as csvfile:
    fieldnames = ['username', 'pr', 'status']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for user, data in prs.items():
        for pr in data["approved"]:
            writer.writerow({'username': user, 'pr': pr, 'status': "approved"})
        for pr in data["unapproved"]:
            writer.writerow({'username': user, 'pr': pr, 'status': "unapproved"})


     
