FROM python:3.8

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install dumb-init -y

# Run the application:
COPY script /opt/app
COPY models /opt/app/models

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python", "-u", "/opt/app/app.py"]

#CMD ["/bin/sh", "-ec", "while :; do echo '.'; sleep 5 ; done"]

