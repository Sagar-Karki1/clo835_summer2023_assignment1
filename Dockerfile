FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app
RUN mkdir -p static
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 81
ENTRYPOINT ["python3"]
CMD ["app.py"]