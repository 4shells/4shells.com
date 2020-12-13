# Standard libraries
import os

# Third party libraries
import click
from starlette.templating import Jinja2Templates
import uvicorn

# Local libraries
import config.common
import config.server


@click.group(
    help=(
        'The 4s Comand Line Interface is a unified tool to manage your '
        'Four Shells services'
    ),
)
@click.option(
    '--data',
    default='~/.four-shells',
    help='State directory',
    show_default=True,
    type=str,
)
@click.option(
    '--debug',
    help='Enable debug mode',
    is_flag=True,
)
def main(
    *,
    data: str,
    debug: bool,
) -> None:
    config.common.DATA = os.path.abspath(os.path.expanduser(data))
    config.common.DATA_CACHIPFS = os.path.join(config.common.DATA, 'cachipfs')
    config.common.DATA_CACHIPFS_REPO = os.path.join(config.common.DATA_CACHIPFS, 'repo')
    config.common.DATA_EPHEMERAL = os.path.join(config.common.DATA, 'ephemeral')
    config.common.DEBUG = debug

    os.makedirs(config.common.DATA, mode=0o700, exist_ok=True)
    os.makedirs(config.common.DATA_CACHIPFS, mode=0o700, exist_ok=True)
    os.makedirs(config.common.DATA_CACHIPFS_REPO, mode=0o700, exist_ok=True)
    os.makedirs(config.common.DATA_EPHEMERAL, mode=0o700, exist_ok=True)

    config.common.spawn_ephemeral_paths()


@main.command(
    name='server',
)
@click.option(
    '--aws-access-key-id',
    required=True,
    type=str,
)
@click.option(
    '--aws-cloudfront-domain',
    required=True,
    type=str,
)
@click.option(
    '--aws-region',
    required=True,
    type=str,
)
@click.option(
    '--aws-secret-access-key',
    required=True,
    type=str,
)
@click.option(
    '--google-oauth-client-id',
    required=True,
    type=str,
)
@click.option(
    '--google-oauth-secret',
    required=True,
    type=str,
)
@click.option(
    '--host',
    help='Bind server to this host',
    required=True,
    type=str,
)
@click.option(
    '--port',
    help='Bind server to this port',
    required=True,
    type=int,
)
@click.option(
    '--production',
    is_flag=True,
)
@click.option(
    '--session-secret',
    required=True,
    type=str,
)
def main_server(
    *,
    aws_access_key_id: str,
    aws_cloudfront_domain: str,
    aws_region: str,
    aws_secret_access_key: str,
    host: str,
    port: str,
    production: bool,
    google_oauth_client_id: str,
    google_oauth_secret: str,
    session_secret: str,
) -> None:
    config.server.AWS_ACCESS_KEY_ID = aws_access_key_id
    config.server.AWS_CLOUDFRONT_DOMAIN = aws_cloudfront_domain
    config.server.AWS_REGION = aws_region
    config.server.AWS_SECRET_ACCESS_KEY = aws_secret_access_key
    config.server.CDN = 'https://' + (
        aws_cloudfront_domain
        if production
        else 'localhost:8401'
    )
    config.server.GOOGLE_OAUTH_CLIENT_ID = google_oauth_client_id
    config.server.GOOGLE_OAUTH_SECRET = google_oauth_secret
    config.server.PRODUCTION = production
    config.server.SESSION_SECRET = session_secret
    config.server.TPL = Jinja2Templates(
        directory=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'templates',
        ),
    )
    config.server.TPL.env.autoescape = False
    config.server.TPL.env.globals['from_cdn'] = config.server.from_cdn

    uvicorn.run(
        app='server.asgi:APP',
        host=host,
        interface='asgi3',
        log_level='debug' if config.common.DEBUG else 'info',
        loop='uvloop',
        port=port,
        workers=1,
    )


if __name__ == '__main__':
    try:
        main(
            prog_name='4s',
        )
    finally:
        config.common.delete_ephemeral_paths()
