#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "Установка Askard Zone..."
pkg update -y && pkg install -y python git
pip install requests beautifulsoup4 colorama --break-system-packages
cd "$(dirname "$0")"
python askard.py