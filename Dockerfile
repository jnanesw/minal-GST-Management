FROM python
COPY . /app
WORKDIR /app
RUN pip install requirements.txt
EXPOSE $PORT
CMD uvicorn --workers=4 --bind 0.0.0.0:$PORT app:app
