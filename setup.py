from setuptools import setup


with open('requirements.txt', 'rb') as f:
    install_requires = f.read().decode('utf-8').split('\n')


setup(
    name='jetrics',
    version=0,
    description="Utility to get JIRA Metrics",
    author='Sid Premkumar',
    author_email='sid.premkumar@gmail.com',
    url='https://github.com/sidpremkumar/Jetrics',
    install_requires=install_requires,
    packages=[
        'Jetrics',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "jetrics=Jetrics.main:main",
        ],
    },
)