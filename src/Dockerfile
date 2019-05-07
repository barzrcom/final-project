FROM python:3.7.3

ENV LANG=en_US.UTF-8 \
	LC_ALL=en_US.UTF-8 \
	FLASK_APP=ml/__main__.py

COPY ml .

RUN pip install -r requirements.txt
WORKDIR ./ml

CMD ["python","__main__.py"]
