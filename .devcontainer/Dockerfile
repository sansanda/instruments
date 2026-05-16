FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml .
COPY README.md .

RUN pip install --upgrade pip

CMD ["/bin/bash"]