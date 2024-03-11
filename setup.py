from setuptools import find_packages, setup

setup(
    name='gh_release_dl',  # Package name (what you'll use with pip install)
    version='0.0.1',  # Version of your package
    description='A CLI tool to download installers from GitHub releases',
    author='ShinChven',
    author_email='shinchven@gmail.com',
    packages=find_packages(),  # Automatically find your Python code
    install_requires=[  # List dependencies here
        'requests',
        'inquirer',
        'tqdm',
        'argparse',
        
    ],
    entry_points={
        'console_scripts': [
            'gh-release-dl=gh_release_dl.main:gh_release_dl'  # Command to invoke your script
        ]
    },
)
