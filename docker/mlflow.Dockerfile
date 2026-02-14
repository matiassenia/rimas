FROM python:3.11-slim

WORKDIR /app

RUN pip install mlflow psycopg2-binary

EXPOSE 5000

ENTRYPOINT ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
CMD ["--backend-store-uri", "postgresql://rimas:rimas@postgres:5432/rimas", "--default-artifact-root", "/mlflow/artifacts"]
