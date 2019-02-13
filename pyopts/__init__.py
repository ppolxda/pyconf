# -*- coding: utf-8 -*-
"""
@create: 2019-02-13 15:55:48.

@author: ppolxda

@desc:
"""
import re
import six
import json
import codecs
import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


INT_LIST = {'int', 'int32', 'int64', 'uint16'}
JSON_STRING = {'jsonString', 'json_string', 'jsonstring'}
FLOAT_LIST = {'float', 'double', 'double8_4', 'double16_6', 'double36_14',
              'double16_2', 'double24_8', 'amount_type'}
STRING_LIST = {'string', 'string4', 'string8', 'string12', 'string16',
               'string24', 'string32', 'string64', 'string128',
               'string256', 'string512'}
BYTE_LIST = {'bytes', 'byte24'}
OTHER_LIST = {'datetime', 'date', 'boolean', 'class', 'any'}
ALL_TYPE_LIST = (INT_LIST | JSON_STRING | FLOAT_LIST |
                 STRING_LIST | BYTE_LIST | OTHER_LIST)


def _(val):
    return val


def is_date(val):
    u"""是否是日期."""
    if not isinstance(val, six.string_types):
        return False
    return re.match(r'[0-9]{4}[0-9]{2}[0-9]{2}', val) is not None


def is_datetime(val):
    u"""是否是整型数."""
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
                     minlen=None, maxval=None, minval=None, regix=None):
            self.update = update
            self.maxlen = maxlen
            self.minlen = minlen
            self.maxval = maxval
            self.minval = minval
            self.regix = regix

        def to_dict(self):
            return {
                'update': self.update,
                'maxlen': self.maxlen,
                'minlen': self.minlen,
                'maxval': self.maxval,
                'minval': self.minval,
                'regix': self.regix,
            }

        def __str__(self):
            return json.dumps(self.to_dict())

        def __repr__(self):
            return self.__str__()

    def __init__(self, name, field_type, desc, default=DefaultUndefine(),
                 help_desc='',  update='false', maxlen=None,
                 minlen=None, maxval=None, minval=None,
                 regix=None, optional=True,
                 opt_short_name=None):
        assert field_type in ALL_TYPE_LIST
        assert isinstance(name, six.string_types) and name.count('.') == 1
        self.name = name
        self.type = field_type
        self.desc = desc
        self.default = default
        self.help_desc = help_desc
        self.optional = optional
        self.options = self.Options(update, maxlen,
                                    minlen, maxval, minval,
                                    regix)

        self.real_type = self.typedefine_to_type()
        self.opt_fsection = self.name.split('.')[0]
        self.opt_fname = self.name.split('.')[1]
        self.opt_aname = self.name.replace('.', '_')
        self.opt_short_name = opt_short_name
        if self.opt_short_name:
            self.opt_arguments = (
                self.opt_short_name, '--{}'.format(self.opt_aname))
        else:
            self.opt_arguments = ('--{}'.format(self.opt_aname),)

    @staticmethod
    def from_dict(**option):
        return FeildOption(**option)

    def to_dict(self):
        return {
            'name': self.name,
            'default': self.default,
            'type': self.type,
            'desc': self.desc,
            'optional': self.optional,
            'options': self.options.to_dict()
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

        elif typedefine == 'datetime':
            return str

        elif typedefine == 'date':
            return str

        elif typedefine == 'boolean':
            return bool

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
                    (not val.optional) and \
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

        if option.type in JSON_STRING:
            cls.field_json(*args)

        elif option.type in STRING_LIST:
            cls.field_string(*args)

        elif option.type in BYTE_LIST:
            cls.field_bytes(*args)

        elif option.type in INT_LIST:
            cls.field_int(*args)

        elif option.type in FLOAT_LIST:
            cls.field_float(*args)

        elif option.type == 'datetime':
            cls.field_datetime(*args)

        elif option.type == 'date':
            cls.field_date(*args)

        elif option.type == 'boolean':
            cls.field_boolean(*args)

        elif option.type == 'class':
            cls.field_class(*args)

        elif option.type == 'any':
            pass

        # # 如果是枚举类型
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

    # @staticmethod
    # def field_class(options, key, val):
    #     if not isinstance(val, dict):
    #         raise FeildInVaildError(_('无效输入类型[{}]').format(key))

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
        self.opts_define = {}
        self.opts_args = {}
        self.opts_config = {}

    def reset_all(self):
        self.opts_define = {}
        self.opts_args = {}
        self.opts_config = {}

    def define(self, name, field_type, desc, default=DefaultUndefine(),
               update='false', maxlen=None,
               minlen=None, maxval=None, minval=None,
               regix=None, optional=True,
               opt_short_name=None, help_desc=''):

        if name in self.opts_define:
            raise FeildInVaildError('{} is defined'.format(name))

        self.opts_define[name] = FeildOption(
            name, field_type, desc, default=default,
            update=update, maxlen=maxlen,
            minlen=minlen, maxval=maxval, minval=minval,
            regix=regix, optional=optional,
            opt_short_name=opt_short_name,
            help_desc=help_desc)

    def get_opt(self, name, defval=DefaultUndefine()):
        opt = self.opts_define.get(name, None)
        if opt is None:
            raise FeildInVaildError('option not found')

        value = self.opts_args.get(name, defval)
        if not isinstance(value, DefaultUndefine):
            return value

        value = self.opts_config.get(name, defval)
        if not isinstance(value, DefaultUndefine):
            return value

        if not isinstance(defval, DefaultUndefine):
            return defval

        return opt.default

    def parse_opts(self, desc):
        parser = argparse.ArgumentParser(description=desc)

        parser.add_argument(
            '-c', '--config', default=None,
            help='config path (file://./config/main.ini|etcd://localhost)')  # noqa

        parser.add_argument(
            '-e', '--encoding', default='utf8',
            help='config encoding')  # noqa

        for i in self.opts_define.values():
            assert isinstance(i, FeildOption)
            parser.add_argument(*i.opt_arguments, default=DefaultUndefine(),
                                type=i.real_type, help=i.help_desc)

            # if isinstance(i.default, DefaultUndefine):
            #     parser.add_argument(*i.opt_arguments,
            #                         type=i.real_type, help=i.help_desc)
            # else:
            #     parser.add_argument(*i.opt_arguments, type=i.real_type,
            #                         default=i.default, help=i.help_desc)
        try:
            args = parser.parse_args()
        except Exception as ex:
            raise FeildInVaildError(ex)

        for i in self.opts_define.values():
            assert isinstance(i, FeildOption)
            value = getattr(args, i.opt_aname)
            if not isinstance(value, DefaultUndefine):
                self.opts_args[i.name] = value

        FeildCheck.field_checks(self.opts_args, self.opts_define, False)

        if args.config is None:
            return

        fpath = re.match(r'^file://(.*?)$', args.config)
        if fpath:
            self.parse_opts_file(fpath.group(1), args.encoding)
            return

        fpath = re.match(r'^etcd://(.*?)$', args.config)
        if fpath:
            self.parse_opts_etcd(args.config, args.encoding)
            return

    def parse_opts_file(self, path, encoding):
        with codecs.open(path, encoding=encoding) as fs:
            fs_config = configparser.ConfigParser()
            fs_config.read_file(fs)

        for i in self.opts_define.values():
            assert isinstance(i, FeildOption)
            if i.real_type == int:
                value = self.__get_value_int_def(
                    fs_config, i.opt_fsection, i.opt_fname, DefaultUndefine())
            elif i.real_type == bool:
                value = self.__get_value_boolen_def(
                    fs_config, i.opt_fsection, i.opt_fname, DefaultUndefine())
            elif i.real_type == str:
                value = self.__get_value_string_def(
                    fs_config, i.opt_fsection, i.opt_fname, DefaultUndefine())
            else:
                raise FeildInVaildError('parse_opts_file error')

            if not isinstance(value, DefaultUndefine):
                self.opts_config[i.name] = value

        FeildCheck.field_checks(self.opts_config, self.opts_define, False)

    def parse_opts_etcd(self, path, encoding):
        pass

    # ----------------------------------------------
    #        get file
    # ----------------------------------------------

    @staticmethod
    def __get_value_boolen_def(fs_config, section, option, defval):
        u"""获取boolen字段配置."""
        try:
            return fs_config.getboolean(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_int_def(fs_config, section, option, defval):
        u"""获取int字段配置."""
        try:
            return fs_config.getint(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_float_def(fs_config, section, option, defval):
        u"""获取int字段配置."""
        try:
            return fs_config.getfloat(section, option)
        except configparser.ParsingError:
            return defval
        except configparser.Error:
            return defval

    @staticmethod
    def __get_value_string_def(fs_config, section, option, defval):
        u"""获取string字段配置."""
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
