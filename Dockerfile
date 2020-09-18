FROM alpine

RUN apk add --no-cache git openssh-client && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

COPY repo-sync.sh /repo-sync.sh

ENTRYPOINT ["/repo-sync.sh"]
