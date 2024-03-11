# GitHub Release Downloader

GitHub Release Downloader is a Python-based command-line tool that allows you to download specific releases and files from a GitHub repository.

## Installation

You can install GitHub Release Downloader directly from the GitHub repository using pip:

```bash
pip install git+https://github.com/ShinChven/gh-release-dl.git
```

## Upgrade

You can upgrade GitHub Release Downloader to the latest version using pip:

```bash
pip install --upgrade git+https://github.com/ShinChven/gh-release-dl.git
```

## Usage

After installation, you can use the `gh-release-dl` command to download releases. You will need to provide the URL of the GitHub repository as an argument:

```bash
gh-release-dl <GitHub repository URL>
```

The program will then fetch all releases from the provided GitHub repository. You will be prompted to select a release version, and then select a file from that release to download.

The selected file will be downloaded to the current working directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
