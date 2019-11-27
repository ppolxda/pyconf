# -*- coding: utf-8 -*-
"""
@create: 2019-02-13 15:55:48.

@author: ppolxda

@desc:
"""
import re
import six
import json
import copy
import codecs
import argparse
from logging import config as log_config
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

PNAME_DEFINE = '{pname}'
BOOL_LIST = {'boolean', 'bool'}
INT_LIST = {'int', 'int32', 'int64', 'uint16'}
JSON_STRING = {'jsonString', 'json_string', 'jsonstring'}
FLOAT_LIST = {'float', 'double', 'double8_4', 'double16_6', 'double36_14',
              'double16_2', 'double24_8', 'amount_type'}
STRING_LIST = {'string', 'string4', 'string8', 'string12', 'string16',
               'string24', 'string32', 'string64', 'string128',
               'string256', 'string512'}
BYTE_LIST = {'bytes', 'byte24'}
OTHER_LIST = {'datetime', 'date',  'class', 'any'}
ALL_TYPE_LIST = (BOOL_LIST | INT_LIST | JSON_STRING | FLOAT_LIST |
                 STRING_LIST | BYTE_LIST | OTHER_LIST)


def _(val):
    return val


def is_date(val):
    if not isinstance(val, six.string_types):
        return False
    return re.match(r'[0-9]{4}[0-9]{2}[0-9]{2}', val) is not None


def is_datetime(val):
    if not isinstance(val, six.string_types):
        return False
    return re.match(r'[0-9]{4}[0-9]{2}[0-9]{2}T[0-9]{2}[0-9]{2}[0-9]{2}', val) is not None  # noqa


class FeildInVaildError(Exception):
    pass


class DefaultUndefine(object):
    pass


class FeildOption(object):

    class Options(object):

        def __init__(self, update='false', maxlen=None,
                     minlen=None, maxval=None, minval=None,
                     regix=None, allow_none=None, optional=True):
            self.update = update
            self.maxlen = maxlen
            self.minlen = minlen
            self.maxval = maxval
            self.minval = minval
            self.regix = regix
            self.allow_none = allow_none
            self.optional = optional

        def to_dict(self):
            return {
                'update': self.update,
                'maxlen': self.maxlen,
                'minlen': self.minlen,
                'maxval': self.maxval,
                'minval': self.minval,
                'regix': self.regix,
                'allow_none': self.allow_none,
                'optional': self.optional,
            }

        def __str__(self):
            return json.dumps(self.to_dict())

    class OptOptions(object):

        def __init__(self, name, opt_name=None,
                     opt_short_name=None,
                     is_print=True, help_desc=''):
            self.opt_name = opt_name
            self.opt_short_name = opt_short_name
            self.help_desc = help_desc
            self.is_print = is_print

            if '.' in name:
                self.opt_fsection = name[:name.find('.')]
                self.opt_fname = name[name.find('.') + 1:]
            else:
                self.opt_fsection = 'root'
                self.opt_fname = name

            if isinstance(opt_name, six.string_types) and len(opt_name) >= 3:
                if not opt_name.startswith('--'):
                    raise FeildInVaildError(
                        _('invaild opt_name[{}]').format(opt_name)
                    )

                self.opt_aname = opt_name[2:]
            else:
                # self.opt_aname = self.name.replace('.', '_')
                self.opt_aname = self.opt_fname.replace('.', '_')

            self.opt_arguments = ['--{}'.format(self.opt_aname)]

            if self.opt_short_name:
                self.opt_arguments.append(self.opt_short_name)

        def to_dict(self):
            return {
                'opt_name': self.opt_name,
                'opt_short_name': self.opt_short_name,
                'opt_fsection': self.opt_fsection,
                'opt_fname': self.opt_fname,
                'opt_aname': self.opt_aname,
                'opt_arguments': self.opt_arguments,
                'is_print': self.is_print,
                'help_desc': self.help_desc,
            }

        def __str__(self):
            return json.dumps(self.to_dict())

    def __init__(self, name, field_type, desc, default=DefaultUndefine(),
                 update='false', maxlen=None,
                 minlen=None, maxval=None, minval=None,
                 regix=None, optional=True, allow_none=False,
                 opt_name=None, opt_short_name=None,
                 is_print=True, help_desc=''):
        assert field_type in ALL_TYPE_LIST
        assert isinstance(name, six.string_types)
        self.name = name
        self.type = field_type
        self.desc = desc
        self.default = default
        self.help_desc = help_desc
        self.real_type = self.typedefine_to_type()
        self.options = self.Options(update, maxlen,
                                    minlen, maxval, minval,
                                    regix, allow_none, optional)

        self.opts = self.OptOptions(
            name, opt_name, opt_short_name, is_print, help_desc
        )

        # check default
        FeildCheck.field_check(self.name, self.default, self)

    def pname_replace(self, pname):
        _new = copy.deepcopy(self)
        _name = self.name.replace(PNAME_DEFINE, pname)
        _new.opts = self.OptOptions(
            _name, _new.opts.opt_name,
            _new.opts.opt_short_name,
            _new.opts.is_print,
            _new.opts.help_desc
        )
        return _new

    @staticmethod
    def from_dict(**option):
        return FeildOption(**option)

    def to_dict(self):
        return {
            'name': self.name,
            'default': self.default,
            'type': self.type,
            'desc': self.desc,
            'options': self.options.to_dict(),
            'opts': self.opts.to_dict()
        }

    def __str__(self):
        return json.dumps(self.to_dict())

    # def __repr__(self):
    #     return self.__str__()

    def typedefine_to_type(self):
        typedefine = self.type

        if typedefine in JSON_STRING:
            return str

        elif typedefine in STRING_LIST:
            return str

        elif typedefine in BYTE_LIST:
            return six.binary_type

        elif typedefine in INT_LIST:
            return int

        elif typedefine in FLOAT_LIST:
            return float

        elif typedefine in BOOL_LIST:
            return bool

        elif typedefine == 'datetime':
            return str

        elif typedefine == 'date':
            return str

        elif typedefine == 'class':
            return dict

        elif typedefine == 'any':
            return None
        else:
            raise FeildInVaildError(_('unknow field type').format(self.name))


# class FeildValue(object):

#     def __init__(self, value, options):
#         assert isinstance(options, FeildOption)
#         self.value = value
#         self.options = options

#     def is_default_value(self):
#         return self.value == self.options.default


class FeildCheck(object):

    @staticmethod
    def field_req_checks(inputs, options):
        # req_keys = set(key for key, val in options.items()
        #                if isinstance(val, FeildOption) and
        #                not val.optional)

        for key, val in options.items():
            if isinstance(val, FeildOption) and \
                    (not val.options.optional) and \
                    key not in inputs:
                raise FeildInVaildError(
                    _('Not enough arguments[{}]').format(key))

    @classmethod
    def field_checks(cls, inputs, options, check_req=False):
        assert isinstance(inputs, dict)
        assert isinstance(options, dict)
        if check_req:
            cls.field_req_checks(inputs, options)

        for key, val in inputs.items():
            option = options.get(key, None)
            if not isinstance(option, FeildOption):
                raise FeildInVaildError(
                    _('{} has not define in options'.format(key)))

            cls.field_check(key, val, option)

    @classmethod
    def field_check(cls, key, val, option):
        assert isinstance(option, FeildOption)
        args = (option, key, val)

        if val is None and option.options.allow_none:
            pass

        elif option.type in JSON_STRING:
            cls.field_json(*args)

        elif option.type in STRING_LIST:
            cls.field_string(*args)

        elif option.type in BYTE_LIST:
            cls.field_bytes(*args)

        elif option.type in INT_LIST:
            cls.field_int(*args)

        elif option.type in FLOAT_LIST:
            cls.field_float(*args)

        elif option.type in BOOL_LIST:
            cls.field_boolean(*args)

        elif option.type == 'datetime':
            cls.field_datetime(*args)

        elif option.type == 'date':
            cls.field_date(*args)

        elif option.type == 'class':
            cls.field_class(*args)

        elif option.type == 'any':
            pass

        # elif len(option.type) > 4 and (
        #         option.type[:4] == 'Enum' or
        #         option.type[-4:] == 'Enum'):
        #     FeildCheck.field_enum(
        #         option.type,
        #         option,
        #         key, val
        #     )
        else:
            raise FeildInVaildError(_('unknow field type[{}]').format(key))

    @staticmethod
    def field_int(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, six.integer_types):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

        minval = opt.options.minval
        maxval = opt.options.maxval

        if minval is not None and val < int(minval):
            raise FeildInVaildError(
                _('value less then minval[{}][min={}]').format(key, minval))

        if maxval is not None and val > int(maxval):
            raise FeildInVaildError(
                _('value more then maxval[{}][max={}]').format(key, maxval))

    @staticmethod
    def field_float(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, (float, int)):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

        minval = opt.options.minval
        maxval = opt.options.maxval

        if minval is not None and val < int(minval):
            raise FeildInVaildError(
                _('value less then minval[{}][min={}]').format(key, minval))

        if maxval is not None and val > int(maxval):
            raise FeildInVaildError(
                _('value more then maxval[{}][max={}]').format(key, maxval))

    @staticmethod
    def field_json(opt, key, val):
        FeildCheck.field_string(opt, key, val)

        if not isinstance(val, (float, int)):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

    @staticmethod
    def field_json_string(opt, key, val):
        FeildCheck.field_string(opt, key, val)
        try:
            reuslt = json.loads(val)
        except Exception:
            raise FeildInVaildError(
                _('invaild type[{}][json string]').format(key))

        if not isinstance(reuslt, dict):
            raise FeildInVaildError(
                _('invaild type[{}][json string]').format(key))

    @staticmethod
    def field_string(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, six.string_types):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

        minlen = opt.options.minlen
        maxlen = opt.options.maxlen
        regix = opt.options.regix

        if minlen is not None and len(val) < int(minlen):
            raise FeildInVaildError(
                _('value length less then minlen[{}][min={}]').format(
                    key, minlen))

        if maxlen is not None and len(val) > int(maxlen):
            raise FeildInVaildError(
                _('value length more then maxlen[{}][max={}]').format(
                    key, maxlen))

        if regix and re.match(regix, val) is None:
            raise FeildInVaildError(
                _('format invaild[{}][regix:{}]').format(key, regix))

    @staticmethod
    def field_bytes(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, six.binary_type):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

        minlen = opt.options.minlen
        maxlen = opt.options.maxlen

        if minlen is not None and len(val) < int(minlen):
            raise FeildInVaildError(
                _('value length less then minlen[{}][min={}]').format(
                    key, minlen))

        if maxlen is not None and len(val) > int(maxlen):
            raise FeildInVaildError(
                _('value length more then maxlen[{}][max={}]').format(
                    key, maxlen))

    @staticmethod
    def field_boolean(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, bool):
            raise FeildInVaildError(_('invaild type[{}]').format(key))

    @staticmethod
    def field_datetime(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not is_datetime(val):
            raise FeildInVaildError(
                _('format invaild[{}][YYYYmmDDTHHMMSS]').format(key))

    @staticmethod
    def field_date(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not is_date(val):
            raise FeildInVaildError(
                _('format invaild[{}][YYYYmmDD]').format(key))

    @staticmethod
    def field_class(opt, key, val):
        assert isinstance(opt, FeildOption)
        assert isinstance(key, six.string_types)

        if not isinstance(val, dict):
            raise FeildInVaildError(_('invaild type[{}]').format(key))


class Options(object):
    """Options."""

    def __init__(self):
        """__init__."""
        self.opts_akey = set()
        self.opts_define = self.load_default_opts()
        self.opts_default_key = list(self.opts_define.keys())
        self.opts_args = {}
        self.opts_config = {}
        self.is_parse = False

        self.pnane = ''
        self.popts_define = None
        self.popts_default_key = None

    def reset_all(self):
        self.opts_akey = set()
        self.opts_define = self.load_default_opts()
        self.opts_default_key = list(self.opts_define.keys())
        self.opts_args = {}
        self.opts_config = {}
        self.is_parse = False

        self.pnane = ''
        self.popts_define = None
        self.popts_default_key = None

    def load_default_opts(self):
        return {
            'root.config': FeildOption(
                'root.config', 'string', 'config_path',
                default=None,
                regix=r'^(?:(file|etcd)://(.*?))?$',
                opt_name='--config', opt_short_name='-c',
                help_desc='config path (file://./config/main.ini|etcd://localhost)',  # noqa
                allow_none=True),
            'root.logging': FeildOption(
                'root.logging', 'string', 'logging_path',
                default=None,
                opt_name='--logging', opt_short_name='-l',
                help_desc='logging config path',
                allow_none=True),
            'root.disable_existing_loggers': FeildOption(
                'root.disable_existing_loggers', 'bool', 'disable_existing_loggers',  # noqa
                default=True,
                opt_name='--disable_existing_loggers', opt_short_name='-ld',
                help_desc='logging config disable_existing_loggers'),
            'root.encoding': FeildOption(
                'root.encoding', 'string', 'encoding',
                default='utf8',
                opt_name='--encoding', opt_short_name='-e',
                help_desc='config encoding'),
        }

    def add_define(self, fopt):
        if not isinstance(fopt, FeildOption):
            raise FeildInVaildError('fopt invaild')

        if fopt.name in self.opts_define and \
                fopt.name not in self.opts_default_key:
            raise FeildInVaildError(_('{} is defined').format(fopt.name))

        if fopt.opts.opt_aname in self.opts_akey:
            raise FeildInVaildError(
                _('opt_aname is exist[{}]'.format(fopt.name)))

        self.opts_akey.add(fopt.opts.opt_aname)
        self.opts_define[fopt.name] = fopt

    def define(self, name, field_type, desc, default=DefaultUndefine(),
               update='false', maxlen=None,
               minlen=None, maxval=None, minval=None,
               regix=None, optional=True, allow_none=False,
               opt_name=None, opt_short_name=None,
               is_print=True, help_desc=''):

        fo = FeildOption(
            name, field_type, desc, default=default,
            update=update, maxlen=maxlen,
            minlen=minlen, maxval=maxval, minval=minval,
            regix=regix, optional=optional, allow_none=allow_none,
            opt_name=opt_name, opt_short_name=opt_short_name,
            is_print=is_print, help_desc=help_desc)

        self.add_define(fo)

    def get_opt(self, name, defval=DefaultUndefine()):
        if name not in self.opts_default_key and not self.is_parse:
            raise FeildInVaildError('not run parse_opts')

        opt = self.opts_define.get(name, None)
        if opt is None:
            raise FeildInVaildError('option not found')

        value = self.opts_args.get(name, defval)
        if value is not None and not isinstance(value, DefaultUndefine):
            return value

        value = self.opts_config.get(name, defval)
        if value is not None and not isinstance(value, DefaultUndefine):
            return value

        if value is not None and not isinstance(defval, DefaultUndefine):
            FeildCheck.field_check(name, defval, opt)
            return defval

        return opt.default

    def parse_opts(self, pnane, desc=''):
        if self.is_parse:
            return

        group_parser = {}
        popts_define = {
            key: val.pname_replace(pnane)
            for key, val in self.opts_define.items()
        }
        popts_default_key = list(popts_define.keys())
        parser = argparse.ArgumentParser(description=desc)

        # add argparse
        for i in popts_define.values():
            assert isinstance(i, FeildOption)
            opt_fsection = i.opts.opt_fsection
            if opt_fsection != 'root':
                if opt_fsection not in group_parser:
                    group_parser[opt_fsection] = parser.add_argument_group(
                        _('{} Options').format(opt_fsection))

                _parser = group_parser[opt_fsection]
            else:
                _parser = parser

            _parser.add_argument(*i.opts.opt_arguments,
                                 default=DefaultUndefine(),
                                 type=i.real_type, help=i.help_desc)

        try:
            args = parser.parse_args()
        except Exception as ex:
            raise FeildInVaildError(ex)

        # get argument result
        for i in popts_define.values():
            assert isinstance(i, FeildOption)
            value = getattr(args, i.opts.opt_aname)
            if not isinstance(value, DefaultUndefine):
                self.opts_args[i.name] = value

        FeildCheck.field_checks(self.opts_args, popts_define, False)

        # load default otps
        config_path = self.get_opt('root.config', None)
        logging_path = self.get_opt('root.logging', None)
        encoding = self.get_opt('root.encoding', None)
        disable_existing_loggers = self.get_opt('root.disable_existing_loggers', None)  # noqa

        if logging_path and isinstance(logging_path, six.string_types):
            self.parse_opts_logging(logging_path, encoding,
                                    disable_existing_loggers)

        # load config in file or etcd
        if config_path and isinstance(config_path, six.string_types):
            is_match = False
            fpath = re.match(r'^file://(.*?)$', config_path)
            if fpath:
                self.parse_opts_file(fpath.group(1), encoding, popts_define)
                is_match = True

            fpath = re.match(r'^etcd://(.*?)$', config_path)
            if fpath:
                self.parse_opts_etcd(config_path, encoding, popts_define)
                is_match = True

            if not is_match:
                raise TypeError(
                    _('root.config fmt error[{}]').format(config_path)
                )

        self.pnane = pnane
        self.popts_define = popts_define
        self.popts_default_key = list(popts_define.keys())
        self.is_parse = True

    def parse_opts_logging(self, path, encoding, disable_existing_loggers):
        with codecs.open(path, encoding=encoding) as fs:
            log_fs = configparser.ConfigParser()
            log_fs.read_file(fs)

            log_config.fileConfig(
                log_fs,
                disable_existing_loggers=disable_existing_loggers
            )

    def parse_opts_file(self, path, encoding, popts_define=None):
        with codecs.open(path, encoding=encoding) as fs:
            fs_config = configparser.ConfigParser()
            fs_config.read_file(fs)

        if popts_define:
            _popts_define = popts_define
        elif self.popts_define:
            _popts_define = self.popts_define
        else:
            _popts_define = self.opts_define

        for i in _popts_define.values():
            assert isinstance(i, FeildOption)
            if i.real_type == int:
                value = self.__get_value_int_def(
                    fs_config, i.opts.opt_fsection,
                    i.opts.opt_fname, DefaultUndefine())
            elif i.real_type == bool:
                value = self.__get_value_boolen_def(
                    fs_config, i.opts.opt_fsection,
                    i.opts.opt_fname, DefaultUndefine())
            elif i.real_type == str:
                value = self.__get_value_string_def(
                    fs_config, i.opts.opt_fsection,
                    i.opts.opt_fname, DefaultUndefine())
            elif i.real_type == float:
                value = self.__get_value_float_def(
                    fs_config, i.opts.opt_fsection,
                    i.opts.opt_fname, DefaultUndefine())
            else:
                raise FeildInVaildError('parse_opts_file error')

            if not isinstance(value, DefaultUndefine):
                self.opts_config[i.name] = value

        FeildCheck.field_checks(self.opts_config, self.opts_define, False)

    def parse_opts_etcd(self, path, encoding, popts_define=None):
        raise NotImplementedError

    def print_config(self, key_weight=32):
        assert isinstance(key_weight, int)
        fmt = '-- {:<' + str(key_weight) + '} -- {}'
        reuslt = ['----------- pyopts start ---------------------------']
        for key in self.opts_define.keys():
            reuslt.append(fmt.format(key, self.get_opt(key)))

        reuslt.append('----------- pyopts end - --------------------------')
        return '\n'.join(reuslt)

    # ----------------------------------------------
    #        get file
    # ----------------------------------------------

    @staticmethod
    def __get_value_boolen_def(fs_config, section, option, defval):
        try:
            return fs_config.getboolean(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_int_def(fs_config, section, option, defval):
        try:
            return fs_config.getint(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_float_def(fs_config, section, option, defval):
        try:
            return fs_config.getfloat(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_string_def(fs_config, section, option, defval):
        try:
            return fs_config.get(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval


opts = Options()

__all__ = [
    'FeildInVaildError',
    'FeildOption',
    'opts'
]
