# run: pip install pydrive

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from os import path
import itertools

settings_dir = 'Cloud_auth'
auth_file = path.join(os.getcwd(), settings_dir, 'Google_auth.json')
folder_on_drive = "Measurements"


class GoogleDriveUploader:
    @staticmethod
    def __GetDrivePath(source_path):
        base, p1 = path.split(source_path)
        base2, p2 = path.split(base)
        return path.join(folder_on_drive, p2, p1)

    @staticmethod
    def __add_parent(dic, id_parent):
        dic['parents'] = [{'kind': 'drive#fileLink', 'id': id_parent}]

    def __create_folder(self, folder_name, parent_id=None):
        folder_metadata = {'title': folder_name, 'mimeType': r'application/vnd.google-apps.folder'}
        if parent_id is not None:
            self.__add_parent(folder_metadata, parent_id)

        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()

        return folder['id']

    def __is_object_exists(self, folder_name, parent_id=None):
        if parent_id is None:
            parent_id = 'root'
        strList = f"'{parent_id}' in parents and trashed=false"
        file_list = self.drive.ListFile({'q': strList})
        # a bug in the library: returns list of lists, not just list
        for cf in itertools.chain(*list(file_list)):
            if cf['title'] == folder_name:
                return cf['id']
        return None

    def __create_folders(self, full_path):
        if full_path[0] == r'/' or full_path[0] == '\\':
            full_path = full_path[1:]
        if full_path[-1] == r'/' or full_path[-1] == '\\':
            full_path = full_path[:-1]
        prev_id = None
        for subdir in full_path.split('\\'):
            curr_id = self.__is_object_exists(subdir, parent_id=prev_id)
            if curr_id is None:  # if exists, then create
                prev_id = self.__create_folder(subdir, parent_id=prev_id)
            else:
                prev_id = curr_id  # else leave existing folder
        return prev_id

    def __upload_file(self, filepath, folder_id=None):
        fname = path.split(filepath)[-1]
        dic = {'title': fname}
        if folder_id is not None:
            self.__add_parent(dic, folder_id)
        if self.__is_object_exists(fname, folder_id):
            print('File', fname, 'already exists, skipping...')
        f = self.drive.CreateFile(dic)
        f.SetContentFile(filepath)
        f.Upload()

    def __init__(self):
        try:
            gauth = GoogleAuth()
            gauth.DEFAULT_SETTINGS['client_config_file'] = path.join(os.getcwd(), settings_dir, 'client_secrets.json')

            if path.exists(auth_file):
                gauth.LoadCredentialsFile(credentials_file=auth_file)

            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(credentials_file=auth_file)

            self.gauth = gauth

            self.drive = GoogleDrive(gauth)
        except Exception as e:
            print('Google Drive authorization failed')
            self.gauth = None
            print(e)

    # uploads a folder with measurements results to Google drive
    # puts it into folder which name is specified by folder_on_drive variable
    # creates there two last folders from path
    def UploadMeasFolder(self, dir_path):
        print('Uploading results to Google drive...')
        try:
            folder = self.__GetDrivePath(dir_path)
            idFolder = self.__create_folders(folder)

            for f in os.listdir(dir_path):
                print('Uploading:', f)
                full_fpath = path.join(dir_path, f)
                self.__upload_file(full_fpath, idFolder)
            print('Data were successfully uploaded to:', folder)
        except Exception as e:
            print('Unable to upload data onto Google Drive')
            print(e)
