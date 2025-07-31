FROM siwarakkari/base-tower-agent

COPY . .

CMD ["python", "worker/main.py"]
