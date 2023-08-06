import setuptools
import os


setuptools.setup(
  name='slag',
  version="0.1.6",
  description='A distributed micro-blog social network on the block chain.',
  long_description=open('README.md').read().strip(),
  author='John Weachock',
  author_email='jweachock@gmail.com',
  url='https://github.com/scizzorz/slag',
  py_modules=['slag'],
  scripts=['bin/slag'],
  install_requires=list(l.strip() for l in open('requirements.txt') if l),
  include_package_data=True,
  license='MIT License',
  zip_safe=False,
  keywords='git blog',
)
