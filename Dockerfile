# Default image
# FROM ubuntu:16.04
FROM python:3.6-stretch
# Update and install basic dependencies
RUN apt-get update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:mc3man/trusty-media
RUN apt-get install libstdc++6 -y
RUN apt-get install liblapack3 -y
RUN apt-get install libblas3 -y
RUN apt-get install python3-pip -y
RUN apt-get install python3 -y
RUN apt-get install libgfortran3
RUN pip3 install gunicorn

# Add our code
COPY ./app /app
WORKDIR ./app

# Copy requirements for ease of installing python modules
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Allow files to be executeable
# (Data migration, signpass
RUN chmod +x manage.py
RUN chmod +x signpass

# Default encoding
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Other Variables
ENV APP_SETTINGS=config.DevelopmentConfig
ENV SECRET_KEY=CnySh+ACsQElyzHh
ENV DATABASE_URL=postgresql://phipps:qaplaqapla@phippspassesdb.c25wttq29yrb.us-east-1.rds.amazonaws.com:5432/phipps_passes
ENV FLASK_APP=app.py

# Open up port 80 for https
EXPOSE 80

# Run the app
CMD ["/bin/bash", "/app/docker-entrypoint.sh"]
# CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
