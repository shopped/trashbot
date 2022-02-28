#!/bin/bash

if [ $# -eq 0 ]; then
  DATA_DIR="./"
else
  DATA_DIR="$1"
fi

# Install Python dependencies
python3 -m pip install pip --upgrade
python3 -m pip install -r requirements.txt

# Download TF Lite models
FILE=${DATA_DIR}/movenet_lightning.tflite
if [ ! -f "$FILE" ]; then
  curl \
    -L 'https://tfhub.dev/google/lite-model/movenet/singlepose/lightning/tflite/float16/4?lite-format=tflite' \
    -o ${FILE}
fi

FILE=${DATA_DIR}/movenet_thunder.tflite
if [ ! -f "$FILE" ]; then
  curl \
    -L 'https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/tflite/float16/4?lite-format=tflite' \
    -o ${FILE}
fi

echo -e "Downloaded files are in ${DATA_DIR}"
