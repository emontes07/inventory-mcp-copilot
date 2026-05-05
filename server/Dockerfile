FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server ./server

EXPOSE 8000

ENV MCP_TRANSPORT=streamable-http
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

CMD ["python3", "server/main.py"]
