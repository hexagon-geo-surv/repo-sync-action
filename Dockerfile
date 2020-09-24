FROM alpine

RUN apk add --no-cache git openssh-client && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN mkdir ~/.ssh && \
  chmod 700 ~/.ssh

COPY id_rsa.pub ~/.ssh/id_rsa.pub

RUN touch ~/.ssh/id_rsa && \
  chmod 600 ~/.ssh/id_rsa && \
  chmod 644 ~/.ssh/id_rsa.pub

COPY repo-sync.sh /repo-sync.sh

ENTRYPOINT ["/repo-sync.sh"]
