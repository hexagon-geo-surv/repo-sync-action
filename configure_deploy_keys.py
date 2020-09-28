import base64
import json
from base64 import b64encode
from typing import Tuple

import click
import requests
import yaml
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from nacl import encoding, public
from requests import codes

GITHUB_API_URL = 'https://api.github.com'
GITHUB_ORGANIZATION = 'hexagon-geo-surv'
JSON_HEADERS = {'Content-Type': 'application/json'}


@click.command()
@click.option('-r', '--repo', required=True, help='Name of the workflow repo storing the secrets')
@click.option('-u', '--user', required=True, envvar='GITHUB_USER', help='GitHub.com - User')
@click.option('-t', '--token', required=True, envvar='GITHUB_TOKEN', help='GitHub.com - Personal Access Token')
def main(repo: str, user: str, token: str) -> None:
    github_auth = user, token

    for repo_name in get_repo_names(repo, github_auth):
        print(f'Configuring {GITHUB_ORGANIZATION}/{repo_name}.git ... ', end='')

        private_key, public_key = __generate_ssh_key_pair()

        secret_name_prefix = repo_name.upper().replace('-', '_')
        set_secret(repo, f'{secret_name_prefix}_SSH_PRIVATE_KEY', private_key, github_auth)
        set_secret(repo, f'{secret_name_prefix}_SSH_PUBLIC_KEY', public_key, github_auth)

        set_deploy_key(repo_name, 'REPO_SYNC', public_key, github_auth)

        print(f'done!')

    print('Finished!')


def get_repo_names(repo: str, github_auth: Tuple) -> [str]:
    response = requests.get(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo}/contents/.github/workflows/main.yml',
                            auth=github_auth)

    if response.status_code != codes.ok:
        raise Exception(response.content)

    response = json.loads(response.content)
    workflow_file_content = base64.b64decode(response['content'])

    workflow_file = yaml.load(workflow_file_content, Loader=yaml.FullLoader)
    return [step['name'] for step in workflow_file['jobs']['repo-sync']['steps'] if 'name' in step]


def __generate_ssh_key_pair() -> Tuple:
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=4096)

    private_key = key.private_bytes(serialization.Encoding.PEM,
                                    serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption())

    public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                               serialization.PublicFormat.OpenSSH)

    return private_key.decode('utf-8'), public_key.decode('utf-8')


def set_secret(repo: str, secret_name: str, secret_value: str, github_auth: Tuple) -> None:
    # https://developer.github.com/v3/actions/secrets/#get-a-repository-public-key
    response = requests.get(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo}/actions/secrets/public-key',
                            auth=github_auth)

    if response.status_code != codes.ok:
        raise Exception(response.content)

    response = json.loads(response.content)
    public_key = response['key']
    key_id = response['key_id']

    # https://developer.github.com/v3/actions/secrets/#create-or-update-a-repository-secret
    response = requests.put(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo}/actions/secrets/{secret_name}',
                            auth=github_auth,
                            headers=JSON_HEADERS,
                            json={
                                'key_id': key_id,
                                'encrypted_value': __encrypt_secret(public_key, secret_value)
                            })

    if response.status_code != codes.created and response.status_code != codes.no_content:
        raise Exception(response.content)


def __encrypt_secret(public_key: str, secret_value: str) -> str:
    # https://developer.github.com/v3/actions/secrets/#example-encrypting-a-secret-using-python
    public_key = public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    return b64encode(encrypted).decode('utf-8')


def set_deploy_key(repo_name: str, deploy_key_name: str, deploy_key_value: str, github_auth: Tuple) -> None:
    # https://developer.github.com/v3/repos/keys/#list-deploy-keys
    response = requests.get(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo_name}/keys', auth=github_auth)

    if response.status_code != codes.ok:
        raise Exception(response.content)

    keys = json.loads(response.content)
    repo_sync_key_id = next(iter([key['id'] for key in keys if key['title'] == 'REPO_SYNC']), None)

    if repo_sync_key_id is not None:
        # https://developer.github.com/v3/repos/keys/#delete-a-deploy-key
        response = requests.delete(
            f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo_name}/keys/{repo_sync_key_id}', auth=github_auth)

        if response.status_code != codes.not_found and response.status_code != codes.no_content:
            raise Exception(response.content)

    # https://developer.github.com/v3/repos/keys/#create-a-deploy-key
    # POST /repos/:owner/:repo/keys
    response = requests.post(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/{repo_name}/keys',
                             auth=github_auth,
                             headers=JSON_HEADERS,
                             json={
                                 'title': deploy_key_name,
                                 'key': deploy_key_value,
                                 'read_only': False
                             })

    if response.status_code != codes.created:
        raise Exception(response.content)


if __name__ == '__main__':
    main()
