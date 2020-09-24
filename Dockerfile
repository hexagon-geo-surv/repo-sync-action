FROM alpine

RUN apk add --no-cache git openssh-client && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

COPY id_rsa.pub ~/.ssh/id_rsa.pub

RUN chmod 600 ~/.ssh/id_rsa && \
  chmod 644 ~/.ssh/id_rsa.pub

COPY repo-sync.sh /repo-sync.sh

ENTRYPOINT ["/repo-sync.sh"]
