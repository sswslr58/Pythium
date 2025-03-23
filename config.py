# coding=utf-8
# Hythonium Config
"""

This is a Pythonic Dictionary Config.
Hythonium will load it as a dictionary and use it in the browser.

Just put this file in the SAME directory as hynium.py | hynium.exe
DO REMEMBER: The filename MUST BE "config.py" !!!
The encoding MUST BE utf-8.

========================================================

The sequence of the keys is not important, but the keys must be unique.
The values can be any type of Python objects, including nested dictionaries.
If a key is not found, the default value will be used.
If there is an extra key, it won't be used.
If the format is wrong, the program will use an empty dictionary as the default value.

========================================================

Notices:
    1. Use 'KEY': VALUE to define a key-value pair.
    2. DO NOT use ';' instead of ':'.
    3. Don't forget to add ',' at the end of the line.

========================================================

Keys are:
    homepage: (str)<URL> -- Set the homepage of Hythonium. eg: "https://www.baidu.com"
    search_engine: (str)<URL> -- Set the search engine of Hythonium. eg: "https://www.baidu.com/s?wd="
    new_tab: (str)<URL> -- Set the new tab when clicking '+' button. eg: "https://www.baidu.com"
    download_folder: (str)<PATH> -- Set the downloading path. eg: "Downloads" | "./Downloads" | "/home/usrname/Downloads" | "C:\\Downloads"
    User_Agent: (str) -- Set User-Agent value. eg: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

========================================================

And you should execute hynium.py or hynium.exe to start Hythonium. NOT THIS FILE!!!

========================================================

For more information, see README.md => Click Here: https://github.com/sswslr58/Hythonium

"""

if __name__ == "__main__":
    print("Execute hynium.py or hynium.exe to start Hythonium next time.")
    print("Do NOT execute this file again !")

config = {
    "homepage": "https://www.bing.com",
    "search_engine": "https://www.bing.com/s?q=",
    "new_tab": "https://www.bing.com",
    "download_folder": "Downloads",
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
}






















