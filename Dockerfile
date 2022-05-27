FROM python:3.9
WORKDIR /app
ADD . /app
COPY . .
ENTRYPOINT ["python"]
CMD ["app.Main:app", "--host", "0.0.0.0", "--port", "80" ]