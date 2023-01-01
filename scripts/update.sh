#!/usr/bin/env bash

set -eu

cd ~/eatonphil.com
git reset --hard
git pull

sudo cp Caddyfile /etc/caddy/Caddyfile
sudo service caddy restart
