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
