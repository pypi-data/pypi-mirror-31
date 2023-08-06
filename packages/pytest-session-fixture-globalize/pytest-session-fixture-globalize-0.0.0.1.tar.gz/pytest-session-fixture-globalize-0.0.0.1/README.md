# pytest-session-fixture-globalize

pytest-forcefail is a plugin to make scope='session' fixtures behave as if written in conftest.py.

See test\_session\_fixture\_globalize.py for example.

Unlike usual plugin, this touches the deep area of \_pytest.fixtures.FixtureManager. **You have to enable this plugin explicitly by --session-fixture-globalize option or PYTEST\_SESSION\_FIXTURE\_GLOBALIZE env.**

Binary distribution: https://pypi.org/project/pytest-session-fixture-globalize/
