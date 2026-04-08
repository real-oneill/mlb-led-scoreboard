#!/bin/bash
cd /home/pi/mlb-led-scoreboard
sudo nohup python main.py \
  --led-gpio-mapping="adafruit-hat-pwm" \
  --led-rows=16 \
  --led-cols=64 \
  --led-slowdown-gpio=2 \
  --led-no-hardware-pulse=1 \
  > logs/mlbled.log 2>&1 &
echo "Scoreboard started. Logs at logs/mlbled.log"
