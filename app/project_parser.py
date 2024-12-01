import datetime
import json
import os
from collections import defaultdict
from datetime import timedelta

from chunking import split_code2docs
import requests
import zipfile


class ProjectParser:

    def __init__(self, request_id, target_file_url, exts=None):
        self._data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(self._data_dir, exist_ok=True)

        self._request_id = request_id
        self._target_file_url = target_file_url

        self._merged_files = None
        self._proj_dir = None
        self._max_unix = 0
        self.last_modified_dttm = None
        self._extensions = exts or self._get_default_extensions()


    def parse(self) -> str:
        self._download_and_unpack_data()
        self._merge_files()

        if os.path.exists(self._proj_dir):
            import shutil
            shutil.rmtree(self._proj_dir)

        return self._merged_files


    def _get_default_extensions(self):
        lang_file_path = os.path.join(self._data_dir, 'languages.json')
        with open(lang_file_path, 'r', encoding='utf-8') as file:
            languages = json.load(file)
        return languages


    def _download_and_unpack_data(self):
        response = requests.get(self._target_file_url)
        archive_path = os.path.join(self._data_dir, f"{self._request_id}.zip")
        self._proj_dir = os.path.join(self._data_dir, str(self._request_id))

        with open(archive_path, 'wb') as file:
            file.write(response.content)

        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(self._proj_dir)
        except (zipfile.BadZipFile, Exception) as e:
            os.remove(archive_path)
            raise Exception(f"Failed to extract archive {archive_path}: {e}")

        os.remove(archive_path)


    def _merge_files(self):
        self._merged_files = defaultdict(str)

        dirs_to_process = [self._proj_dir]

        while dirs_to_process:
            current_dir = dirs_to_process.pop(0)
            try:
                for root, _, files in os.walk(current_dir):
                    for file in files:
                        file_ext = os.path.splitext(file)[1].lower()
                        for language, exts in self._extensions.items():
                            if file_ext in exts:
                                self._process_file(root, file, language)
            except Exception as e:
                print(f"Ошибка при обходе директории {current_dir}: {e}")


        return self._merged_files


    def _process_file(self, root, file, language):
        file_path = os.path.join(root, file)
        rel_path = os.path.relpath(str(file_path), self._proj_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.check_last_modify_time(file_path)
                file_content = self._strip_empty_lines(f.read())
                self._merged_files[language] += f"{rel_path}\n```\n{file_content}\n```\n\n"
        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")


    def check_last_modify_time(self, file_path):
        cur_unix = os.path.getmtime(file_path)

        if cur_unix > self._max_unix:
            self._max_unix = cur_unix

            last_modified_time = datetime.datetime.fromtimestamp(cur_unix)
            timezone_offset = datetime.timedelta(hours=3)
            last_modified_time = last_modified_time.replace(tzinfo=datetime.timezone(timezone_offset))

            self.last_modified_dttm = last_modified_time.isoformat()


    def _union_all_project_files(self):
        result_str = ""
        for language, code in self._merged_files.items():
            result_str += f"<<<<{language} code:\n\n{code}\n>>>>end of {language} code\n"
        return result_str


    @staticmethod
    def _strip_empty_lines(s):
        lines = s.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        return '\n'.join(lines)


def split_proj_to_chunks(id: str, target_file_url: str):
    parser = ProjectParser(id, target_file_url)
    parsed_files_by_lang = parser.parse()
    chunks = []
    for lang, content in parsed_files_by_lang:
        chunks.append(split_code2docs(content, lang))
    return chunks, parser.last_modified_dttm
