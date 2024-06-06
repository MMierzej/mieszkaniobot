FROM python:3.12-alpine as builder

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

WORKDIR /app

COPY requirements.txt .
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt


FROM python:3.12-alpine

RUN apk add --no-cache libffi openssl

RUN adduser mieszkaniobot \
    --home /home/mieszkaniobot \
    --disabled-password
RUN addgroup mieszkaniobot mieszkaniobot
USER mieszkaniobot

WORKDIR /home/mieszkaniobot

COPY --from=builder --chown=mieszkaniobot:mieszkaniobot \
     /app/.venv /home/mieszkaniobot/.venv
COPY --chown=mieszkaniobot:mieszkaniobot \
     mieszkaniobot.py /home/mieszkaniobot/mieszkaniobot.py

ENV PATH="/home/mieszkaniobot/.venv/bin:$PATH"

CMD ["python", "-u", "mieszkaniobot.py"]
