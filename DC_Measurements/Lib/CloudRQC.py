import os
from os import path
from webdav3.client import Client


class NextCloudUploader:
    @staticmethod
    def __get_password():
        settings_dir = 'Cloud_auth'
        auth_file = path.join(os.getcwd(), settings_dir, 'Nextcloud_auth')
        with open(auth_file, 'r') as f:
            passwd = f.read()
        return passwd.strip().split(',')

    def __init__(self):
        url, login, passwd = self.__get_password()
        options = {
            'webdav_hostname': url,
            'webdav_login': login,
            'webdav_password': passwd
        }
        self.client = Client(options)

    def UploadFolder(self, meas_path):
        print('Uploading results to Google drive...')
        try:
            client = self.client
            base_dir = r'/Superconductor/DC_Measurements/'
            base, end = path.split(meas_path)
            base, end2 = path.split(base)

            path1 = path.join(base_dir, end2)
            if not client.check(path1):
                client.mkdir(path1)

            path2 = fr'{path1}/{end}'
            if not client.check(path2):
                client.mkdir(path2)

            client.upload_sync(remote_path=path2, local_path=meas_path)
        except Exception as e:
            print('Unable to upload to RQC NextCloud')
            print(e)
        else:
            print('Data were successfully uploaded to:', path2)
