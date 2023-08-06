from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='lecroyparser',
      version='1.0',
      description='Parse LeCroy Binary Files.',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Physics'],
      keywords='LeCroy Binary Scope',
      url='http://github.com/bennomeier/lecroyparser',
      author='Benno Meier',
      author_email='meier.benno@gmail.com',
      license='MIT',
      packages=['lecroyparser'],
      include_package_data=True,
            install_requires = [
          'numpy',
          ],
      zip_safe=False)

