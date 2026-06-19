FROM python:3.9-slim

# FFmpeg ইনস্টল করা বাধ্যতামূলক
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

# লাইব্রেরি ইনস্টল করা
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
