#!/bin/bash

# Run /projects/ticker/ticker.py automatically on boot with cron.
# See documentation at https://github.com/cze1rice/ENGI301/tree/main/project_01 for setting up cron.

cd /var/lib/cloud9/projects/spotibox/ticker
sudo python3 ticker.py
