import re
from setuptools import setup

def get_latest_version(changelog):
    """Retrieve latest version of package from changelog file."""
    # Match strings like "## [1.2.3] - 2017-02-02"
    regex = r"^##\s*\[(\d+.\d+.\d+)\]\s*-\s*\d{4}-\d{2}-\d{2}$"
    with open(changelog, "r") as changelog:
        content = changelog.read()
    return re.search(regex, content, re.MULTILINE).group(1)

setup(
    name='sphinxcontrib-lookup-yaml',
    url='https://github.com/Jakski/sphinxcontrib-lookup-yaml',
    author='Jakub Pieńkowski',
    author_email='jakski@sealcode.org',
    license='MIT',
    description='Sphinx extension to lookup YAML values',
    platforms='any',
    version=get_latest_version('CHANGELOG'),
    packages=['sphinxcontrib.lookup_yaml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Documentation'
    ],
    install_requires=[
        'sphinx',
        'pyyaml'
    ],
    test_suite='tests.test_lookup_yaml.TestLookupYAML',
    tests_require=[
        'sphinx-testing'
    ],
)
