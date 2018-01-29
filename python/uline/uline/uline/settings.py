# -*- coding:utf-8 -*-
import os
import re
from os.path import expanduser

bash_rc = ''
if os.path.exists(expanduser("~/.bashrc")):
    with open(expanduser("~/.bashrc")) as f:
        bash_rc += f.read()

if os.path.exists(expanduser("~/.bash_profile")):
    with open(expanduser("~/.bash_profile")) as f:
        bash_rc += f.read()

match = re.search(r'ULINE_CMS_ENV=(.+)', bash_rc)
env = match.group(1) if match else 'default'

WX_0_CAT_LIST = [
    '161215010100663', '161215010100664', '161215010100665', '161215010100666',
    '161215010100667', '161215010100668', '161215010100669', '161215010100670',
    '161215010100671', '161215010100672', '161215010100673', '161215010100674',
    '161215010100675', '161215010100676',
]

if env == 'DEV':
    from uline.config.dev.conf import *
elif env == 'LOCAL':
    from uline.config.local.conf import *
elif env == 'CMBC_PROD':
    # 招商银行
    from uline.config.cmbc.conf import *
elif env == 'SPD_PROD':
    # 浦发银行
    from uline.config.spd.conf import *
elif env == 'SPDLOCAL':
    # 浦发银行
    from uline.config.spdlocal.conf import *
elif env == 'DEV3':
    from uline.config.dev3.conf import *
else:
    raise Exception('必须在~/.bashrc或~/.bash_profile中设置ULINE_CMS_ENV环境变量')
