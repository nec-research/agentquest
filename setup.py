from setuptools import setup, find_packages

setup(
    name="agentquest",
    version="0.1",
    packages=find_packages(),
    install_requires=["levenshtein", "numpy", "termcolor"],
    include_package_data=True,
)
