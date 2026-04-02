FROM public.ecr.aws/ubuntu/ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

# install packages
RUN apt-get update -y && apt-get install -y \
    git \
    make \
    unzip \
    curl \
    software-properties-common \
    mysql-client \
    pipx \
    pkg-config \
    vim

# configure environment variables
ENV EDITOR=vim

# install aws-cli
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" && unzip awscliv2.zip
RUN ./aws/install

# install rain
RUN curl -L -o /tmp/rain.zip https://github.com/aws-cloudformation/rain/releases/download/v1.23.0/rain-v1.23.0_linux-arm64.zip
RUN unzip /tmp/rain.zip
RUN mv ./rain-v1.23.0_linux-arm64/rain /usr/local/bin/rain

# install python
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update -y && \
    apt-get install -y python3.13 python3.13-venv python3.13-dev python3-pip

# install cfn-lint
RUN pip install cfn-lint

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV UV_LINK_MODE=copy

# configure bash aliases
RUN echo "alias ls='ls -alh'" >> /root/.bashrc
RUN echo "alias gco='git checkout'" >> /root/.bashrc
RUN echo "alias gs='git status'" >> /root/.bashrc
RUN echo "alias ga='git add .'" >> /root/.bashrc
RUN echo "alias gc='git commit'" >> /root/.bashrc
