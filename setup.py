import setuptools

with open("README.md", "r") as file:
    more_description = file.read()

setuptools.setup(
    name="backtestify",
    version="0.1.4",
    author="Eladio Rocha Vizcaino",
    author_email="eladio.rocha99@gmail.com",
    description="A package for backtesting trading strategies",
    more_description=more_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EladioRocha/backtestify",
    project_urls={
        "Bug Tracker": "https://github.com/EladioRocha/backtestify/issues"
    },
    license="Apache License 2.0",
    packages=["backtestify"],
    install_requires=["pandas"]
)