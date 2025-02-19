FROM python:3.8-slim

WORKDIR /app 

RUN apt-get update && \
    apt-get install -y curl cmake g++ git build-essential libsodium-dev libcurl4-openssl-dev gdb && \
    apt-get autoremove -y && apt-get clean

RUN pip install --upgrade build setuptools wheel

RUN git clone https://github.com/lokingdav/libcpex.git
RUN cd libcpex && python -m build
RUN cd libcpex && pip install dist/*.whl
RUN rm -rf libcpex

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -e .
