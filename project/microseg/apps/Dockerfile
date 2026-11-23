# campus-app:1.0  used by api, auth, admin and the ops pod
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY news.py api.py auth.py admin.py ./
RUN useradd --uid 1000 --create-home app
USER app
