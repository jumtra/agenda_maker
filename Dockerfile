FROM nvcr.io/nvidia/cuda:11.7.0-cudnn8-devel-ubuntu22.04
ARG HF_TOKEN
ENV PYTHONUNBUFFERED=1 
ENV HF_TOKEN=$HF_TOKEN
# SYSTEM
RUN apt-get update --yes --quiet && DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    software-properties-common \
    build-essential apt-utils \
    wget curl vim git ca-certificates kmod libssl-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*



# PYTHON 3.10
RUN add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update --yes --quiet
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3.10-lib2to3 \
    python3.10-gdbm \
    python3.10-tk \
    pip

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 999 \
    && update-alternatives --config python3 && ln -s /usr/bin/python3 /usr/bin/python



# Set the locale to Japanese (ja_JP.UTF-8) and configure it to be non-interactive
RUN apt-get update && apt-get install -y language-pack-ja && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8

# Set the default locale environment variables
ENV LANGUAGE ja_JP:en
ENV LC_ALL ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" keyboard-configuration\
    python3-pip \
    man \
    cmake \
    make \
    ffmpeg  \
    && apt-get -y clean all
RUN python -m pip install --upgrade pip && python -m pip install poetry

# GET AGENDA MAKER
# GET LLM
WORKDIR /home/
RUN git clone https://github.com/jumtra/agenda_maker.git
WORKDIR /home/agenda_maker/
RUN poetry config installer.max-workers 10 && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi -vvv
RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 python3 -m pip install llama-cpp-python==0.1.83 --no-cache-dir
RUN python -c "from huggingface_hub._login import _login; _login(token='$HF_TOKEN', add_to_git_credential=False)"
COPY ELYZA-japanese-Llama-2-7b-fast-instruct-q4_0.gguf ELYZA-japanese-Llama-2-7b-fast-instruct-q4_0.gguf
# for Gradio
EXPOSE 6006
