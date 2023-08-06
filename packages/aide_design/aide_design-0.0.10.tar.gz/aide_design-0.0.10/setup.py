from setuptools import setup, find_packages

setup(name='aide_design',
      version='0.0.10',
      description='AguaClara Infrastructure Design Engine',
      url='https://github.com/AguaClara/aguaclara_design',
      author='AguaClara at Cornell',
      author_email='aguaclara@cornell.edu',
      license='MIT',
      packages=find_packages(),
      install_requires=['pint','numpy','pandas','matplotlib'],
      include_package_data=True,
      test_suite="tests",
      zip_safe=False)
