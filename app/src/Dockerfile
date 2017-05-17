FROM python:3.6-slim
ENV /home/app/chatbot $PATH
ADD . /home/app/chatbot
WORKDIR /home/app/chatbot
EXPOSE 8080
RUN apt-get update && apt-get install -y nano
RUN pip3 install -r requirements.txt
CMD python3 bot.py