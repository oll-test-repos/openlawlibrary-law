import sys
import json
from oll.publish.server.Host import AuthRepo
from oll.publish.server.cloudfront import invalidate_cloudfront_and_notify


def process_stdin():
   return sys.stdin.read()

def do_something(update_data, state, config):

    transient = state["transient"]
    persistent = state["persistent"]
    auth_repos_data = update_data["auth_repos"]
    config_repos_data = config.pop("repos")
    for auth_repo_data in auth_repos_data:
        repo_update_data = auth_repo_data["update"]
        repo_data = repo_update_data["auth_repo"]["data"]
        config_repo_data = config_repos_data.get(repo_data.get("name"))
        repo_data |= config
        repo_data |= config_repo_data
        auth_repo = AuthRepo.from_json_dict(repo_data)
        persistent, transient = auth_repo.pull_preview_and_development(repo_update_data, persistent, transient)
        invalidate_cloudfront_and_notify(auth_repo, transient)
        state["transient"] = transient
        state["persistent"] = persistent

    return state

def send_state(state):
    # printed data will be sent from the script back to the updater
    print(json.dumps(state))


if __name__ == '__main__':
    data = process_stdin()
    data = json.loads(data)
    config = data["config"]
    state = do_something(data["update"], data["state"], config)
    send_state(state)