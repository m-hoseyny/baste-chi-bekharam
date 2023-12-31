# pull official base image
FROM python:3.8-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app/
# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
# ENTRYPOINT ["python", "app.py"]
