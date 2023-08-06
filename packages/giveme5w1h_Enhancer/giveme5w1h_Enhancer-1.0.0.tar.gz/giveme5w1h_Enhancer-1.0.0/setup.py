from setuptools import setup, find_packages

setup(name='giveme5w1h_Enhancer',
      version='1.0.0',
      description="Extraction of the journalistic five W and one H questions (5W1H) from news articles.",
      long_description="""Giveme5W1H_Enhancer is an open source, easy-to-use system to that extracts phrases answering the journalist 5W1H questions to describe an article's main event: who did what, when, where, why, and how?""",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet',
          'Topic :: Scientific/Engineering :: Information Analysis',
      ],
      keywords='question answering news event detection event extraction 5w fivew 5w1h fivewoneh question-answering qa reporters questions',
      author='Felix Hamborg',
      author_email='felix.hamborg@uni-konstanz.de',
      url='https://github.com/fhamborg/Giveme5W_NewsCluster_enhancer',
      download_url='https://github.com/fhamborg/Giveme5W_NewsCluster_enhancer',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'requests',
        'python_dateutil',
        'extractor',
        'xmltodict',
      ],
      extras_require={
      }
)
