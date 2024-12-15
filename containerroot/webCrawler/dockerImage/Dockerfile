FROM python:3.9

WORKDIR /crawler
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create directories for logs and output
RUN mkdir -p /crawler/logs
RUN mkdir -p /crawler/output

COPY . .