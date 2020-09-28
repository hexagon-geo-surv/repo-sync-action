#!/bin/sh -e
ORIGIN=$1
UPSTREAM=$2
REPO_DIR=repo

echo "Setup directory..."
mkdir $REPO_DIR

echo "Setup SSH ..."
echo "$SSH_PRIVATE_KEY" > /root/.ssh/id_rsa
echo "$SSH_PUBLIC_KEY" > /root/.ssh/id_rsa.pub

echo "Clone origin $ORIGIN ..."
git clone $ORIGIN repo

cd $REPO_DIR

echo "Add remote upstream $UPSTREAM ..."
git remote add upstream $UPSTREAM

echo "Fetch from upstream $UPSTREAM ..."
git fetch upstream

echo "Push to origin $ORIGIN ..."
git push origin "refs/remotes/upstream/*:refs/heads/*" --force

echo "Push tags to origin $ORIGIN ..."
git push origin --tags --force

echo "Cleanup ..."
cd ..
rm -rf $REPO_DIR

echo "Successfully synced origin $ORIGIN from upstream $UPSTREAM"
