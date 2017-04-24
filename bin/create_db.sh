#!/bin/sh

#first arg username , second arg database name
cd /
sudo -u  postgres createuser "$1";
sudo -u  postgres createdb "$2" --owner="$1";


