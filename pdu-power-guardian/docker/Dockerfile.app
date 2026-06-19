FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir numpy scikit-learn prometheus-client
COPY src/ src/
EXPOSE 9200
CMD ["python","src/exporter/prometheus_exporter.py"]
