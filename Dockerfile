#FROM python:3.10-slim
FROM lscr.io/linuxserver/chromium:latest

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    xvfb \
    libnss3 \
    libgbm1 \
    libasound2 \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Google Chrome (The modern way without apt-key)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .

COPY tests/ ./tests/

# Set display environment variable for Xvfb
ENV DISPLAY=:99

# Use a shell script as a bridge to launch Xvfb and then your app
# This avoids the JSONArgsRecommended warning
#RUN echo 'Xvfb :99 -screen 0 1920x1080x24 & uvicorn main:app --host 0.0.0.0 --port 8003' > entrypoint.sh && chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]