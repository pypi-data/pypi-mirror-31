from setuptools import setup

setup(
    name='serial',
    version='0.0.62',
    description='A framework for serializing/deserializing JSON/YAML/XML into python class instances and vice versa',
    url='https://bitbucket.com/davebelais/serial.git',
    author='David Belais',
    author_email='david@belais.me',
    license='MIT',
    classifiers=[
        # 'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='rest api serialization serialize',
    packages=['serial'],
    install_requires=[
        'future>=0.16.0',
        'pyyaml>=3.12',
        'iso8601>=0.1.12',
    ],
)
