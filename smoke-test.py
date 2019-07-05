import asyncio
import sys
import os
from hashlib import blake2b
import aiohttp

ARTIFACTS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tests', 'artifacts')

SIGN_KEY = 'SMOKE_TEST'
SERVER_HOST = 'localhost'
SERVER_PORT = 4040


def encode(text):
    return text.encode('utf-8')

async def post(apk_path, apk_signed_path):
    sign = None
    hasher = blake2b(key=SIGN_KEY.encode('ascii'), digest_size=16)
    with open(apk_path, 'rb') as f1:
        hasher.update(f1.read())
    sign = hasher.hexdigest()
    async with aiohttp.ClientSession() as session:
        data = {
            'apk': open(apk_path, 'rb'),
            'sign': sign
        }
        url = 'http://{}:{}'.format(SERVER_HOST, SERVER_PORT)
        async with session.post(url, data=data) as res:
            if res.headers.get('content-type') == 'application/octet-stream':
                with open(apk_signed_path, 'wb') as apk_signed_file:
                    apk_signed_file.write(await res.read())
                print('signed apk saved to %s' % apk_signed_path)
                return 'file'
            else:
                print(await res.text())
                return 'json'

async def main():
    await post(os.path.join(ARTIFACTS_PATH, 'app-debug.apk'), '/tmp/app-debug-signed.apk')
    await post(os.path.join(ARTIFACTS_PATH, 'app-release.apk'), '/tmp/app-release-signed.apk')

asyncio.run(main())
