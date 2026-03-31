import os


def validate_repo_path(repo_path):
    if not os.path.exists(repo_path):
        return False
    if not os.path.isdir(repo_path):
        return False
    git_path = os.path.join(repo_path, '.git')
    return os.path.exists(git_path)


def extract_repo_name(repo_path):
    if not repo_path:
        return ""
    repo_path = repo_path.rstrip(os.sep)
    return os.path.basename(repo_path)


def format_update_message(message):
    if not message:
        return ""
    return message.replace('\n', ' ').replace('\r', '')
