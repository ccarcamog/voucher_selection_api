### 1. Installing an OS to my container
FROM alpine:3.15

### 2. Installing Java 11 over Alpine
RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk11-jre

### 3. Installing Python3 and PIP
RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

### 4. Adding project files to image
ADD . /voucher_selection_api
WORKDIR /voucher_selection_api

### 5. Installing python libraries
RUN pip install -r requirements.txt