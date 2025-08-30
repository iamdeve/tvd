#!/bin/bash
# Activate virtual environment
source yt-env/bin/activate

# Set temp dir
#export TWITTER_DOWNLOADER_TEMP_DIR="/home/ubuntu/video_downloads"

# Start Gunicorn (foreground mode, stops with Ctrl+C)

gunicorn -w 1 -b 127.0.0.1:6000 tw_api_v4:app \
  --access-logfile /home/ubuntu/logs/gunicorn-access.log \
  --error-logfile /home/ubuntu/logs/gunicorn-error.log