FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Blender dependencies including OpenGL/EGL
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1-mesa \
    libgbm1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libxi6 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxcb-xkb1 \
    libxcb-render-util0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb1 \
    libx11-6 \
    libxxf86vm1 \
    libxfixes3 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Blender
RUN wget https://download.blender.org/release/Blender5.0/blender-5.0.1-linux-x64.tar.xz \
    && tar -xf blender-5.0.1-linux-x64.tar.xz \
    && mv blender-5.0.1-linux-x64 /opt/blender \
    && ln -s /opt/blender/blender /usr/local/bin/blender \
    && rm blender-5.0.1-linux-x64.tar.xz

WORKDIR /workspace

COPY engine-dataset-gen.blend dataset-gen.py /workspace/

ENV NUM_SAMPLES=2
# Force CPU rendering to avoid GPU issues
ENV CYCLES_DEVICE=CPU

CMD ["blender", "--background", "engine-dataset-gen.blend", "--python", "dataset-gen.py"]