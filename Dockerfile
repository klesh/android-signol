FROM android-ci:v2

RUN mkdir /app
COPY src/app.py /app/
COPY requirements.txt /app/
RUN apt -qy install build-essential checkinstall
RUN apt -qy install libreadline-gplv2-dev libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
RUN tar xzf Python-3.7.3.tgz
RUN cd /Python-3.7.3 && ./configure --enable-optimizations && make altinstall
RUN rm -rf /Python-3.7.3 /Python-3.7.3.tgz
RUN python3.7 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/requirements.txt
RUN apt -qy autoremove
