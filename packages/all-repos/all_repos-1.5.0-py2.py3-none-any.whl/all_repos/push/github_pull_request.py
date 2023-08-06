import collections
import json
import subprocess
import urllib.request

from all_repos import autofix_lib
from all_repos import git


Settings = collections.namedtuple('Settings', ('api_key', 'username', 'fork'))
Settings.__new__.__defaults__ = (False,)


def push(settings: Settings, branch_name: str) -> None:
    headers = {'Authorization': f'token {settings.api_key}'}

    remote_url = git.remote('.')
    _, _, repo_slug = remote_url.rpartition(':')

    if settings.fork:
        resp = urllib.request.urlopen(urllib.request.Request(
            f'https://api.github.com/repos/{repo_slug}/forks',
            headers=headers, method='POST',
        ))
        new_slug = json.loads(resp.read())['full_name']
        new_remote = remote_url.replace(repo_slug, new_slug)
        autofix_lib.run('git', 'remote', 'add', 'fork', new_remote)
        remote = 'fork'
        head = f'{settings.username}:{branch_name}'
    else:
        remote = 'origin'
        head = branch_name

    autofix_lib.run('git', 'push', remote, f'HEAD:{branch_name}', '--quiet')

    title = subprocess.check_output(('git', 'log', '-1', '--format=%s'))
    body = subprocess.check_output(('git', 'log', '-1', '--format=%b'))

    data = json.dumps({
        'title': title.decode().strip(),
        'body': body.decode().strip(),
        'base': 'master',
        'head': head,
    }).encode()

    resp = urllib.request.urlopen(urllib.request.Request(
        f'https://api.github.com/repos/{repo_slug}/pulls',
        data=data, headers=headers, method='POST',
    ))

    url = json.loads(resp.read())['html_url']
    print(f'Pull request created at {url}')
