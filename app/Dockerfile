FROM python:3.11-slim

# working directory
WORKDIR /app

# copy project files
COPY . /app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# expose correct port
EXPOSE 5151

# command to run flask app
CMD ["python", "app/app.py"]
