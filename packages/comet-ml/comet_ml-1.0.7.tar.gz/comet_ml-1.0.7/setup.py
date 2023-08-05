import setuptools

setuptools.setup(
    name="comet_ml",
    packages=['comet_ml'],
    version="1.0.7",
    url="https://www.comet.ml",
    author="Comet ML Inc.",
    author_email="mail@comet.ml",
    description="Supercharging Machine Learning",
    long_description=open('README.rst').read(),
    install_requires=[
        "websocket-client>=0.44.0", "requests>=2.18.4", "six",
        "wurlitzer>=1.0.1"
    ],
    test_requires=['websocket-server', 'pytest', 'responses'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
