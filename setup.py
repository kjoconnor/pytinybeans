import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytinybeans",
    version="1.0",
    author="Kevin O'Connor",
    author_email="kjoconnor@gmail.com",
    description="Python library to interact with the Tinybeans API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kjoconnor/pytinybeans",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.5",
    install_requires=["requests",],
)
