import shutil
import magic
from pathlib import Path

class FileMover:
    def __init__(self):
        self.mime = magic.Magic(mime=True)
        self.target_dir = Path(f'{Path.home()}/Downloads')
        self.temp_dir = self.find_latest_temp_dir(Path(f'{Path.home()}/AppData/Local/Temp'))
        print(f'temp_dir: {self.temp_dir}')

    def move_files(self):
        for filename in self.temp_dir.iterdir():
            source = self.temp_dir / filename
            if source.is_file():
                # Determine the MIME type of the file
                mime_type = self.mime.from_file(str(source))
                # Suggest the file extension based on the MIME type
                extension = self.suggest_extension(mime_type)
                destination = self.target_dir / (filename.stem + extension)
                shutil.move(source, destination)
                print(f'Moved: {filename} to {destination}')
    
    def suggest_extension(self, mime_type):
        mime_to_extension = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'application/zip': '.zip',
            'application/pdf': '.pdf',
            'text/plain': '.txt',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
            'application/json': '.json',
            'application/xml': '.xml',
            'application/octet-stream': '.bin',
            'video/mp4': '.mp4',
            'audio/mpeg': '.mp3',
            'text/csv': '.csv',
            'text/html': '.html',
            'application/x-tar': '.tar',
            'application/gzip': '.gz',
            'application/x-rar-compressed': '.rar',
            'application/x-7z-compressed': '.7z',
        }
        return mime_to_extension.get(mime_type, '')
    
    def find_latest_temp_dir(self, base_temp_dir: Path):
        temp_dirs = [d for d in base_temp_dir.iterdir() if d.is_dir() and d.name.startswith('playwright-artifacts-')]
        latest_temp_dir = max(temp_dirs, key=lambda d: d.stat().st_ctime)
        return latest_temp_dir

