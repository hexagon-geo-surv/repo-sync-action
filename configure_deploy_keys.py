import json
from base64 import b64encode
from typing import Tuple

import click
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from nacl import encoding, public
from requests import codes

GITHUB_API_URL = 'https://api.github.com'
GITHUB_ORGANIZATION = 'hexagon-geo-surv'
JSON_HEADERS = {'Content-Type': 'application/json'}


@click.command()
@click.option('-u', '--user', required=True, envvar='GITHUB_USER', help='GitHub.com - User')
@click.option('-t', '--token', required=True, envvar='GITHUB_TOKEN', help='GitHub.com - Personal Access Token')
def main(user: str, token: str) -> None:
    github_auth = user, token

    for repo_name in get_repo_names():
        private_key, public_key = __generate_ssh_key_pair()

        set_secret(f'{repo_name.upper()}_SSH_PRIVATE_KEY', private_key, github_auth)
        set_secret(f'{repo_name.upper()}_SSH_PUBLIC_KEY', public_key, github_auth)

        set_deploy_key(repo_name, "REPO_SYNC", public_key, github_auth)

        print(f'Configured "{GITHUB_ORGANIZATION}/{repo_name}.git"')

    print('Done!')


def get_repo_names() -> [str]:
    # TODO: Read repo names from .github/workflows/main.yml
    return ['bitbake']


def __generate_ssh_key_pair() -> Tuple:
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=4096)

    private_key = key.private_bytes(serialization.Encoding.PEM,
                                    serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption())

    public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                               serialization.PublicFormat.OpenSSH)

    return private_key.decode('utf-8'), public_key.decode('utf-8')


def set_secret(secret_name: str, secret_value: str, github_auth: Tuple) -> None:
    # https://developer.github.com/v3/actions/secrets/#get-a-repository-public-key
    response = requests.get(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/repo-sync/actions/secrets/public-key',
                            auth=github_auth)

    if response.status_code != codes.ok:
        raise Exception(response.content)

    response = json.loads(response.content)
    public_key = response['key']
    key_id = response['key_id']

    # https://developer.github.com/v3/actions/secrets/#create-or-update-a-repository-secret
    response = requests.put(f'{GITHUB_API_URL}/repos/{GITHUB_ORGANIZATION}/repo-sync/actions/secrets/{secret_name}',
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
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode('utf-8'), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
    return b64encode(encrypted).decode('utf-8')


def set_deploy_key(repo_name: str, deploy_key_name: str, deploy_key_value: str, github_auth: Tuple) -> None:
    # https://developer.github.com/v3/repos/keys/#delete-a-deploy-key
    # DELETE /repos/:owner/:repo/keys/:key_id
    # TODO

    # https://developer.github.com/v3/repos/keys/#create-a-deploy-key
    # POST /repos/:owner/:repo/keys
    # title
    # key
    # read_only
    # TODO
    pass


if __name__ == '__main__':
    main()
