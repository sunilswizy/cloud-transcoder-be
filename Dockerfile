FROM 567995762001.dkr.ecr.us-east-1.amazonaws.com/cloud-transcoder/base-image:latest

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app/main.py"]