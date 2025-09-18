FROM python:3.10-slim

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pip install pipenv
RUN pipenv install
RUN pip install gunicorn

COPY . .

EXPOSE 10000
ENTRYPOINT ["gunicorn -b 0.0.0.0:10000 --access-logfile - --error-logfile - server:app"]