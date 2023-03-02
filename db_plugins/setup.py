from setuptools import setup
try:
    import db_plugins
except ImportError:
    import sys
    sys.path.append(".")
    import db_plugins

with open('requirements.txt', 'r') as fh:
    requirements = fh.readlines()

setup(
    name='db-plugins',
    version=db_plugins.__version__,
    packages=['db', 'db.sql', 'db.mongo', 'db.mongo.helpers', 'cli'],
    package_dir={'': 'db_plugins'},
    author='ALeRCE Team',
    author_email='contact@alerce.online',
    description='ALeRCE database plugins.',
    python_requires=">=3.6,<3.10",
    requires=requirements,
    extra_requires=[
        'psycopg2-binary',
        'pytest',
        'pytest-docker',
        'coverage',
        'alchemy_mock',
        'mongomock',
    ],
    entry_points={
        'console-scripts': [
            'dbp=db_plugins.cli.manage:cli'
        ]
    }
)
