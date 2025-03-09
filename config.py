# Hythonium Config
"""
This is a Pythonic Dictionary Config
The Sequences of the keys are not important, but the keys must be unique.
The values can be any type of Python objects, including nested dictionaries.
If a key is not found, the default value will be used.
If there is a extra key, it won't be used.
If the format is wrong, the programme will use an empty dict as a default value.
========================================================
Notices:
    1. Use "KEY": VALUE, to define a key-value pair.
    2. DO NOT use ';' instead of ':'
    3. Don't forget to plus ',' in the end of the line.
"""

config = {
    "homepage": "https://www.bing.com",
    "search_engine": "https://www.baidu.com/s?wd=",
    "new_tab": "https://www.baidu.com",
    "save_folder": "Downloads",
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "default_dnload_filename": "download_file",
}
