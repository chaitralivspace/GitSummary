import os
# set GH_TOKEN=<token>
# Command to validate github cli token: gh repo list livspaceeng -L 10 --json isPrivate

class Configuration:
    GITHUB_TOKEN = "<GITHUB TOKEN>"
    GITHUB_ORG = "livspaceeng"
    SINCE = "2023-07-01" # Date since for commit report
    REPO_FILTER = [ "paramarsh", "bumblebee" ] # Report only these, set to None for all
    TEMP_DIR = os.path.join(os.getcwd(), "temp").replace("\\", "/")
    ACCOUNT = "orgs"  # Allowed values users or orgs
    REPO_COUNT = 1000 # Rough number of repos

if os.system("git --version > " + os.devnull) != 0:
    raise Exception("Git is not installed or not in path")
