import os
import requests
import sys

# Replace with your GitHub Personal Access Token (PAT)
# It's highly recommended to set this as an environment variable
# export GITHUB_TOKEN="your_pat_here"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("Error: GITHUB_TOKEN environment variable not set.")
    sys.exit(1)

def get_user_teams(username: str, organizations: list) -> list:
    """
    Checks if a user is a member of any team in the specified organizations.

    Args:
        username (str): The GitHub username to check.
        organizations (list): A list of GitHub organization names.

    Returns:
        list: A list of teams the user is a member of.
    """
    all_teams = []
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    print(f"Checking for user '{username}' in organizations: {', '.join(organizations)}")
    print("-" * 50)

    for org in organizations:
        try:
            # First, get a list of all teams in the organization
            teams_url = f"https://api.github.com/orgs/{org}/teams"
            response = requests.get(teams_url, headers=headers)
            response.raise_for_status()
            teams = response.json()

            if not teams:
                print(f"No teams found in organization '{org}'.")
                continue

            # For each team, check if the user is a member
            for team in teams:
                team_name = team['slug']
                team_id = team['id']
                team_members_url = f"https://api.github.com/orgs/{org}/teams/{team_name}/memberships/{username}"
                member_response = requests.get(team_members_url, headers=headers)

                # Check if the user is a member of the team
                if member_response.status_code == 200:
                    # The response body contains the membership status.
                    # 'state' can be 'active' or 'pending'
                    membership_data = member_response.json()
                    if membership_data.get('state') == 'active':
                        team_info = {
                            "organization": org,
                            "team_name": team_name,
                            "id": team_id
                        }
                        all_teams.append(team_info)
                        print(f"✅ Found user '{username}' in team '{org}/{team_name}'.")

                elif member_response.status_code == 404:
                    # User is not a member of this specific team
                    pass
                else:
                    # Handle other potential errors like API rate limits
                    print(f"⚠️ Error checking team '{org}/{team_name}': {member_response.status_code} - {member_response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ An error occurred with organization '{org}': {e}")

    return all_teams

# --- Example Usage ---
if __name__ == "__main__":
    # Example user and organizations
    target_user = "rostalan"  # Replace with the user you want to check
    target_orgs = ["podman-desktop", "redhat-developer", "containers", "jbosstools"]  # Replace with the organizations you want to check

    # Get the list of teams
    teams_list = get_user_teams(target_user, target_orgs)

    print("\n" + "="*50)
    if teams_list:
        print(f"🎉 Summary: User '{target_user}' is a member of the following teams:")
        for team in teams_list:
            print(f"{team['organization']}/{team['team_name']}")
    else:
        print(f"Summary: User '{target_user}' is not a member of any teams in the specified organizations.")

