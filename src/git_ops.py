import subprocess


def check_repo_update(repo_path):
    try:
        cmd = ['git', 'pull', '--dry-run']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        output = result.stdout.lower()
        if 'already up to date' in output:
            return False
        elif 'fatal' in output or 'error' in output:
            return None
        else:
            return True
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None


def pull_repo(repo_path):
    try:
        cmd = ['git', 'pull']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            formatted_output = output.replace('\n', ' ').replace('\r', '')
            return formatted_output
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None
