FROM siwarakkari/base-tower-agent

COPY . .

CMD ["python", "seeder/main.py"]
