from datetime import datetime
class Config:
    URL = "https://livspaceengg.atlassian.net"
    JIRA_TOKEN = "<JIRA_TOKEN>"
    ACCOUNT = "Chaithrahebbar@livspace.com"
    SINCE = "2023-11-01"
    UNTIL = "2023-12-01"
    JQL = "and (issuetype = story or issuetype = task or issuetype = bug) and (status = closed) and resolution = Done"
    # JIRA_FILTER = ["SAG", "Services", "CAT", "QAD", "IN"]
    JIRA_FILTER = ["QAD"]
    STORY_FIELD = "customfield_10036"
    SPRINT_FIELD = "customfield_10020"
