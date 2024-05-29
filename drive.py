import os.path
import io
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


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
    results = (
        service.files()
        .list(pageSize=10, supportsAllDrives=True, includeItemsFromAllDrives=True, q=f'name = \'{sys.argv[1]}\' and mimeType = \'application/vnd.google-apps.folder\'', fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      print("No files found.")
      return
    for item in items:
      folderId = item['id']
      destinationFolder = sys.argv[1]
      downloadFolder(service, folderId, destinationFolder)
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


def downloadFolder(service, fileId, destinationFolder):
    if not os.path.isdir(destinationFolder):
        os.mkdir(path=destinationFolder)

    results = service.files().list(
        pageSize=300,
        q="parents in '{0}'".format(fileId),
        fields="files(id, name, mimeType)"
        ).execute()

    items = results.get('files', [])

    for item in items:
        itemName = item['name']
        itemId = item['id']
        itemType = item['mimeType']
        filePath = destinationFolder + "/" + itemName

        if itemType == 'application/vnd.google-apps.folder':
            print("Stepping into folder: {0}".format(filePath))
            downloadFolder(service, itemId, filePath) # Recursive call
        elif not itemType.startswith('application/'):
            downloadFile(service, itemId, filePath)
        else:
            print("Unsupported file: {0}".format(itemName))


def downloadFile(service, fileId, filePath):
    # Note: The parent folders in filePath must exist
    print("-> Downloading file with id: {0} name: {1}".format(fileId, filePath))
    request = service.files().get_media(fileId=fileId)
    fh = io.FileIO(filePath, mode='wb')

    try:
        downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)

        done = False
        while done is False:
            status, done = downloader.next_chunk(num_retries = 2)
            if status:
                print("Download %d%%." % int(status.progress() * 100))
        print("Download Complete!")
    finally:
        fh.close()

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        pass
        main()
    else:
        print("add argument")