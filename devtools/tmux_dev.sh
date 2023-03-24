#!/bin/bash
# see https://www.peterdebelak.com/blog/tmux-scripting/

cd /data/ngs_pipeline/app

tmux new -s ngs_pipeline_dev -d
tmux send-keys -t ngs_pipeline_dev 'e src/app/app.py' C-m
tmux new-window -t ngs_pipeline
#tmux rename-window -t ngs_pipeline couchdb

# is by default horizontal
# -v splits vertical
tmux rename-window -t ngs_pipeline_dev servers
tmux split-window -t ngs_pipeline_dev
tmux split-window -t ngs_pipeline_dev
tmux split-window -t ngs_pipeline_dev

tmux select-pane -t 0
tmux send-keys -t ngs_pipeline_dev '/data/fhoelsch/run_couchdb.sh' C-m

tmux select-pane -t 1
tmux send-keys -t ngs_pipeline_dev './run_rabbitmq.sh' C-m

tmux select-pane -t 2
tmux send-keys -t ngs_pipeline_dev 'source /data/fhoelsch/.venv/bin/activate' C-m

tmux select-pane -t 3
tmux send-keys -t ngs_pipeline_dev 'source /data/fhoelsch/.venv/bin/activate' C-m

tmux attach -t ngs_pipeline
