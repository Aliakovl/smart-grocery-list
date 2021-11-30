FROM python:3.9
# set work directory
WORKDIR /tgbot
# copy project
COPY . /tgbot
# install dependencies
RUN pip install -r requirements.txt
# run app
CMD ["python3", "tgbot.py"]