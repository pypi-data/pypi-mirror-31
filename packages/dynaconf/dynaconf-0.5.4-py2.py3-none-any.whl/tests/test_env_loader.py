import os
from dynaconf.loaders.env_loader import load
from dynaconf import settings  # noqa

os.environ['DYNACONF_HOSTNAME'] = 'host.com'
os.environ['DYNACONF_PORT'] = '@int 5000'
os.environ['DYNACONF_VALUE'] = '@float 42.1'
os.environ['DYNACONF_ALIST'] = '@json ["item1", "item2", "item3"]'
os.environ['DYNACONF_ADICT'] = '@json {"key": "value"}'
os.environ['DYNACONF_DEBUG'] = '@bool true'
os.environ['PROJECT1_HOSTNAME'] = 'otherhost.com'
os.environ['PROJECT1_PORT'] = '@int 8080'

settings.configure()


def test_env_loader():
    assert settings.HOSTNAME == 'host.com'


def test_single_key():
    load(settings, namespace='PROJECT1', key='HOSTNAME')
    assert settings.HOSTNAME == 'otherhost.com'
    assert settings.PORT == 5000


def test_dotenv_loader():
    assert settings.DOTENV_INT == 1
    assert settings.DOTENV_STR == "hello"
    assert settings.DOTENV_FLOAT == 4.2
    assert settings.DOTENV_BOOL is False
    assert settings.DOTENV_JSON == ['1', '2']
    assert settings.DOTENV_NOTE is None


def test_dotenv_other_namespace_loader():
    load(settings, namespace='FLASK')
    assert settings.DOTENV_STR == "flask"
