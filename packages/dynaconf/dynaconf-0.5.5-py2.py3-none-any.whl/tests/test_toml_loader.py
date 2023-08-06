import pytest
from dynaconf import LazySettings
from dynaconf.loaders.toml_loader import load

settings = LazySettings(
    DYNACONF_NAMESPACE='EXAMPLE',
)


TOML = """
[example]
password = 99999.0
host = "server.com"
port = 8080.0

  [example.service]
  url = "service.com"
  port = 80.0

    [example.service.auth]
    password = "qwerty"
    test = 1234.0

[development]
password = 88888.0
host = "dev_server.com"
"""

TOML2 = """
[example]
secret = "@float 42"
password = 123456.0
"""

TOMLS = [TOML, TOML2]


def test_load_from_toml():
    """Assert loads from TOML string"""
    load(settings, filename=TOML)
    assert settings.HOST == 'server.com'
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=TOML, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    load(settings, filename=TOML)
    assert settings.HOST == 'server.com'


def test_load_from_multiple_toml():
    """Assert loads from TOML string"""
    load(settings, filename=TOMLS)
    assert settings.HOST == 'server.com'
    assert settings.PASSWORD == 123456
    assert settings.SECRET == 42.0
    assert settings.PORT == 8080
    assert settings.SERVICE['url'] == 'service.com'
    assert settings.SERVICE.url == 'service.com'
    assert settings.SERVICE.port == 80
    assert settings.SERVICE.auth.password == 'qwerty'
    assert settings.SERVICE.auth.test == 1234
    load(settings, filename=TOMLS, namespace='DEVELOPMENT')
    assert settings.HOST == 'dev_server.com'
    assert settings.PASSWORD == 88888
    load(settings, filename=TOMLS)
    assert settings.HOST == 'server.com'
    assert settings.PASSWORD == 123456


def test_no_filename_is_none():
    """Assert if passed no filename return is None"""
    assert load(settings) is None


def test_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in TOML"""
    with pytest.raises(KeyError):
        load(settings, filename=TOML, namespace='FOOBAR', silent=False)


def test_no_key_error_on_invalid_namespace():
    """Assert error raised if namespace is not found in TOML"""
    load(settings, filename=TOML, namespace='FOOBAR', silent=True)


def test_load_single_key():
    """Test loading a single key"""
    toml = """
    [foo]
    bar = "blaz"
    zaz = "naz"
    """
    load(settings, filename=toml, namespace='FOO', key='bar')
    assert settings.BAR == 'blaz'
    assert settings.exists('BAR') is True
    assert settings.exists('ZAZ') is False
