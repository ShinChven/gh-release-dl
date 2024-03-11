import os
import requests
import argparse
import inquirer
import tqdm

def get_latest_release(repo_url: str) -> dict:
  """Fetches the latest release data from the GitHub API."""
  owner, repo = repo_url.split("/")[-2:]
  api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
  response = requests.get(api_url)
  response.raise_for_status()
  return response.json()

def get_download_options(release_data):
  """Extracts download options from the release information."""
  options = []
  for asset in release_data['assets']:
    options.append((asset['browser_download_url'], asset['name']))
  return options

def select_download(options):
  """Provides a selection interface for the user."""
  questions = [
    inquirer.List('asset',
              message="Select the file to download",
              choices=[option[1] for option in options],
              ),
  ]
  answers = inquirer.prompt(questions)

  selected_option = None
  for i, (url, filename) in enumerate(options):
    if filename == answers['asset']:
      selected_option = i
      break

  if selected_option is not None:
    return options[selected_option][0]
  else:
    print("Error: Selected file not found.")
    return None

def download_file(url, download_path):
  """Downloads the file, checking for existing files and showing a progress bar."""
  filename = os.path.basename(url)
  filepath = os.path.join(download_path, filename)

  # Ensure the download path exists
  os.makedirs(download_path, exist_ok=True) 

  if os.path.exists(filepath):
    print(f"File {filename} already exists. Skipping download.")
    return

  response = requests.get(url, stream=True)
  response.raise_for_status()

  total_size = int(response.headers.get('content-length', 0))
  with open(filepath, 'wb') as f:
    with tqdm.tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as progress_bar:
      for chunk in response.iter_content(chunk_size=1024):
        if chunk:
          f.write(chunk)
          progress_bar.update(len(chunk))
  print(f"Download complete: {filepath}")

def gh_release_dl():
  parser = argparse.ArgumentParser(description="Download installer from GitHub releases")
  parser.add_argument('repo_url', help="GitHub repository URL")
  args = parser.parse_args()

  download_folder = os.getcwd()  # Download to the current working directory

  try:
    release_data = get_latest_release(args.repo_url)
    download_options = get_download_options(release_data)
    download_url = select_download(download_options)

    if download_url:
      download_file(download_url, download_folder)

  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

if __name__ == '__main__':
  gh_release_dl()
