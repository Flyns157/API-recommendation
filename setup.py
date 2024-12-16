from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.in") as f:
    required = f.read().splitlines()

setup(
    name="Recommender",
    version="0.1.0",
    author="Cuisset Mattéo, Delcambre Jean-Alexis",
    author_email="matteo.cuisset@gmail.com, ja.delcambre@gmail.com ",
    description="A Flask-based recommendation API service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.univ-artois.fr/sae5/api-recommendation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=required,
    entry_points={
        "console_scripts": [
            "recommender=Recommender.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
