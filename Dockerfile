FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" spider

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY app.py .
COPY templates ./templates
COPY static ./static

RUN chown -R spider:spider /app

USER spider

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
