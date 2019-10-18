FROM python:3-alpine
ENV FLASK_APP /usr/src/app/app.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 0
EXPOSE 5000
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "flask", "run", "--host=0.0.0.0", "--cert=/certs/cert.pem", "--key=/certs/key.pem" ]
