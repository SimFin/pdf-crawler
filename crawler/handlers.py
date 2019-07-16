import csv
import os
import uuid
from urllib.parse import urlparse
import psutil


class LocalStoragePDFHandler:
    def __init__(self, directory, subdirectory):
        self.directory = directory
        self.subdirectory = subdirectory

    def handle(self, response, *args, **kwargs):
        parsed = urlparse(response.url)
        filename = str(uuid.uuid4()) + ".pdf"
        subdirectory = self.subdirectory or parsed.netloc
        directory = os.path.join(self.directory, subdirectory)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, filename)
        path = _ensure_unique(path)
        with open(path, 'wb') as f:
            f.write(response.content)

        return path


class CSVStatsPDFHandler:
    _FIELDNAMES = ['filename', 'local_name', 'url', 'linking_page_url', 'size', 'depth']

    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        os.makedirs(directory, exist_ok=True)

    def get_handled_list(self):
        list_handled = []
        if self.name:
            file_name = os.path.join(self.directory, self.name + '.csv')
            if os.path.isfile(file_name):
                with open(file_name, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for k, row in enumerate(reader):
                        if k > 0:
                            list_handled.append(row[2])
        return list_handled

    def handle(self, response, depth, previous_url, local_name, *args, **kwargs):
        parsed_url = urlparse(response.url)
        name = self.name or parsed_url.netloc
        output = os.path.join(self.directory, name + '.csv')
        if not os.path.isfile(output):
            with open(output, 'w', newline='') as file:
                csv.writer(file).writerow(self._FIELDNAMES)

        with open(output, 'a', newline='') as file:
            writer = csv.DictWriter(file, self._FIELDNAMES)
            filename = get_filename(parsed_url)
            row = {
                'filename': filename,
                'local_name': local_name,
                'url': response.url,
                'linking_page_url': previous_url or '',
                'size': response.headers.get('Content-Length') or '',
                'depth': depth,
            }
            writer.writerow(row)


class ProcessHandler:

    def __init__(self):
        self.process_list = []

    def register_new_process(self, pid):
        self.process_list.append(int(pid))

    def kill_all(self):

        # kill all current processes in list as well as child processes
        for pid in self.process_list:

            try:
                parent_process = psutil.Process(int(pid))
            except psutil._exceptions.NoSuchProcess:
                continue
            children = parent_process.children(recursive=True)

            for c in children:
                c.terminate()

            parent_process.terminate()

        self.process_list = []


def get_filename(parsed_url):
    filename = parsed_url.path.split('/')[-1]
    if parsed_url.query:
        filename += f'_{parsed_url.query}'
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    filename = filename.replace('%20', '_')

    if len(filename) >= 255:
        filename = str(uuid.uuid4())[:8] + ".pdf"

    return filename


def _ensure_unique(path):
    if os.path.isfile(path):
        short_uuid = str(uuid.uuid4())[:8]
        path = path.replace('.pdf', f'-{short_uuid}.pdf')
        return _ensure_unique(path)
    return path
