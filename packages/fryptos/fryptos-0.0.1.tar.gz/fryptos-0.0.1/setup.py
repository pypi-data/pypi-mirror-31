"""Set up script"""
from setuptools import setup

setup(name="fryptos",
      version='0.0.1',
      description='Encrypt files.',
      # long_description="",
      # TODO: Add classifiers.
      classifiers=[
          'Programming Language :: Python'
         ],
      keywords='encrypt file',
      author='Shohei Mukai',
      author_email='mukaishohei76@gmail.com',
      url = 'https://github.com/pyohei/Fryptos',
      packages=['fryptos'],
      entry_points={
          'console_scripts': [
              'fryptos = fryptos.main:execute'],
          },
      license='MIT',
      install_requires=[],
      )

