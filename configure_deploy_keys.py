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


def main():
    ssh_keys = __generate_ssh_keys()
    private_key = ssh_keys[0]
    public_key = ssh_keys[1]

    print(private_key)
    print(public_key)


def __generate_ssh_keys() -> Tuple:
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=4096)

    private_key = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption())

    public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH,
                                               serialization.PublicFormat.OpenSSH)

    return private_key, public_key


if __name__ == '__main__':
    main()
