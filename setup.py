import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="royston",
    version="0.0.7",
    author="Ian Read",
    author_email="ianharveyread@gmail.com",
    description="Trending news library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/readikus/royston",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)
