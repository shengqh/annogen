import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="annotateGenome",
    version="0.0.8",
    author="Quanhu Sheng",
    author_email="quanhu.sheng.1@vumc.org",
    description="Annotate bed file with genome information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shengqh/annotateGenome",
    entry_points = {
        'console_scripts': ['annotateGenome=annotateGenome.__main__:main'],
    },
    packages=setuptools.find_packages(),
    package_data={'annotateGenome': ['data/*.bed']},
    install_requires=['argparse', 'pytabix', 'numpy'],
    data_files=[('bin', ['bin/bedGraphToBigWig', 'bin/cmpr2in.R'])],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)

