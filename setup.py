import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nabonassar",
    version="0.0.1",
    author="Tom Elliott",
    author_email="tom.elliott@nyu.edu",
    description="Data pre-processing for Shanati project",
    license="AGPL-3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_url="https://github.com/isawnyu/nabonassar",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10.6",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    install_requires=["airtight"],
    python_requires=">=3.10.6",
)
