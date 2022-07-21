FROM python
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE $PORT
CMD uvicorn --workers=4 --bind 0.0.0.0:$PORT app:app
