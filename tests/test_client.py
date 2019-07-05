import pytest
import asyncio
import sys
import os
from hashlib import blake2b
import aiohttp
import subprocess
import time

@pytest.fixture()
def server_proc(app_path, server_host, server_port, sign_key, ks_path, ks_pass, key_alias, key_pass):
    env = {}
    env.update(os.environ)
    env['HOST'] = server_host
    env['PORT'] = str(server_port)
    env['SIGN_KEY'] = sign_key
    env['KS_PATH'] = ks_path
    env['KS_PASS'] = ks_pass
    env['KEY_ALIAS'] = key_alias
    env['KEY_PASS'] = key_pass or ''
    p = subprocess.Popen(['python', app_path], env=env)
    time.sleep(1) # wait till server is fully ready
    yield p
    p.kill()


@pytest.mark.asyncio
async def test_whole(server_proc,
                     server_host,
                     server_port,
                     sign_key,
                     app_release_apk_path,
                     app_release_signed_apk_path,
                     app_debug_apk_path):

    def encode(text):
        return text.encode('utf-8')

    async def post(apk_path, check):
        sign = None
        hasher = blake2b(key=sign_key.encode('ascii'), digest_size=16)
        with open(apk_path, 'rb') as f1:
            hasher.update(f1.read())
        sign = hasher.hexdigest()
        async with aiohttp.ClientSession() as session:
            data = {
                'apk': open(apk_path, 'rb'),
                'sign': sign
            }
            url = 'http://{}:{}'.format(server_host, server_port)
            async with session.post(url, data=data) as res:
                await check(res)

    # postive case
    async def check_positive(res):
        assert res.headers.get('content-type') == 'application/octet-stream'
        with open(app_release_signed_apk_path, 'rb') as expected_apk:
            assert expected_apk.read()  == await res.read()

    await post(app_release_apk_path, check_positive)

    # negative case
    async def check_negative(res):
        assert 'json' in res.headers.get('content-type')
        text = await res.text()
        print(text)
        assert 'ZipAlignError' in text
        assert 'stderr' in text
    await post(app_debug_apk_path, check_negative)
