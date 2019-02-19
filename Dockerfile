FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -e .
ENTRYPOINT ["python"]
CMD ["./test/db.py"]
