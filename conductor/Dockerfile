FROM python:3.10-alpine

WORKDIR /app

# Install dependencies.
ADD requirements.txt /app
ADD nodes.txt /app

RUN cd /app && \
    pip install -r requirements.txt

# Add actual source code.
ADD main.py /app


CMD ["python", "main.py"]
