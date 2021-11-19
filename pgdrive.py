from pydrive2.drive import GoogleDrive
from pydrive2.auth import GoogleAuth
from tabulate import tabulate
from multipledispatch import dispatch
from os import scandir, mkdir
from os.path import basename, getsize, join, isfile
from mimetypes import guess_type
from tqdm import tqdm
from speedtest import Speedtest
from treelib import Tree


def get_gauth():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("credentials.json")
    if gauth.credentials is None:
        local_head = int(input("Enter '1' for Local Authenticating and '2' for Headless Authenticating: \n"))
        if local_head == 1:
            gauth.LocalWebserverAuth()
            return gauth
        else:
            gauth.CommandLineAuth()
            return gauth
    elif gauth.access_token_expired:
        gauth.Refresh()
        return gauth
    else:
        gauth.Authorize()
        return gauth


def init_drive_object(gauth):
    return GoogleDrive(gauth)


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_basic_info(drive):
    about = drive.GetAbout()
    print(tabulate([["name", about["name"]], ["emailAddress", about["user"]["emailAddress"]],
                    ["rootFolderId", about["rootFolderId"]],
                    ["quotaBytesTotal",
                     about["quotaBytesTotal"] + ' (' + sizeof_fmt(int(about["quotaBytesTotal"])) + ')'],
                    ["quotaBytesUsed", about["quotaBytesUsed"] + ' (' + sizeof_fmt(int(about["quotaBytesUsed"])) + ')'],
                    ]))


@dispatch(object)
def upload_file(drive):
    source_path = input("Enter the full path to file:\nsource_path = ").strip('\"')
    destination_path = input("Enter ID of folder on Google Drive:\ndestination_path = ").strip('\"')
    file = drive.CreateFile(
        {'parents': [{'id': destination_path}], 'title': basename(source_path), 'mimetype': guess_type(source_path)[0]})
    file.SetContentFile(source_path)
    with open(source_path, "rb") as fobj:
        total = getsize(source_path)
        with Tqdm.wrapattr(
                fobj,
                "read",
                desc=file['title'],
                total=total,
        ) as wrapped:
            if total:
                file.content = wrapped
            file.Upload()


@dispatch(object, str, str)
def upload_file(drive, source_path, destination_path):
    file = drive.CreateFile(
        {'parents': [{'id': destination_path}], 'title': basename(source_path), 'mimeType': guess_type(source_path)[0]})
    file.SetContentFile(source_path)
    with open(source_path, "rb") as fobj:
        total = getsize(source_path)
        with Tqdm.wrapattr(
                fobj,
                "read",
                desc=file['title'],
                total=total,
        ) as wrapped:
            if total:
                file.content = wrapped
            file.Upload()


def create_folder_drive(drive, folder_name, folder_path):
    folder_name = folder_name.strip('\"')
    folder_path = folder_path.strip('\"')
    file = drive.CreateFile(
        {'parents': [{'id': folder_path}], 'title': basename(folder_name),
         'mimeType': "application/vnd.google-apps.folder"})
    file.Upload()
    return file['id']


def scan_upload(drive, source_path, ids, base_path):
    s = scandir(source_path)
    for i in s:
        if i.is_dir():
            next_path = source_path + '\\' + i.name
            ids[next_path[next_path.find(base_path.split('\\')[-1]):]] = create_folder_drive(drive, i.name, ids[
                source_path[source_path.find(base_path.split('\\')[-1]):]])
            scan_upload(drive, next_path, ids, base_path)
        else:
            upload_file(drive, source_path + '\\' + i.name,
                        ids[source_path[source_path.find(base_path.split('\\')[-1]):]])


def upload_folder(drive):
    source_path = input("Enter the full path to folder:\nsource_path = ").strip('\"')
    destination_path = input("Enter ID of folder on Google Drive:\ndestination_path = ").strip('\"')
    print("Uploading...")
    base_path = source_path
    destination_path = create_folder_drive(drive, basename(source_path), destination_path)
    ids = {basename(source_path): destination_path}
    scan_upload(drive, source_path, ids, base_path)
    print("Upload Successful")


def perma_delete_file(drive):
    file_id = input("Enter ID of file:\n").strip('\"')
    file = drive.CreateFile({'parents': [{'id': file_id}]})
    file.Delete()


def send_trash_file(drive):
    file_id = input("Enter ID of file:\n").strip('\"')
    file = drive.CreateFile({'parents': [{'id': file_id}]})
    file.Trash()


def remove_trash_file(drive):
    file_id = input("Enter ID of file:\n").strip('\"')
    file = drive.CreateFile({'parents': [{'id': file_id}]})
    file.UnTrash()


def perma_delete_folder(drive):
    folder_path = input("Enter ID of folder on Google Drive:\nfolder_path = ").strip('\"')
    folder = drive.CreateFile({'id': folder_path})
    folder.Delete()
    print("Deleted")


def send_trash_folder(drive):
    folder_path = input("Enter ID of folder on Google Drive:\nfolder_path = ").strip('\"')
    folder = drive.CreateFile({'id': folder_path})
    folder.Trash()
    print("Sent to Trash")


def remove_trash_folder(drive):
    folder_path = input("Enter ID of folder on Google Drive:\nfolder_path = ").strip('\"')
    folder = drive.CreateFile({'id': folder_path})
    folder.UnTrash()
    print("Removed from Trash")


def file_info(drive):
    file_id = input("Enter ID of file on Google Drive:\nfile_path = ").strip('\"')
    file = drive.CreateFile({'id': file_id})
    print(tabulate(
        [["title", file["title"]], ["id", file["id"]], ["mimeType", file["mimeType"]], ["labels", file["labels"]],
         ["createdDate", file["createdDate"]], ["modifiedDate", file["modifiedDate"]],
         ["downloadUrl", file["downloadUrl"]], ["userPermission", file["userPermission"]],
         ["fileExtension", file["fileExtension"]], ["md5Checksum", file["md5Checksum"]], ["fileSize", file["fileSize"]],
         ["driveId", file["driveId"]]]))


class Tqdm(tqdm):
    def update_to(self, current, total):
        self.total = total
        self.update(current - self.n)

    def tdqm_or_callback_wrapped(fobj, method, total, callback=None, **pbar_kwargs):
        if callback:
            from funcy import nullcontext
            from tqdm.utils import CallbackIOWrapper

            callback.set_size(total)
            wrapper = CallbackIOWrapper(callback.relative_update, fobj, method)
            return nullcontext(wrapper)

        return Tqdm.wrapattr(fobj, method, total=total, bytes=True, **pbar_kwargs)


@dispatch(object)
def download_file(drive):
    source_path = input("Enter the fileId:\nfileId = ").strip('\"')
    destination_path = input("Enter full path of folder:\ndestination_path = ").strip('\"').rstrip('\\')
    file = drive.CreateFile({"id": source_path})
    output = destination_path + '\\' + file['title']
    mimetype = file['mimeType']
    file.FetchMetadata(fields="fileSize")
    size = int(file["fileSize"])
    chunksize = int(Speedtest().download())

    with Tqdm(desc=file['title']) as pbar:
        if size:
            file.GetContentFile(filename=output, mimetype=mimetype, remove_bom=True, chunksize=chunksize,
                                callback=pbar.update_to)
        else:
            with open(output, "w"):
                pass


@dispatch(object, str, str, int)
def download_file(drive, source_path, destination_path, chunksize):
    file = drive.CreateFile({"id": source_path})
    output = destination_path + '\\' + file['title']
    mimetype = file['mimeType']
    file.FetchMetadata(fields="fileSize")
    size = int(file["fileSize"])

    with Tqdm(desc=file['title']) as pbar:
        if size:
            file.GetContentFile(filename=output, mimetype=mimetype, remove_bom=True, chunksize=chunksize,
                                callback=pbar.update_to)
        else:
            with open(output, "w"):
                pass


def create_folder_local(folder_name, folder_path):
    folder_name = folder_name.strip('\"')
    folder_path = folder_path.strip('\"')
    path = join(folder_path, folder_name)
    try:
        mkdir(path)
    except FileExistsError:
        pass
    return path


def scan_download(drive, source_path, destination_path, paths, chunksize):
    s = drive.ListFile({'q': f"'{source_path}' in parents and trashed=false"}).GetList()
    for i in s:
        if i['mimeType'] == "application/vnd.google-apps.folder":
            next_path = create_folder_local(i['title'], destination_path)
            paths[i['id']] = destination_path + '\\' + i['title']
            scan_download(drive, i['id'], next_path, paths, chunksize)
        else:
            parent = i['parents'][0]['id']
            download_file(drive, i['id'], paths[parent], chunksize)


def download_folder(drive):
    source_path = input("Enter the folderId:\nfolderId = ").strip('\"')
    destination_path = input("Enter Id of folder:\ndestination_path = ").strip('\"').rstrip('\\')
    file = drive.CreateFile({"id": source_path})
    print("Downloading...")
    destination_path = create_folder_local(file['title'], destination_path)
    paths = {file['id']: destination_path}
    chunksize = int(Speedtest().download())
    scan_download(drive, source_path, destination_path, paths, chunksize)
    print("Download Successful")


def scan_folder(drive, tree, source_path):
    s = drive.ListFile({'q': f"'{source_path}' in parents and trashed=false"}).GetList()
    for i in s:
        if i['mimeType'] == "application/vnd.google-apps.folder":
            tree.create_node(i['title'] + '/', i['id'], source_path)
            scan_folder(drive, tree, i['id'])
        else:
            tree.create_node(i['title'], i['id'], source_path)


def list_files(drive):
    source_path = input("Enter the folderId:\nfolderId = ").strip('\"')
    tree = Tree()
    tree.create_node(drive.CreateFile({"id": source_path})['title'] + '/', source_path)
    scan_folder(drive, tree, source_path)
    tree.show()


def main():
    gauth = get_gauth()
    drive = init_drive_object(gauth)
    while 1:
        s = int(input("\n1. Get Basic Information about Account\n"
                      "2. Get Information about a File\n"
                      "3. List all Files and Folders in a Folder\n"
                      "4. Upload File\n"
                      "5. Upload Folder\n"
                      "6. Download File\n"
                      "7. Download Folder\n"
                      "8. Delete File Permanently\n"
                      "9. Delete Folder Permanently\n"
                      "10. Move File to Trash\n"
                      "11. Move Folder to Trash\n"
                      "12. Remove File from Trash\n"
                      "13. Remove Folder to Trash\n"
                      "14. Exit\n"
                      "\nEnter Selection: "))
        if s == 1:
            get_basic_info(drive)
        elif s == 2:
            file_info(drive)
        elif s == 3:
            list_files(drive)
        elif s == 4:
            upload_file(drive)
        elif s == 5:
            upload_folder(drive)
        elif s == 6:
            download_file(drive)
        elif s == 7:
            download_folder(drive)
        elif s == 8:
            perma_delete_file(drive)
        elif s == 9:
            perma_delete_folder(drive)
        elif s == 10:
            send_trash_file(drive)
        elif s == 11:
            send_trash_folder(drive)
        elif s == 12:
            remove_trash_file(drive)
        elif s == 13:
            remove_trash_folder(drive)
        elif s == 14:
            break
        else:
            print("Invalid Selection")


if __name__ == '__main__':
    main()
