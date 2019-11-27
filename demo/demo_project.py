# -*- coding: utf-8 -*-
import re
from pyopts import opts
from pyopts import FeildOption


class MainSettings(object):

    # ----------------------------------------------
    #        root
    # ----------------------------------------------

    ROOT_LOGGING = 'root.logging'
    ROOT_LOGGING_OPT = FeildOption(
        ROOT_LOGGING, 'string',
        default='./config/logging/logging_00.ini',
        desc='logging path',
        help_desc='logging path',
        opt_short_name='-l',
        allow_none=True
    )

    ROOT_CONFIG = 'root.config'
    ROOT_CONFIG_OPT = FeildOption(
        ROOT_CONFIG, 'string',
        default='file://./config/main.ini',
        desc='main config path',
        help_desc=('main config path'
                   '(file://./config/main.ini|etcd://localhost)'),
        opt_short_name='-c',
        allow_none=True
    )

    ROOT_DISABLE_EXISTING_LOGGERS = 'root.disable_existing_loggers'
    ROOT_DISABLE_EXISTING_LOGGERS_OPT = FeildOption(
        ROOT_DISABLE_EXISTING_LOGGERS, 'bool',
        default=False,
        desc='disable existing loggers',
        help_desc='disable existing loggers',
        opt_short_name='-ld'
    )

    @staticmethod
    def print_config():
        return opts.print_config(40)

    @classmethod
    def init_opt(cls, name):
        if opts.is_parse:
            return

        keys = filter(lambda x: re.match(r'^(.+)_OPT$', x), dir(cls))
        for i in keys:
            opts.add_define(getattr(cls, i))
        opts.parse_opts(name)


class Settings(MainSettings):

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
    assert settings.zmp_in_url == 'tcp://*:6700'
    assert settings.zmp_out_url == 'tcp://*:6701'


if __name__ == '__main__':
    main()
