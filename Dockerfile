# Use official Airflow image as base
FROM apache/airflow:2.8.0-python3.11

# Switch to root to install system packages
USER root

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install Python packages
RUN pip install --no-cache-dir \
    selenium==4.15.0 \
    webdriver-manager==4.0.1 \
    beautifulsoup4==4.12.2 \
    lxml==5.1.0 \
    apache-airflow-providers-amazon==8.13.0

# Set Chrome binary location
ENV CHROME_BIN=/usr/bin/google-chrome-stable
