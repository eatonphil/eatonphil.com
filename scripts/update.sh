#!/usr/bin/env bash

set -eu

cd ~/eatonphil.com
git reset --hard
git pull
sudo rm -rf /usr/share/caddy/*
sudo mv {home,lists,notes} /usr/share/caddy/
sudo chown -R caddy:caddy /usr/share/caddy/
sudo restorecon -r /usr/share/caddy/
