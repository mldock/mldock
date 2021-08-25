#!/usr/bin/env bash
script_name="$1"
shift
if [ "$script_name" = "train" ]; then
    python ./src/container/training/train.py $@
else
    python ./src/container/prediction/serve.py
fi
