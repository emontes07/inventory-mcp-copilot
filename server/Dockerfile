FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV PORT=8000

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./main.py
COPY tools ./tools
COPY data ./data
COPY widgets ./widgets
COPY static ./static

EXPOSE 8000

CMD ["python3", "main.py"]