FROM python:3

WORKDIR /app

COPY ./ /app

RUN pip install -r /app/requirements.txt

EXPOSE 8080

CMD [ "python", "runserver.py" ]
