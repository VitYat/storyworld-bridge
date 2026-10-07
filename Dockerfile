FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV STORYWORLD_HOST=0.0.0.0
ENV STORYWORLD_PORT=8765
ENV PYTHONUNBUFFERED=1

EXPOSE 8765

CMD ["python", "server.py"]
