import os
from shutil import copyfile

from jinja2 import Template as JTemplate

from tifa.consts import (
    JS_LIB_VERS,

    WEBPACK_MODE_DISABLE,
    WEBPACK_MODE_CLASSIC,
    WEBPACK_MODE_SEPARATE,
    WEBPACK_MODE_RADICAL,
)
from tifa.filters import underscore
from tifa.utils import isalpha

here = os.path.abspath(os.path.dirname(__file__))
_template_root = os.path.join(here, 'templates')


class Folder(object):
    def __init__(self, name, folders=None, files=None):
        self.name = name
        self.folders = folders
        self.files = files

    def render(self, path):
        folder_path = os.path.join(path, self.name)
        os.makedirs(folder_path)
        for folder in self.folders or []:
            folder.render(folder_path)
        files = self.files
        for file in files or []:
            file.render(folder_path)


class File(object):
    def __init__(self, name, origin, params=None):
        self.name = name
        self.origin = origin
        self.params = params

    def render(self, path):
        file_path = os.path.join(path, self.name)
        template_path = os.path.join(_template_root, self.origin)
        if self.params:
            with open(template_path, 'r') as f:
                template = JTemplate(f.read(), trim_blocks=True)
            content = template.render(**self.params)
            content += '\n'
            with open(file_path, 'w') as f:
                f.write(content)
        else:
            copyfile(template_path, file_path)


class Template(object):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def default_py_libs():
        return ['click', 'Flask', 'Jinja2']

    @property
    def name(self):
        return self.config['name']

    @property
    def routes(self):
        return self.config.get('routes')

    @property
    def models(self):
        return self.config.get('models')

    @property
    def confs(self):
        return self.config.get('confs')

    @property
    def webpack_mode(self):
        return self.config.get('webpack')

    @property
    def has_assets(self):
        return self.webpack_mode in [
            WEBPACK_MODE_CLASSIC, WEBPACK_MODE_RADICAL
        ]

    @property
    def has_vue(self):
        return self.webpack_mode in [
            WEBPACK_MODE_SEPARATE, WEBPACK_MODE_RADICAL
        ]

    def gen_routes(self):
        routes = self.routes
        if not routes:
            return None
        files = [File(
            name='{}.py'.format(route),
            origin='routes/route.py.j2',
            params=dict(name=route)
        ) for route in routes]
        files.append(
            File(
                name='__init__.py',
                origin='routes/__init__.py.j2',
                params=dict(routes=routes)
            )
        )
        return Folder(name='routes', files=files)

    def gen_models(self):
        models = self.models
        if not models:
            return None
        files = [File(
            name='{}.py'.format(underscore(model)),
            origin='models/table.py.j2',
            params=dict(cls=model)
        ) for model in models]
        files += [
            File(name='__init__.py', origin='models/__init__.py.j2',
                 params=dict(models=[(x, underscore(x)) for x in models])),
            File(name='base.py', origin='models/base.py.j2'),
        ]
        return Folder(name='models', files=files)

    def gen_template_folder(self):
        if not self.has_assets:
            return None
        return Folder(name='templates', files=[
            File(name='base.html', origin='html/base.html.j2')
        ])

    def gen_py_module(self):
        libs = Template.default_py_libs()

        module_folders = list()

        model_folder = self.gen_models()
        if model_folder:
            libs += ['Flask-SQLAlchemy', 'Flask-Alembic', 'PyMySQL']
            module_folders.append(model_folder)

        routes_folder = self.gen_routes()
        if routes_folder:
            module_folders.append(routes_folder)

        template_folder = self.gen_template_folder()
        if template_folder:
            module_folders.append(template_folder)

        config = self.config
        name = self.name
        routes = config.get('routes')
        models = config.get('models')
        return Folder(
            name=name, folders=module_folders,
            files=[
                File(
                    name='__init__.py', origin='__init__.py.j2',
                    params=dict(
                        routes=routes, models=models,
                        has_assets=self.has_assets
                    ),
                )
            ]
        ), libs

    def gen_confs(self):
        files = [
            File(name='base_settings.py',
                 origin='conf/base_settings.py.j2',
                 params=dict(has_assets=self.has_assets))
        ]
        domain = '<domain>'
        port = '<port>'
        confs = self.confs
        if confs:
            if 'supervisor' in confs:
                files.append(File(
                    name='supervisor.conf', origin='conf/supervisor.conf.j2',
                    params=dict(name=self.name)
                ))
            if 'gunicorn' in confs:
                files.append(File(
                    name='gunicorn_conf.py', origin='conf/gunicorn_conf.py.j2',
                    params=dict(port=port)
                ))
            if 'nginx' in confs:
                files.append(File(
                    name='nginx.conf', origin='conf/nginx.conf.j2',
                    params=dict(domain=domain, port=port)
                ))
        webpack_mode = self.webpack_mode
        if webpack_mode == WEBPACK_MODE_DISABLE:
            return Folder(name='conf', files=files)
        params = dict(mode=webpack_mode, has_vue=self.has_vue)
        webpack_base = File(
            name='webpack.base.js',
            origin='conf/webpack.base.js.j2', params=params)
        webpack_dev = File(
            name='webpack.dev.js',
            origin='conf/webpack.dev.js.j2', params=params)
        webpack_prod = File(
            name='webpack.prod.js',
            origin='conf/webpack.prod.js.j2', params=params)
        files += [webpack_base, webpack_dev, webpack_prod]
        if self.has_assets:
            assets = File(name='assets.json', origin='conf/assets.json.j2')
            files.append(assets)
        return Folder(name='conf', files=files)

    def gen_js_lib_file(self):
        """Generate package.json"""
        webpack_mode = self.webpack_mode
        if webpack_mode == WEBPACK_MODE_DISABLE:
            return None
        libs = []
        dev_libs = [
            'webpack', 'webpack-dev-server',
            'babel-core', 'babel-loader', 'babel-preset-env',
            'extract-text-webpack-plugin', 'css-loader', 'style-loader',
        ]
        if webpack_mode == WEBPACK_MODE_SEPARATE:
            dev_libs += ['html-webpack-plugin']
        if self.has_vue:
            libs += ['vue']
            dev_libs += ['vue-loader', 'vue-template-compiler']

        def _lib_row(lib):
            return '"' + lib + '": ' + '"' + JS_LIB_VERS[lib] + '"'

        libs = [_lib_row(x) for x in libs]
        dev_libs = [_lib_row(x) for x in dev_libs]
        return File(
            name='package.json',
            origin='package.json.j2',
            params=dict(libs=libs, dev_libs=dev_libs, name=self.name)
        )

    def gen_fn_folder(self):
        """Generate front-end folder"""
        if self.webpack_mode == WEBPACK_MODE_DISABLE:
            return None
        css_folder = Folder(name='css', files=[
            File(name='normalize.css', origin='fn/normalize.css.j2')
        ])
        root_files = [
            File(name='main.js', origin='fn/main.js.j2',
                 params=dict(webpack_mode=self.webpack_mode))
        ]
        if self.webpack_mode in [WEBPACK_MODE_SEPARATE, WEBPACK_MODE_RADICAL]:
            root_files.append(File(name='App.vue', origin='fn/App.vue.j2'))
        return Folder(name='fn', folders=[css_folder], files=root_files)

    @staticmethod
    def gen_py_lib_file(libs):
        """Generate Pipfile"""
        libs = [x if isalpha(x) else '"' + x + '"' for x in libs]
        return File(
            name='Pipfile',
            origin='Pipfile.j2',
            params=dict(libs=libs)
        )

    def render(self, path):
        name = self.name
        models = self.models
        module_folder, py_libs = self.gen_py_module()
        folders = [module_folder]
        conf_folder = self.gen_confs()
        if conf_folder:
            folders.append(conf_folder)
        fn_folder = self.gen_fn_folder()
        if fn_folder:
            folders.append(fn_folder)

        manage_file = File(
            name='manage.py', origin='manage.py.j2',
            params=dict(name=name, models=models)
        )
        files = [
            manage_file, self.gen_py_lib_file(py_libs),
            File(name='README.md', origin='readme.md.j2',
                 params=dict(name=self.name)),
        ]
        js_lib_file = self.gen_js_lib_file()
        if js_lib_file:
            files.append(js_lib_file)
        if self.webpack_mode:
            files.append(File(name='.babelrc', origin='conf/.babelrc.j2'))
        root = Folder(
            name=name,
            folders=folders,
            files=files
        )
        root.render(path)
