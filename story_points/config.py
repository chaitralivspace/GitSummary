from datetime import datetime
class Config:
    URL = "https://livspaceengg.atlassian.net"
    JIRA_TOKEN = "<JIRA_TOKEN>"
    ACCOUNT = "Chaithrahebbar@livspace.com"
    SINCE = "2023-10-01"
    UNTIL = datetime.today().strftime("%Y-%m-%d")
    JQL = "and (issuetype = story or issuetype = task) and (status = closed)"
    # JIRA_FILTER = ["SAG", "Services", "CAT", "QAD", "IN"]
    JIRA_FILTER = ["QAD"]
    STORY_FIELD = "customfield_10036"
    SPRINT_FIELD = "customfield_10020"
