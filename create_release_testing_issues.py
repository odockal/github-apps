import os
import requests
import json

MAIN_ISSUE_DESCRIPTION = """
Placeholder for testing of [1.22.1 bits](https://github.com/podman-desktop/podman-desktop/releases/tag/v1.22.1) of Podman Desktop using [Podman 5.6.2](https://github.com/containers/podman/releases/tag/v5.6.2).

#### Diff-list of commits between the current and the latest release: 
* https://github.com/podman-desktop/podman-desktop/compare/v1.22.0...v1.22.1

#### 1.22.1 Milestones issue: 
* https://github.com/podman-desktop/podman-desktop/milestone/56

Podman 5.6.2 client and installer available for windows and mac (linked above)

#### Fedora base image version available for:

#####  Windows
 * WSL Base image: `quay.io/podman/machine-os-wsl:5.6`
 * HyperV base image: `quay.io/podman/machine-os:5.6`

##### Mac OS
 * Base image: `quay.io/podman/machine-os:5.6`

```
$ skopeo inspect docker://quay.io/podman/machine-os:5.6 | jq ".Digest"
TBD

podman image inspect quay.io/podman/machine-os:5.6 | jq ".[].RepoDigests"
[
TBD
]

```

##### Linux
* [Podman 5.6.1 fedora packages in Fedora 41/42](https://bodhi.fedoraproject.org/updates/?search=podman-5.6.1)
* [Podman 5.6.1 fedora packages Koji](https://koji.fedoraproject.org/koji/buildinfo?buildID=2811154)

#### Focus area for testing of Podman Desktop:
* Update to Podman 5.6.2
#### Release sheet: 
* [1.22.1 podman desktop testing tracking results]()

#### End of testing target date:
* Please finish testing by Wednesday (2025-10-15) EOD around 18:00 CET."""

SUB_ISSUE_DESCRIPTION = """Please perform a release testing of a particular Podman Desktop version with given configuration (platform and virtualization provider). 
For details see the parent issue.
Once you are done testing, please mark down (comment) orientation time (in hours) that testing took and what configuration of the system you have used (ie. win 10 x64, etc.)."""


def create_github_issues(repo_name, main_issue_title, main_issue_description, release_testing_lead, subtasks):
    """
    Creates a main GitHub issue and multiple sub-issues linked to it.
    
    Args:
        repo_name (str): The name of the repository (e.g., 'your_username/your_repo').
        main_issue_title (str): The title for the main issue.
        main_issue_description (str): The description for the main issue.
        subtasks (list): A list of dictionaries, where each dictionary represents a sub-issue.
                         Each dictionary must have 'title' and 'description' and can optionally
                         have an 'assignee' field.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: 'GITHUB_TOKEN' environment variable is not set. Please set it before running the script.")
        return

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    issues_url = f"https://api.github.com/repos/{repo_name}/issues"

    # --- Create the main issue ---
    main_issue_data = {
        "title": main_issue_title,
        "body": main_issue_description,
        "assignees": [release_testing_lead]  # Optionally assign the main issue
    }
    try:
        response = requests.post(issues_url, headers=headers, data=json.dumps(main_issue_data))
        response.raise_for_status()
        main_issue = response.json()
        print(f"✅ Main issue created: {main_issue['html_url']}")
        
        # We need the node_id to create the relationship
        parent_issue_id = main_issue['id']
        parent_issue_number = main_issue['number']
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating main issue: {e}")
        return

    # --- Create and link the sub-issues ---
    for subtask in subtasks:
        assignee = subtask.get('assignee')
        
        # 1. Create the sub-issue first
        sub_issue_data = {
            "title": subtask['title'],
            "body": subtask['description']
        }
        if assignee:
            sub_issue_data['assignees'] = [assignee]

        sub_issue = None
        try:
            sub_response = requests.post(issues_url, headers=headers, data=json.dumps(sub_issue_data))
            print(f"Status code: {sub_response.status_code}")
            sub_response.raise_for_status()
            sub_issue = sub_response.json()
            sub_issue_id = sub_issue['id']
            print(f"✅ Sub-issue created: {sub_issue['html_url']}")

            # 2. Now, link the sub-issue to the parent using the dedicated endpoint
            # This requires a POST request to the parent issue's sub_issues endpoint
            sub_issues_url = f"https://api.github.com/repos/{repo_name}/issues/{parent_issue_number}/sub_issues"
            link_data = {
                "sub_issue_id": sub_issue_id
            }
            
            link_headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            link_response = requests.post(sub_issues_url, headers=link_headers, data=json.dumps(link_data))
            link_response.raise_for_status()
            print(f"Status code: {link_response.status_code}")
            print(f"🔗 Sub-issue linked to parent issue #{parent_issue_number}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating or linking sub-issue: {e}")
            
# --- Script Usage Example ---
if __name__ == "__main__":
    # --- Configuration ---
    # Replace with your actual repository name (e.g., 'your_username/your_repo')
    REPO_NAME = "organization/repository"

    # --- Main Issue Details ---
    MAIN_ISSUE_TITLE = "Testing of Podman Desktop 1.22.1 Bug fix release with Podman 5.6.2"

    RELEASE_TESTING_LEAD = "odockal"  # Optional assignee for the main issue

    # --- Sub-issues Details ---
    SUB_ISSUES = [
        {
            "title": "Testing of Podman Desktop 1.22.1 on Mac OS with Likbrun provider",
            "description": SUB_ISSUE_DESCRIPTION, 
            "assignee": "serbangeorge-m"  # Optional assignee
        },
        {
            "title": "Testing of Podman Desktop 1.22.1 on Mac OS with Applehv provider",
            "description": SUB_ISSUE_DESCRIPTION,
            "assignee": "cbr7"
        },
        {
            "title": "Testing of Podman Desktop 1.22.1 on Windows with WSL provider",
            "description": SUB_ISSUE_DESCRIPTION,
            "assignee": "danivilla9"
        },
        {
            "title": "Testing of Podman Desktop 1.22.1 on Windows with HyperV provider",
            "description": SUB_ISSUE_DESCRIPTION,
            "assignee": "ScrewTSW"
        },        {
            "title": "Testing of Podman Desktop 1.22.1 on Linux",
            "description": SUB_ISSUE_DESCRIPTION,
            "assignee": "amisskii"
        },        {
            "title": "Testing of Podman Desktop 1.22.1 on RHEL",
            "description": SUB_ISSUE_DESCRIPTION,
            "assignee": RELEASE_TESTING_LEAD
        },
        {
            "title": "Automated Testing of Podman Desktop 1.22.1 bug fix release",
            "description": "Trigger and collect the automated test results from all configurations",
            "assignee": RELEASE_TESTING_LEAD
        }
    ]

    # --- Run the script ---
    create_github_issues(
        repo_name=REPO_NAME,
        main_issue_title=MAIN_ISSUE_TITLE,
        main_issue_description=MAIN_ISSUE_DESCRIPTION,
        release_testing_lead=RELEASE_TESTING_LEAD,
        subtasks=SUB_ISSUES
    )
