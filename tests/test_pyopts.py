# -*- coding: utf-8 -*-

import os
import sys
import copy
import unittest
import asyncio
try:
    from pyopts import opts
    from pyopts import FeildInVaildError
except ImportError:
    import sys
    sys.path.insert(0, os.getcwd())
    from pyopts import opts
    from pyopts import FeildInVaildError

# fpath = os.path.abspath(os.path.dirname(__file__))


def test_init(func):

    def reset(self, *args, **kwargs):
        opts.reset_all()
        self.reset_sysargv()

        func(self, *args, **kwargs)
    return reset


class TestMathFunc(unittest.TestCase):
    """Test mathfuc.py"""

    DEFARGS = copy.deepcopy(sys.argv)

    def reset_sysargv(self):
        sys.argv = copy.deepcopy(self.DEFARGS)

    @test_init
    def test_a_default_value(self):
        opts.define('a.a', 'string', 'a.a', '1111')
        opts.define('a.b', 'int', 'a.b', '2222')
        opts.parse_opts('appname')
        self.assertEqual(opts.get_opt('a.a'), '1111')
        self.assertEqual(opts.get_opt('a.b'), '2222')

    @test_init
    def test_b_field_priority(self):
        '''test_b_field_priority

        argv > config > get_opt default > default
        '''
        sys.argv.append('--a_a=3333')
        sys.argv.append('--config=file://./tests/test.ini')
        opts.define('a.a', 'string', 'a.a', '1111')
        opts.define('a.b', 'string', 'a.b', '2222')
        opts.define('a.c', 'string', 'a.c', '5555')
        opts.parse_opts('appname')
        self.assertEqual(opts.get_opt('a.a'), '3333')
        self.assertEqual(opts.get_opt('a.b'), '4444')
        self.assertEqual(opts.get_opt('a.c', '7777'), '7777')
        self.assertEqual(opts.get_opt('a.c'), '5555')

    @test_init
    def test_c_field_typecheck(self):
        '''test_c_field_typecheck'''
        sys.argv.append('--config=file://./tests/test.ini')
        opts.define('a.f', 'string', 'a.f', '5555', maxlen=3)
        ex2 = None
        try:
            opts.parse_opts('appname')
        except FeildInVaildError as ex:
            ex2 = ex

        self.assertIsInstance(ex2, FeildInVaildError, 'must except')

    # @test_init
    # def test_c_init(self):
    #     sys.argv.append('--help')
    #     opts.define('a.a', 'string', 'a.a', '1111', help_desc='test a.a')
    #     opts.define('a.b', 'string', 'a.a', '2222', help_desc='test a.b')
    #     opts.define('a.c', 'string', 'a.a', '5555', help_desc='test a.c')
    #     opts.parse_opts('appname')


if __name__ == '__main__':
    unittest.main()
