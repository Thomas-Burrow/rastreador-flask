#Stage 1: Install OS and deps
FROM debian:stable
ENV DEBIAN_FRONTEND=noninteractive
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3.13-venv git libmariadb-dev
#TODO: figure out how to secure ourselves from pip supply chain attacks

WORKDIR /app
#Corre com o repositório atual
COPY . .
RUN python3 -m venv venv
#activate
VOLUME /app/instance
ENV PATH="/app/venv/bin:$PATH"
RUN pip install -r requirements.txt
EXPOSE 8080

CMD ["python", "-m", "gunicorn", "--config", "gunicorn_config.py", "rastreador:create_app()"]