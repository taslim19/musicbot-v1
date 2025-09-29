FROM nikolaik/python-nodejs:python3.10-nodejs19-bullseye

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg neofetch \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt
RUN pip3 install uvicorn fastapi

CMD ["python3", "app.py"]
