class Config:
    token="<GITHUB_PAT>"
    org="livspaceeng"
    team_slug="visualization"
    exclude_repos=["qad-deployments", "app-flux", "sag-deployments"]
    additional_user_names=["ayurjain-livspace","rohit-kr-livspace","pkb98","sundeep-9"]
    REPO_FILTER = { "paramarsh", "auxilium", "brok", "sindri", "liv-home", "lego-web", "livhome-backend", "paramarsh", "pylab-client", "render-farm", "Simulator",
                    "spider", "welcomeboard3d", "py-consumers", "parametric-3dtool", "blueprint", "Parametric-Simulator", "ls-backoffice","odin","peggy",
                    "quotes-graphql", "platformweb" }
    start="2024-01-01"
    end="2024-02-01"
    allowed_base_bracnches = ["prod", "master", "main"]
