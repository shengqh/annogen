import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="annogen",
    version="0.1.0",
    author="Quanhu Sheng",
    author_email="quanhu.sheng.1@vumc.org",
    description="Annotate bed file with genome information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shengqh/annogen",
    entry_points = {
        'console_scripts': ['annogen=annogen.__main__:main'],
    },
    packages=['annogen'],
    package_dir={'annogen': 'src/annogen'},
    package_data={'annogen': ['data/*.*']},
    install_requires=['argparse', 'pytabix', 'numpy'],
    data_files=[('bin', ['bin/bedGraphToBigWig'])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)

