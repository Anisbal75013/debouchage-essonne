#!/bin/bash
cd /sessions/happy-beautiful-cray/mnt/Assainissement91
node node_modules/.bin/astro build > build_complete.log 2>&1
echo "BUILD DONE: exit=$?" >> build_complete.log
