import os
from jira import JIRA
from config import Config
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
import xlsxwriter


def do_main():
    jira = JIRA(Config.URL, basic_auth=(Config.ACCOUNT, Config.JIRA_TOKEN))
    workbook = xlsxwriter.Workbook(os.path.join(os.getcwd(), "summary.xlsx"))
    pageSize = 50
    projects = jira.projects()
    # fields = jira.fields()
    projectbar = tqdm(range(
        len(projects)), bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|", position=0)
    for idx in projectbar:
        proj = projects[idx]
        issuesList = []
        if Config.JIRA_FILTER is not None and proj.key not in Config.JIRA_FILTER:
            continue
        worksheet = workbook.add_worksheet(f"{proj.key}")
        worksheet.set_column(0, 6, 30)
        bold = workbook.add_format({"bold": True, "bg_color": "#FFC7CE"})
        worksheet.write_row(0, 0, [
                            "Assignee", "Issue", "Priority", "Story Points", "Sprint", "Resolved"], bold)

        projectbar.set_description_str(f"Fetching project {proj.key}")
        aggregate = defaultdict(lambda: 0)
        issues = jira.search_issues(f""" project = "{proj.key}" and resolutiondate >= {Config.SINCE} and resolutiondate < {Config.UNTIL} {Config.JQL} order by priority desc""",
                                    startAt=0, maxResults=1, json_result=True)
        issuesbar = tqdm(range(0, issues["total"], pageSize),
                         bar_format="{desc:50s} {percentage:3.0f}%|{bar:100}|", position=1, colour="magenta", leave=False, desc="Fetching issues")
        for startIndex in issuesbar:
            issues = jira.search_issues(
                f"""project = "{proj.key}" and resolutiondate > {Config.SINCE} and resolutiondate < {Config.UNTIL} {Config.JQL} order by priority desc""", startIndex, pageSize, True, None, expand="names")
            if len(issues) == 0:
                break
            issuesList.extend(issues)

        for (index, i) in enumerate(issuesList):
            storyPoints = max(float(i.raw["fields"][Config.STORY_POINT_ESTIMATE_FIELD] or "0.0"),
                              float(i.raw["fields"][Config.STORY_POINT_FIELD] or "0.0"))
            sprint = i.raw["fields"][Config.SPRINT_FIELD].pop() if i.raw["fields"][Config.SPRINT_FIELD] else {"name": "Unknown"}
            closed = datetime.strptime(
                i.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d")
            worksheet.write_row(
                index + 1, 0, [f"{i.fields.assignee}", i.key, f"{i.fields.priority}", storyPoints, sprint["name"], closed])
            aggregate[i.fields.assignee] += storyPoints
        index = len(issuesList) + 5
        worksheet.write_row(index - 1, 0, ["Totals", "", "", "", "", ""], bold)
        for author in aggregate:
            row = [f"{author}", aggregate[author]]
            worksheet.write_row(index, 0, row)
            index += 1
    workbook.close()


do_main()
