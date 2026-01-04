FROM python:3.13-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create temp directory
RUN mkdir -p temp

# Set environment variable (will be overridden by platform)
ENV TELEGRAM_BOT_TOKEN=""

# Run the bot
CMD ["python", "bot.py"]
