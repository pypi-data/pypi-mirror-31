from setuptools import setup, find_packages

setup(
    name = 'netbluemind',
    packages = find_packages(),
    version = '3.1.28073-1',
    description = 'Automatically generated client for BlueMind REST API',
    author = 'BlueMind team',
    author_email = 'contact@bluemind.net',
    url = 'http://git.blue-mind.net/gitlist/bluemind/',
    keywords = ['bluemind', 'rest', 'api', 'mail', 'groupware'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    install_requires=["enum34; python_version < '3.4'", 'requests'],
)
