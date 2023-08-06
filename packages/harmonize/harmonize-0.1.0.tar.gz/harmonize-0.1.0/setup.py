import setuptools

setuptools.setup(
    name='harmonize',
    version='0.1.0',
    author='Andrew Rabert',
    author_email='ar@nullsum.net',
    license='Apache 2.0',
    packages=['harmonize'],
    install_requires=['consumers'],
    entry_points={
        'console_scripts': ['harmonize=harmonize:main']
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only'
    ),
)
