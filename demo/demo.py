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
