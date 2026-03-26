FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pr1.py .
EXPOSE 8020
CMD ["gunicorn", "pr1:app", "--bind", "0.0.0.0:8020"]