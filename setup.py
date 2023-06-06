import setuptools

with open("README.md", "r") as file:
    readme = file.read()

setuptools.setup(
    name="backtestify",
    version="0.1.5",
    author="Eladio Rocha Vizcaino",
    author_email="eladio.rocha99@gmail.com",
    description="A package for backtesting trading strategies",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/EladioRocha/backtestify",
    project_urls={
        "Bug Tracker": "https://github.com/EladioRocha/backtestify/issues"
    },
    license="Apache License 2.0",
    packages=["backtestify"],
    install_requires=["pandas"]
)