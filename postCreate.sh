#!/bin/bash
echo "[postCreate] Running postCreate.sh as $(whoami) in $PWD"

# Make sure conda/mamba/uv are on PATH and shell hooks are available
source /home/$(whoami)/.bashrc

# Ensure we’re in the RoboVerse workspace
cd "$HOME/RoboVerse"

############################
# Clone repos if missing
############################

echo "[postCreate] Check and clone missing repositories."

if [ ! -d "$HOME/RoboVerse/third_party/geo_sem_place/.git" ]; then
    echo "[postCreate] Cloning geo_sem_place..."
    git clone --branch main \
        git@gitlab.ipb.uni-bonn.de:robotic_manipulation/geo_sem_place/geo_sem_place.git \
        "$HOME/RoboVerse/third_party/geo_sem_place"
# else
#     echo "[postCreate] geo_sem_place already present, skipping clone."
fi

if [ ! -d "$HOME/RoboVerse/third_party/geo_sem_place_dataset/.git" ]; then
    echo "[postCreate] Cloning geo_sem_place_dataset..."
    git clone --branch main \
        git@hf.co:datasets/robotic-manipulation/geo_sem_place_dataset \
        "$HOME/RoboVerse/third_party/geo_sem_place_dataset"
# else
#     echo "[postCreate] geo_sem_place_dataset already present, skipping clone."
fi

if [ ! -d "$HOME/RoboVerse/third_party/sam3/.git" ]; then
    echo "[postCreate] Cloning sam3..."
    git clone --branch master \
        git@github.com:RoboticManipulation/sam3.git \
        "$HOME/RoboVerse/third_party/sam3"
# else
#     echo "[postCreate] sam3 already present, skipping clone."
fi

echo "[postCreate] Done."