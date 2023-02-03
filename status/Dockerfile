# Image: tapis/status-config-builder

FROM python:3.11
RUN apt-get update && apt-get install -y vim

RUN pip install Jinja2
RUN pip install pyyaml

RUN mkdir -p /templates
ADD config.yaml.j2 /templates

ADD compile.py /compile.py
CMD ["python", "/compile.py"]

