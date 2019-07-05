# Introduction

A simple android apk signing web service.

# Configuration

All settings are done by setting up __Envrionement Variables__

`HOST` : web server listening host
`PORT` : web server listening port
`SIGN_KEY` : for server to verify if requests are legit. client must use this key on `blake2d` algorithm to generate signature of the apk being signed.
`KS_PATH` : path to keystore file
`KS_PASS` : password of the keystore file
`KEY_ALIAS` : alias of key
`KEY_PASS` : password of the key if any

# Install requirements and run
```
pip install -r requirements.txt
python3.7 src/app.py
```

# Build and run as docker
1. Use `Dockerfile` to build the docker image. You can checkout the base image repository (here)[https://github.com/klesh/gitlab-android-ci]
2. Use `docker-compose.yml` to run the docker image
