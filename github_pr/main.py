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

def get_pr_count_for_user_name(user_name, start, end):
    url = f"{host}/search/issues?q=is:pr+author:{user_name}+is:merged+merged:{start}..{end}"
    response = requests.request("GET", url, headers=headers,)
    response.raise_for_status()
    response = response.json()
    items = list(filter(lambda x: x["repository_url"] not in [f"{host}/repos/{Config.org}/{repo}" for repo in Config.exclude_repos],response["items"]))
    print([item["html_url"] for item in items])
    return len(list(items))


team_id = get_team_id(Config.team_slug)
team_members = get_team_members_user_names(team_id)
for member in team_members + Config.additional_user_names:
    print(member, get_pr_count_for_user_name(member, Config.start, Config.end))

