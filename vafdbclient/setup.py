import setuptools

exec(open("vafdbclient/version.py").read())

setuptools.setup(
    name="vafdb",
    author="Thomas Brier",
    version=__version__,  # type: ignore
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": "vafdb = vafdbclient.cli:main"},
)
