import os
import sys

import click

from genius_cli.client import GeniusClient, ApiError
from genius_cli.utils import collect_files, extract_files, collect_app_names, migrate_db, install_deps, remove_db, \
    wait_for_file_changes, run_django


def run():
    api_token = os.environ.get('GENIUS_TOKEN', None)
    features_env = os.environ.get('GENIUS_FEATURES', None)

    if not api_token:
        print('No genius api token. Add GENIUS_TOKEN variable to your profile.')
        sys.exit(1)

    genius = GeniusClient(
        api_url=os.environ.get('GENIUS_URL', 'https://genius-project.io/en/api/'),
        token=api_token,
    )

    @click.group()
    def cli():
        pass

    @click.command()
    @click.option('--auto', is_flag=True, help='Generate and run migrations')
    @click.option('--install', is_flag=True, help='Install dependencies')
    @click.option('--watch', is_flag=True, help='Watch for changes')
    @click.option('--up', is_flag=True, help='--with=django + --install + --auto + --watch + --run')
    @click.option('--run', is_flag=True, help='Run django when generation ends')
    @click.option('--port', default='8000', help='Django host:port to run on')
    @click.option('--host', default=None, help='Django host:port to run on')
    @click.option('--rebuild', help='Rebuild application migrations')
    @click.option('--remove', help='Remove application migrations')
    @click.option('--src', default='.', help='Sources path')
    @click.option('--dst', default='.', help='Target path')
    @click.option('--name', help='Request name (for debug purposes)')
    @click.option('--with', default='', help='Extra features to use (coma separated)')
    @click.argument('app', nargs=-1)
    def gen(auto, src, dst, name, install, rebuild, remove, app, run, host, port, watch, up, **kwargs):
        if not host:
            host = '127.0.0.1:{}'.format(port)

        features = kwargs.get('with', features_env)

        if not features:
            features = []
        else:
            features = features.split(',')

        if up:
            install = True
            auto = True
            watch = True
            run = True

        if len(app) == 0:
            app = collect_app_names()

        src = os.path.realpath(src)
        dst = os.path.realpath(dst)

        if watch:
            print('Watching for changes...')

        django = None
        for i in wait_for_file_changes('**/*.col', watch=watch):
            if watch:
                print('Generating ...', end='')

            files = collect_files(src)

            try:
                data = genius.generate(files, name=name, collections=app, features=features)

                if django:
                    print('Terminating django...')
                    django.terminate()

                extract_files(dst, data['response']['files'])

                if remove:
                    remove_db(apps=app, features=features)

                if install or rebuild:
                    install_deps()

                if auto:
                    migrate_db(apps=app, features=features)

                if watch:
                    print('ok.')

                if run:
                    print('Starting django...')
                    django = run_django(features=features, run_host=host)

            except ApiError:
                pass

    gen()


