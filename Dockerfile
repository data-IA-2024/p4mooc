FROM python:3.9.5-slim
WORKDIR /code
COPY ./requirements.txt /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY . /code
CMD ["fastapi", "run", "app.py", "--port", "80"]