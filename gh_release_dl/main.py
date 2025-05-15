import os
import requests
import argparse
import inquirer
import tqdm

def get_all_releases(repo_url: str) -> list:
  """Fetches all release data from the GitHub API."""
  if "://" in repo_url: # Check if it's a full URL
    owner, repo = repo_url.split("/")[-2:]
  else: # Assume it's in the format <username>/<reponame>
    owner, repo = repo_url.split("/")
  api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
  response = requests.get(api_url)
  response.raise_for_status()
  return response.json()

def select_release(releases):
  """Provides a selection interface for the user to choose a release or exit."""
  release_tags = [release['tag_name'] for release in releases]
  choices = ["Exit"] + release_tags

  default_choice = None
  if release_tags: # Set default to the first actual release tag
    default_choice = release_tags[0]

  questions = [
    inquirer.List('release_choice',
              message="🚀 Select a release version (or Exit)", # Changed emoji
              choices=choices,
              default=default_choice, # Set the default selection
              ),
  ]
  answers = inquirer.prompt(questions)

  if not answers: # Handles Ctrl+D or other cancellation returning None
    return "EXIT_PROGRAM"

  selected_value = answers.get('release_choice')

  if selected_value == "Exit":
    return "EXIT_PROGRAM"

  # Find the selected release object
  for release in releases:
    if release['tag_name'] == selected_value:
      return release

  # This part should ideally not be reached if inquirer works as expected
  # and the selected_value was a valid tag_name.
  print("Error: Selected release tag not found in release list (unexpected).")
  return None

def get_download_options(release_data):
  """Extracts download options from the release information."""
  options = []
  for asset in release_data['assets']:
    options.append((asset['browser_download_url'], asset['name']))
  return options

def select_download(options):
  """Provides a selection interface for the user."""
  choices = ["Back"] + [option[1] for option in options]
  questions = [
    inquirer.List('asset',
              message="📦 Select the file to download (or Back)",
              choices=choices,
              ),
  ]
  answers = inquirer.prompt(questions)

  if answers['asset'] == "Back":
    return "BACK"

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
    releases = get_all_releases(args.repo_url)
    if not releases:
      print("No releases found for this repository.")
      return

    while True: # Main interaction loop
      selected_release_data = select_release(releases)

      if selected_release_data == "EXIT_PROGRAM":
        print("Exiting program.")
        break

      if selected_release_data is None:
        # Error message already printed by select_release or indicates an issue.
        print("Exiting due to an issue in release selection.")
        break

      # At this point, selected_release_data is a valid release dictionary
      download_options = get_download_options(selected_release_data)
      if not download_options:
        print(f"No downloadable files found for release '{selected_release_data['tag_name']}'. Please select another release.")
        continue # Go back to release selection

      download_url = select_download(download_options)

      if download_url == "BACK":
        print("Returning to release selection...")
        continue # Go back to release selection

      if download_url: # A file URL was returned
        download_file(download_url, download_folder)
        # Assuming successful download means the task is complete.
        break # Exit the while loop
      else:
        # select_download returned None (error selecting file, message already printed by select_download)
        print("No file selected or error in file selection. Returning to release selection.")
        continue # Go back to release selection

  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
  except (KeyboardInterrupt, EOFError):
    print("\nUser cancelled. Exiting.")
  except Exception as e: # Catch any other unexpected errors
    print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
  gh_release_dl()
