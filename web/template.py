# coding: utf-8
'''模版渲染，用的mako'''
import os, sys
import glob
import shutil
import traceback
from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import logging

log = logging.getLogger()

render = None

class Render:
    def __init__(self, loc="templates", tmpdir=None, cache=False, charset='utf-8'):
        self.loc = loc
        if cache:
            self.cache = {}
        else:
            self.cache = False

        self.charset = charset

        if tmpdir:
            if not os.path.isdir(tmpdir):
                os.mkdir(tmpdir)
            try:
                # rm old data
                exidirs = glob.glob(tmpdir + "/flying*")
                for d in exidirs:
                    shutil.rmtree(d)
            except:
                pass
            self.tmpdir = os.path.join(tmpdir, "flying."+str(os.getpid()))
        else:
            self.tmpdir = None

    def __call__(self, tplname, **args):
        return self.display(tplname, **args)

    def display(self, tplname, **args):
        try:
            if self.cache is False or tplname not in self.cache:
                mylookup = TemplateLookup(directories=[self.loc],
                                          filesystem_checks=False,
                                          module_directory=self.tmpdir,
                                          output_encoding=self.charset,
                                          encoding_errors='replace',
                                          default_filters=['decode.utf8'])
                c = mylookup.get_template(tplname)

                if self.cache is not False:
                    self.cache[tplname] = c

            if self.cache:
                c = self.cache[tplname]

            s = c.render(**args)

            return s
        except:
            log.error('\n=== template error ===' + exceptions.text_error_template().render() + '\n=== template error end ===')
            return 'template error!'

def install(loc="templates", tmpdir="/tmp", cache=False, charset='utf-8'):
    global render
    render = Render(loc, tmpdir, cache, charset)
    return render


def with_template(tpl_file, tpl_render=None):
    '''模版装饰器。自动将方法返回的数据作为模版参数'''
    def f(func):
        def _(self, *args, **kwargs):
            if not tpl_render:
                global render
                tpl_render = render
            x = func(self, *args, **kwargs)
            return tpl_render.display(tpl_file, **x)
        return _
    return f

def test():
    from zpy.base import logger
    log = logger.install('stdout')
    #loc = os.path.join(path, 'templates')
    loc = '/Users/jove/work/test/'
    r = Render(loc)
    print(r.display("test.html", name='xxx'))

if __name__ == '__main__':
    test()




