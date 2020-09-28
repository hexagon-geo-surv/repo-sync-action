FROM alpine

RUN apk add --no-cache git openssh-client && \
  echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN mkdir /root/.ssh && \
  chmod 700 /root/.ssh && \
  touch /root/.ssh/id_rsa && \
  chmod 600 /root/.ssh/id_rsa && \
  touch /root/.ssh/id_rsa.pub && \
  chmod 644 /root/.ssh/id_rsa.pub

COPY repo-sync.sh /repo-sync.sh

ENTRYPOINT ["/repo-sync.sh"]
