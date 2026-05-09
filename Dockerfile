FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=60s --timeout=10s --retries=3 CMD python scripts/check_stale_data.py || exit 1

CMD ["python", "main.py"]
