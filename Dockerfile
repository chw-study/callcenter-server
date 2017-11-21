FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt

COPY . /usr/src/app

CMD [ "python", "__main__.py" ]
