import os.path
import gdown
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

GOOGLE_DRIVE=''

def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results_all = (
        service.files() #
        .list(pageSize=10, supportsAllDrives=True, includeItemsFromAllDrives=True, q=f'\'{GOOGLE_DRIVE}\' in parents  and mimeType = \'application/vnd.google-apps.folder\'', fields="nextPageToken, files(id)")
        .execute()
    )

    items = results_all.get("files", [])
    # print(items)
  #
    if not items:
      # print("No folders found.")
      return
    for item in items:
      folderId = item['id']
      results = (
        service.files() #and name = \'{sys.argv[1]}\'
        .list(pageSize=10, supportsAllDrives=True, includeItemsFromAllDrives=True, q=f'\'{folderId}\' in parents and name = \'{sys.argv[1]}\' and mimeType = \'application/vnd.google-apps.folder\'', fields="nextPageToken, files(id, name)")
        .execute()
      )
      items_in_folder = results.get("files", [])
      if not items_in_folder:
          continue
      for item_i in items_in_folder:
          url = f"https://drive.google.com/drive/folders/{item_i['id']}"
          gdown.download_folder(url)
          return
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        pass
        main()
    else:
        print("add argument")