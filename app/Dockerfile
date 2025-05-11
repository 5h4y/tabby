FROM python:3.11-slim

# working directory
WORKDIR /app

# get requirements.txt
COPY ../requirements.txt /app/requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the project
COPY . /app

# expose correct port
EXPOSE 5151

# command to run flask app
CMD ["python", "app/app.py"]
