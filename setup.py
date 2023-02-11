import io
from setuptools import setup


with open('requirements.txt') as f:
    required = f.readlines()

version = {}
with open("src/lumber/version.py") as f:
    exec(f.read(), version)

setup(
    name='lumber-sdk',
    version=version["__version__"],
    description='An open-source Python SDK for connecting to the LumberHub platform',
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/hivecv/lumber-sdk',
    keywords="data aggregation device configuration open source development kit",
    author='HiveCV',
    author_email='lukasz@hivecv.com',
    license_files=('LICENSE',),
    packages=['lumber'],
    package_dir={"": "src"},
    install_requires=required,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
