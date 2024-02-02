from datetime import datetime
class Config:
    URL = "https://livspaceengg.atlassian.net"
    JIRA_TOKEN = "<JIRA_TOKEN>"
    ACCOUNT = "Chaithrahebbar@livspace.com"
    SINCE = "2024-01-01"
    UNTIL = "2024-02-01"
    JQL = "and (issuetype = story or issuetype = task or issuetype = bug) and (status = closed) and resolution = Done"
    JIRA_FILTER = ["QAD"]
    STORY_POINT_ESTIMATE_FIELD = "customfield_10016"
    STORY_POINT_FIELD = "customfield_10016"
    SPRINT_FIELD = "customfield_10020"
