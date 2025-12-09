FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

ARG DOCKER_UID=1000
ARG DOCKER_GID=1000
ARG DOCKER_USER=user
ARG HOME=/home/${DOCKER_USER}

RUN groupadd -g $DOCKER_GID $DOCKER_USER \
    && useradd --uid $DOCKER_UID --gid $DOCKER_GID -m $DOCKER_USER \
    && echo "$DOCKER_USER ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

## Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES=all
ENV NVIDIA_VISIBLE_DEVICES=all

## Uncomment this command to change apt source if you encouter connection issues in China mainland
# RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && \
#     sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

########################################################
## Install dependencies
########################################################
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    ssh \
    x11-apps \
    mesa-utils \
    ninja-build \
    vulkan-tools \
    libglu1 \
    # ref: https://askubuntu.com/a/1072878
    libglib2.0-0 \
    # ref: https://stackoverflow.com/a/76778289
    libxrandr2 \
    vim \
    && apt clean
RUN apt install -y -o Dpkg::Options::="--force-confold" sudo

## Install git lfs
RUN apt install -y git-lfs

## Install VirtualGL installation to share GUI remotely
## Test with: vglrun +v glxgears
## Show details with: vglrun -d egl glxinfo -B
RUN apt install -y --no-install-recommends libxtst6 libxv1 libturbojpeg && apt clean
RUN wget https://github.com/VirtualGL/virtualgl/releases/download/3.1.4/virtualgl_3.1.4_amd64.deb
RUN dpkg -i virtualgl_3.1.4_amd64.deb
RUN echo "export QT_X11_NO_MITSHM=1" >> ${HOME}/.bashrc
RUN echo "export VGL_DISPLAY=egl" >> ${HOME}/.bashrc
RUN echo "export VGL_CLIENT=localhost" >> ${HOME}/.bashrc
RUN echo "export VGL_QUAL=100" >> ${HOME}/.bashrc
RUN echo "export VGL_FPS=60" >> ${HOME}/.bashrc
RUN echo "export VGL_COMPRESS=0" >> ${HOME}/.bashrc
RUN echo "export PYOPENGL_PLATFORM=egl" >> ${HOME}/.bashrc
# Deactivate importing viser as viewer to pyroki
RUN echo "export PYROKI_ENABLE_VIEWER=0" >> ${HOME}/.bashrc

## Switch user
USER ${DOCKER_USER}
WORKDIR ${HOME}

## Use bash instead of sh
SHELL ["/bin/bash", "-c"]

## Install conda
RUN wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh" \
    && bash "Miniforge3-$(uname)-$(uname -m).sh" -b -p ${HOME}/conda \
    && rm "Miniforge3-$(uname)-$(uname -m).sh"
ENV PATH=${HOME}/conda/condabin:$PATH

## Initialize all future shells
RUN conda init bash \
    && mamba shell init --shell bash

## Install uv
RUN wget https://astral.sh/uv/install.sh \
    && bash install.sh \
    && rm install.sh
ENV PATH=${HOME}/.local/bin:$PATH

## Clone pyroki for later installation
RUN mkdir -p ${HOME}/packages \
    && git clone https://github.com/RoboticManipulation/pyroki.git ${HOME}/packages/pyroki

## Install CuRoBo
# git submodule update --init --recursive
# cd third_party/curobo

########################################################
## Clone RoboVerse
########################################################
## Option 1: Clone from github
# TODO: remove this when released
COPY --chown=${DOCKER_USER} id_ed25519 ${HOME}/.ssh/id_ed25519
COPY --chown=${DOCKER_USER} id_ed25519.pub ${HOME}/.ssh/id_ed25519.pub
RUN ssh-keyscan github.com >> ${HOME}/.ssh/known_hosts
# RUN git clone --depth 1 --branch metasim git@github.com:RoboVerseOrg/RoboVerse.git ${HOME}/RoboVerse
## Option 2: Copy necessary files for building conda environment
COPY --chown=${DOCKER_USER} ./metasim ${HOME}/RoboVerse/metasim
COPY --chown=${DOCKER_USER} ./third_party ${HOME}/RoboVerse/third_party
COPY --chown=${DOCKER_USER} ./roboverse_pack ${HOME}/RoboVerse/roboverse_pack
COPY --chown=${DOCKER_USER} ./pyproject.toml ${HOME}/RoboVerse/pyproject.toml
WORKDIR ${HOME}/RoboVerse

########################################################
## Check ssh access
########################################################
# RUN --mount=type=ssh \
#     ssh-add -l || echo "ssh-add failed or agent has no identities"

########################################################
## Clone GeoSemPlace
########################################################
RUN if [ ! -d ${HOME}/RoboVerse/third_party/geo_sem_place ]; then \
        git clone --branch main \
            git@gitlab.ipb.uni-bonn.de:robotic_manipulation/geo_sem_place/geo_sem_place.git \
            ${HOME}/RoboVerse/third_party/geo_sem_place; \
    fi

########################################################
## Clone GeoSemPlace Dataset
########################################################
RUN if [ ! -d ${HOME}/RoboVerse/third_party/geo_sem_place_dataset ]; then \
        git clone --branch main \
            git@hf.co:datasets/robotic-manipulation/geo_sem_place_dataset \
            ${HOME}/RoboVerse/third_party/geo_sem_place_dataset; \
    fi

########################################################
## Clone SAM3
########################################################
RUN if [ ! -d ${HOME}/RoboVerse/third_party/sam3 ]; then \
        git clone --branch master \
            git@github.com:RoboticManipulation/sam3.git \
            ${HOME}/RoboVerse/third_party/sam3; \
    fi

########################################################
## Install isaaclab, mujoco, sapien3, pybullet
########################################################

## Create conda environment
RUN mamba create -n metasim python=3.10 -y \
    && mamba clean -a -y
RUN echo "mamba activate metasim" >> ${HOME}/.bashrc

## Pip install
RUN cd ${HOME}/RoboVerse \
    && eval "$(mamba shell hook --shell bash)" \
    && mamba activate metasim \
    && uv pip install -e ".[isaaclab211,mujoco,sapien3,pybullet]" \
    && uv pip install -e "${HOME}/packages/pyroki/" \
    # && uv pip install -e "${HOME}/third_party/curobo/" --no-build-isolation \
    && uv pip install pygame \
    && uv cache clean

# Test proxy connection
# RUN wget --method=HEAD --output-document - https://www.google.com/

## Install IsaacLab v1.4.1
# RUN mkdir -p ${HOME}/packages \
#     && cd ${HOME}/packages \
#     && eval "$(mamba shell hook --shell bash)" \
#     && mamba activate metasim \
#     && git clone --depth 1 --branch v1.4.1 https://github.com/isaac-sim/IsaacLab.git IsaacLab \
#     && cd IsaacLab \
#     && sed -i '/^EXTRAS_REQUIRE = {$/,/^}$/c\EXTRAS_REQUIRE = {\n    "sb3": [],\n    "skrl": [],\n    "rl-games": [],\n    "rsl-rl": [],\n    "robomimic": [],\n}' source/extensions/omni.isaac.lab_tasks/setup.py \
#     && ./isaaclab.sh -i \
#     && pip cache purge

## Install IsaacLab v2.1.0
# RUN mkdir -p ${HOME}/packages \
#     && cd ${HOME}/packages \
#     && eval "$(mamba shell hook --shell bash)" \
#     && mamba activate metasim \
#     && git clone --depth 1 --branch v2.1.0 https://github.com/isaac-sim/IsaacLab.git IsaacLab2 \
#     && cd IsaacLab2 \
#     && sed -i '/^EXTRAS_REQUIRE = {/,/^}$/c\EXTRAS_REQUIRE = {\n    "sb3": [],\n    "skrl": [],\n    "rl-games": [],\n    "rsl-rl": [],\n}' source/isaaclab_rl/setup.py \
#     && sed -i 's/if platform\.system() == "Linux":/if False:/' source/isaaclab_mimic/setup.py \
#     && ./isaaclab.sh -i \
#     && pip cache purge

## Install IsaacLab v2.1.1
RUN mkdir -p ${HOME}/packages \
    && cd ${HOME}/packages \
    && eval "$(mamba shell hook --shell bash)" \
    && mamba activate metasim \
    && git clone --depth 1 --branch v2.1.1 https://github.com/isaac-sim/IsaacLab.git IsaacLab211 \
    && cd IsaacLab211 \
    && sed -i '/^EXTRAS_REQUIRE = {/,/^}$/c\EXTRAS_REQUIRE = {\n    "sb3": [],\n    "skrl": [],\n    "rl-games": [],\n    "rsl-rl": [],\n}' source/isaaclab_rl/setup.py \
    && sed -i 's/if platform\.system() == "Linux":/if False:/' source/isaaclab_mimic/setup.py \
    && ./isaaclab.sh -i none \
    && pip cache purge

## Install IsaacLab v2.2.1
# RUN mkdir -p ${HOME}/packages \
#     && cd ${HOME}/packages \
#     && eval "$(mamba shell hook --shell bash)" \
#     && mamba activate metasim \
#     && git clone --depth 1 --branch v2.2.1 https://github.com/isaac-sim/IsaacLab.git IsaacLab221 \
#     && cd IsaacLab221 \
#     && sed -i '/^EXTRAS_REQUIRE = {/,/^}$/c\EXTRAS_REQUIRE = {\n    "sb3": [],\n    "skrl": [],\n    "rl-games": [],\n    "rsl-rl": [],\n}' source/isaaclab_rl/setup.py \
#     && sed -i 's/if platform\.system() == "Linux":/if False:/' source/isaaclab_mimic/setup.py \
#     && ./isaaclab.sh -i none \
#     && pip cache purge

# Install GeoSemPlace
RUN cd ${HOME}/RoboVerse/third_party \
    && eval "$(mamba shell hook --shell bash)" \
    && mamba activate metasim \
    && uv pip install --upgrade pip setuptools wheel \
    && uv pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 \
    && uv pip install -e "$HOME/RoboVerse/third_party/sam3[notebooks]" \
    && uv pip install pandas \
    && uv pip install -r "$HOME/RoboVerse/third_party/geo_sem_place/requirements.txt" \
    && uv pip install -e "$HOME/RoboVerse/third_party/geo_sem_place" \
    && uv cache clean

########################################################
## Install genesis
########################################################
# RUN mamba create -n metasim_genesis python=3.11 -y \
#     && mamba clean -a -y
# RUN cd ${HOME}/RoboVerse \
#     && eval "$(mamba shell hook --shell bash)" \
#     && mamba activate metasim_genesis \
#     && uv pip install -e ".[genesis]" \
#     && uv pip install -e "${HOME}/packages/pyroki/" \
#     # && uv pip install -e "${HOME}/third_party/curobo/" --no-build-isolation \
#     && uv pip install pygame \
#     && uv cache clean

########################################################
## Install isaacgym
########################################################
# RUN mamba create -n metasim_isaacgym python=3.8 -y \
#     && mamba clean -a -y
# RUN mkdir -p ${HOME}/packages \
#     && cd ${HOME}/packages \
#     && wget https://developer.nvidia.com/isaac-gym-preview-4 \
#     && tar -xf isaac-gym-preview-4 \
#     && rm isaac-gym-preview-4
# RUN find ${HOME}/packages/isaacgym/python -type f -name "*.py" -exec sed -i 's/np\.float/np.float32/g' {} +
# RUN cd ${HOME}/RoboVerse \
#     && eval "$(mamba shell hook --shell bash)" \
#     && mamba activate metasim_isaacgym \
#     && uv pip install -e ".[isaacgym]" "isaacgym @ ${HOME}/packages/isaacgym/python" \
#     && uv pip install pygame \
#     && uv cache clean
# ## Fix error: libpython3.8.so.1.0: cannot open shared object file
# ## Refer to https://stackoverflow.com/a/75872751
# RUN export CONDA_PREFIX=${HOME}/conda/envs/metasim_isaacgym \
#     && mkdir -p $CONDA_PREFIX/etc/conda/activate.d \
#     && echo "export OLD_LD_LIBRARY_PATH=\$LD_LIBRARY_PATH && export LD_LIBRARY_PATH=$CONDA_PREFIX/lib/:\$LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh \
#     && mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d \
#     && echo "export LD_LIBRARY_PATH=\$OLD_LD_LIBRARY_PATH && unset OLD_LD_LIBRARY_PATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
# ## Fix error: No such file or directory: '.../lib/python3.8/site-packages/isaacgym/_bindings/src/gymtorch/gymtorch.cpp'
# RUN mkdir -p ${HOME}/conda/envs/metasim_isaacgym/lib/python3.8/site-packages/isaacgym/_bindings/src \
#     && cp -r ${HOME}/packages/isaacgym/python/isaacgym/_bindings/src/gymtorch ${HOME}/conda/envs/metasim_isaacgym/lib/python3.8/site-packages/isaacgym/_bindings/src/gymtorch

########################################################
## Helpful message
########################################################
# RUN echo 'echo "Remember to run: xhost +local:docker on the host to enable GUI applications."' >> ${HOME}/.bashrc
