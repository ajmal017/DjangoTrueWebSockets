import os
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV

if os.getenv('DBG') and os.getenv(DJANGO_AUTORELOAD_ENV):
    import pydevd_pycharm
    print('CONNECTING TO REMOTE DEBUG SERVER')
    pydevd_pycharm.settrace(
        host='172.17.0.1',
        port=12345,
        stdoutToServer=True,
        stderrToServer=True,
        suspend=False,
        # patch_multiprocessing=True
    )
    print('CONNECTED')

