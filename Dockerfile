FROM python:3

COPY . .

RUN pip install -r requirements.txt

CMD ["python3","-m","app.main"]