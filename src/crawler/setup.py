from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = [r for r in f.readlines() if not r.startswith('git+http')]

setup(
    name='crawler',
    version="1.0.0",
    author='Bar Z',
    packages=find_packages(),
    install_requires=required
)
