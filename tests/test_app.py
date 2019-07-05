import pytest
from os import path, unlink
from src import app

@pytest.mark.asyncio
async def test_run_cmd():
    # postive case
    assert await app.run_cmd('date')

    # negative case
    with pytest.raises(app.ZipAlignError) as excinfo:
        await app.run_cmd('asl45laskdjg', extype=app.ZipAlignError)
    assert '[stderr]' in str(excinfo.value)

@pytest.mark.asyncio
async def test_sign_apk(app_release_apk_path, app_release_signed_apk_path, app_debug_apk_path, ks_path, ks_pass, key_alias):
    # postive case
    apk_out_path = await app.sign_apk(app_release_apk_path, ks_path, ks_pass, key_alias)
    assert apk_out_path != app_release_signed_apk_path
    assert path.isfile(apk_out_path)
    try:
        with open(apk_out_path, 'rb') as a, open(app_release_signed_apk_path, 'rb') as b:
            # should be identical to the manual signed package
            assert a.read() == b.read()
    finally:
        unlink(apk_out_path)

    # negative case: zipalign wouldn't work correctly against debug-apk
    with pytest.raises(app.ZipAlignError):
        await app.sign_apk(app_debug_apk_path, ks_path, ks_pass, key_alias)
