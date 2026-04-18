FROM python:3.12-slim
WORKDIR /app
COPY piprequirements.txt .
RUN pip install -r piprequirements.txt
COPY . .
CMD ["python", "-m", "bot.bot_runner"]
