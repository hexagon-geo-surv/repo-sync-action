# TODO:
# 1) Implement click skeleton
# 2) Options: -t/--token, -u/--user
# 3) Read all origin URLs from .github/workflows/main.yml
# 4) Foreach URL:
# 4a) Generate ssh key pair
# 4b) Refresh #REPO#_SSH_PRIVATE_KEY in secrets of repo-sync.git
# 4c) Refresh REPO_SYNC deploy key in fork/mirror.git
from typing import Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

GITHUB_API_URL = 'https://github.com.com/api/v3/'
GITHUB_ORGANIZATION = 'hexagon-geo-surv'


def main():
    for repo_name in get_repo_names():
        private_key, public_key = __generate_ssh_key_pair()

        set_secret(f'{repo_name.upper()}_SSH_PRIVATE_KEY', private_key)
        set_secret(f'{repo_name.upper()}_SSH_PUBLIC_KEY', public_key)

        set_deploy_key(repo_name, "REPO_SYNC", public_key)

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

    return private_key, public_key


def set_secret(name, value):
    pass


def set_deploy_key(repo_name, name, public_key):
    pass


if __name__ == '__main__':
    main()
