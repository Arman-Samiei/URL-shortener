FROM python:3.7-slim AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv


ENV PATH="/opt/venv/bin:$PATH"


RUN pip install pymongo==3.11.2
RUN pip install Flask==2.0.2
RUN pip install requests==2.27.1
RUN pip install markupsafe==1.1.1

FROM python:3.7-alpine

COPY --from=compile-image /opt/venv /opt/venv

COPY app.py .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "app.py"]

