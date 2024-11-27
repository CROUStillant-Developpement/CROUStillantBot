FROM python:3.12.7-alpine3.20

RUN apk add --no-cache git

COPY . ./CROUStillantBot

WORKDIR /CROUStillantBot

RUN git submodule update --init --recursive

RUN git submodule foreach git pull origin main

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "__main__.py"]
