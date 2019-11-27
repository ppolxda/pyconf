# pyopts

## install

pip install

```bash
pip install git+https://github.com/ppolxda/pyopts
```

## value priority

argv > config > get_opt default > default

## demo

test.ini

```ini
[a]
c=1111
[d]
f=22222222
[appname]
cc=456456
```

python

```python
from pyopts import opts


def main():
    opts.define('{pname}.cc', 'string', 'a', '1111', help_desc='a desc')
    opts.define('a.a', 'string', 'a', '1111', help_desc='a desc')
    opts.define('a.b', 'int', 'b', 2222, help_desc='b desc')
    opts.define('a.c', 'int', 'c', 2222, help_desc='c desc')
    opts.define('d.f', 'int', 'f', 3333, help_desc='f desc')
    opts.parse_opts('appname')
    assert opts.get_opt('{pname}.cc') == '456456'
    assert opts.get_opt('a.a') == '1111'
    assert opts.get_opt('a.b') == 2222
    assert opts.get_opt('a.c') == 9
    assert opts.get_opt('d.f') == 22222222


if __name__ == '__main__':
    main()
```

run shell

```shell
python demo.py --config=file://./demo.ini --c=9
```

## demo for project

```python
# -*- coding: utf-8 -*-
import re
from pyopts import opts
from pyopts import FeildOption
from pyopts import RootSettings


class Settings(RootSettings):

    PUSHER_ZMP_IN_URL = 'main_config.zmp_in_url'
    PUSHER_ZMP_IN_URL_OPT = FeildOption(
        PUSHER_ZMP_IN_URL, 'string',
        default='tcp://*:6700',
        desc='quoted zmp_in_url',
        help_desc='quoted zmp_in_url'
    )

    PUSHER_ZMP_OUT_URL = 'main_config.zmp_out_url'
    PUSHER_ZMP_OUT_URL_OPT = FeildOption(
        PUSHER_ZMP_OUT_URL, 'string',
        default='tcp://*:6701',
        desc='quoted zmp_out_url',
        help_desc='quoted zmp_out_url'
    )

    def __init__(self, name):
        self.init_opt(name)
        self.zmp_in_url = opts.get_opt(self.PUSHER_ZMP_IN_URL)
        self.zmp_out_url = opts.get_opt(self.PUSHER_ZMP_OUT_URL)


def main():
    settings = Settings('myproject')
    print(settings.print_config())
    assert settings.zmp_in_url == 'tcp://*:6700'
    assert settings.zmp_out_url == 'tcp://*:6701'


if __name__ == '__main__':
    main()

```

print log config

```log
----------- pyopts start ---------------------------
-- root.config                              -- None
-- root.logging                             -- None
-- root.disable_existing_loggers            -- False
-- root.encoding                            -- utf8
-- main_config.zmp_in_url                   -- tcp://*:6700
-- main_config.zmp_out_url                  -- tcp://*:6701
----------- pyopts end - --------------------------
```
