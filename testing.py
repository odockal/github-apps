import os
import requests
import json

def run_testing_call(repo_name, parent_issue_number, sub_issue_number):

    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: 'GITHUB_TOKEN' environment variable is not set. Please set it before running the script.")
        return

    try:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        sub_issues_url = f"https://api.github.com/repos/{repo_name}/issues/{parent_issue_number}/sub_issues"

        sub_issue_url = f"https://api.github.com/repos/{repo_name}/issues/{sub_issue_number}"
        sub_response = requests.post(sub_issue_url, headers=headers)
        sub_issue_id = sub_response.json()['id']
        print(f"Sub Issue nodeID: {sub_issue_id}")
        # Now, link the sub-issue to the parent using the dedicated endpoint
        link_data = {
            "sub_issue_id": sub_issue_id
        }

        link_response = requests.post(sub_issues_url, headers=headers, data=json.dumps(link_data))
        link_response.raise_for_status()
        print(f"Status code: {link_response.status_code}")
        print(f"🔗 Sub-issue linked to parent issue #{parent_issue_number}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating or linking sub-issue '{sub_issue_number}': {e}")
            
# --- Script Usage Example ---
if __name__ == "__main__":
    # --- Configuration ---
    # Replace with your actual repository name (e.g., 'your_username/your_repo')
    REPO_NAME = "odockal/podman-desktop-qe"
    
    # --- Run the script ---
    run_testing_call(REPO_NAME, 30, 31)
