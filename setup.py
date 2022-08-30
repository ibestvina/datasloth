from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='datasloth',
    version='0.1',
    description='Natural language Pandas queries',
    url='http://github.com/ibestvina/datasloth',
    author='Ivan Bestvina',
    author_email='ivan.bestvina@gmail.com',
    license='MIT',
    packages=['datasloth'],
    zip_safe=False,
    install_requires=[
        'openai',
        'pandas',
        'pandasql'
    ],
    long_description=readme(),
)