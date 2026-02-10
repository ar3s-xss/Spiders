FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# create non-root user
RUN adduser --disabled-password --gecos "" spider

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application
COPY app.py .
COPY templates ./templates
COPY static ./static

# create persistent data directory
RUN mkdir /data && chown spider:spider /data

# fix permissions
RUN chown -R spider:spider /app

USER spider

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
