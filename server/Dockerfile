FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server ./server

EXPOSE 8000

ENV FASTMCP_TRANSPORT=streamable-http
ENV PYTHONUNBUFFERED=1

CMD ["python", "server/main.py"]
