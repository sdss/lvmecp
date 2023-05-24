FROM python:3.11-slim-bullseye

MAINTAINER Jose Sanchez-Gallego, gallegoj@uw.edu
LABEL org.opencontainers.image.source https://github.com/sdss/lvmecp

WORKDIR /opt

COPY . lvmecp

RUN pip3 install -U pip setuptools wheel
RUN cd lvmecp && pip3 install .
RUN rm -Rf lvmecp

ENTRYPOINT lvmecp actor start --debug
