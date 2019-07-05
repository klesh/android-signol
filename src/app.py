import asyncio
import tempfile
import os
from hashlib import blake2b
from aiohttp import web

HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '4040'))
SIGN_KEY = os.environ.get('SIGN_KEY', 'pseudorandom key').encode('ascii')
KS_PATH = os.environ.get('KS_PATH', 'keystore/testkey.jks')
KS_PASS = os.environ.get('KS_PASS', 'helloworld')
KEY_ALIAS = os.environ.get('KEY_ALIAS', 'hello')
KEY_PASS = os.environ.get('KEY_PASS')

class ClientError(Exception):
    pass

class ZipAlignError(ClientError):
    pass

class SignError(ClientError):
    pass

async def run_cmd(cmd, env=None, extype=None):
    extype = extype or Exception
    proc = await asyncio.create_subprocess_shell(
        cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    [stdout, stderr] = await proc.communicate()
    if proc.returncode:
        raise extype('{}\n[code]{}\n[stdout]\n{}\n\n[stderr]\n{}'.format(
            cmd,
            proc.returncode,
            stdout.decode(),
            stderr.decode()))
    return stdout

async def sign_apk(apk_in_path, ks_path, ks_pass, key_alias=None, key_pass=None):
    _, apk_aligned_path = tempfile.mkstemp()
    _, apk_out_path = tempfile.mkstemp()
    try:
        align_cmd = "zipalign -f -v -p 4 '{}' '{}'".format(apk_in_path, apk_aligned_path)

        await run_cmd(align_cmd, extype=ZipAlignError)
        sign_cmd = "apksigner sign --ks '{}' --ks-pass env:KS_PASS --in '{}' --out '{}'".format(
            ks_path,
            apk_aligned_path,
            apk_out_path)
        env = {}
        env.update(os.environ)
        env['KS_PASS'] = ks_pass
        if key_alias:
            sign_cmd += ' --ks-key-alias {}'.format(key_alias)
        if key_pass:
            sign_cmd += " --key-pass env:KEY_PASS"
            env['KEY_PASS'] = key_pass
        await run_cmd(sign_cmd, env=env, extype=SignError)
        return apk_out_path
    except:
        os.unlink(apk_out_path)
        raise
    finally:
        os.unlink(apk_aligned_path)


class SendFileThenDeleteResponse(web.FileResponse):
    async def write_eof(self):
        os.unlink(self._path)
        return await super().write_eof()

async def handle(request):
    reader = await request.multipart()
    apk_field = await reader.next()
    if not apk_field or not apk_field.filename:
        return web.json_response({'error': 'no file uploaded'}, status=400)
    if not apk_field.filename.lower().endswith('.apk'):
        return web.json_response({'error': 'not a apk file'}, status=400)
    apk_in_path = tempfile.mkstemp()[1]
    apk_in_file = open(apk_in_path, 'wb')
    hasher = blake2b(key=SIGN_KEY, digest_size=16)
    try:
        # stream uploaded apk into a temporary file
        while True:
            chunk = await apk_field.read_chunk(8192) # default 8kb/chunk
            if not chunk:
                break
            hasher.update(chunk)
            apk_in_file.write(chunk)

        apk_in_file.flush()
        # verifty signature
        hash_field = await reader.next()
        if not hash_field or hash_field.name != 'sign':
            return web.json_response({'error': 'missing signature'})

        expected_hash = hasher.hexdigest()
        actual_hash = (await hash_field.read()).decode('ascii')
        if actual_hash != expected_hash:
            return web.json_response({'error': 'invalid signature'})

        # perform package signing

        print('start sign apk')
        apk_out_path = await sign_apk(apk_in_path, KS_PATH, KS_PASS, KEY_ALIAS, KEY_PASS)
        return SendFileThenDeleteResponse(apk_out_path, headers={
            'Content-Dispositon': 'attachment; filename="%s"' % os.path.basename(apk_field.filename)
        })
    except Exception as ex:
        status = 400 if isinstance(ex, ClientError) else 500
        return web.json_response({'error': ex.__class__.__name__, 'message': str(ex)}, status=status)
    finally:
        apk_in_file.close()
        os.unlink(apk_in_path)


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post('/', handle)])

    web.run_app(app, host=HOST, port=PORT)
    print('Server is up: http://{}:{}'.format(HOST, PORT))
