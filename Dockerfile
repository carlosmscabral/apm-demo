FROM python:3.8.0

RUN pip3 install --upgrade pip

RUN apt-get update \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

WORKDIR /app
RUN easy_install https://github.com/GoogleCloudPlatform/cloud-debug-python/releases/download/v2.15/google_python_cloud_debugger-py3.8-linux-x86_64.egg
RUN pip3 install -r requirements.txt

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

ENTRYPOINT ["python3", "app.py"]