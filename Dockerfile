FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY opusjev ./opusjev
RUN pip install --no-cache-dir .
VOLUME ["/app/runs"]
ENTRYPOINT ["opusjev"]
CMD ["paper", "--provider", "jev", "--run-dir", "runs/paper"]
