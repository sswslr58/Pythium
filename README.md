# Hythonium
A web browser based on Python PyQt5.
# How to conifg
1.Put 'config.py' and 'hynium.py' or 'hynium.exe' in the same directory.
  If there is NO config.py, You can make one by yourself.
2.Edit 'config.py'
  Edit it like Python. Make the content:
    config = {
      "Key1": Value1,
      "Key2": Value2,
    }
  'Keys' are all str objects. 
  Keys are:
    homepage: (str)<URL> -- Set the homepage of Hythonium. eg:"https://www.baidu.com"
    search_engine: (str)<URL> -- Set the search engine of Hythonium. eg:"https://www.baidu.com/s?wd="
    new_tab: (str)<URL> -- Set the new tab when clicking '+' button. eg:"https://www.baidu.com"
    save_folder: (str)<PATH> -- Set the downloading path. eg:"Downloads" | "./Downloads" | "/home/usrname/Downloads" | "C:\\Downloads"
    User-Agent: (str) -- Set UA value. eg:"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    default_dnload_filename: (str) -- Set default downloading file name eg:"download_file"
# How to build your own one
In terminal:
pip install pyinstaller # If you use conda, you can change this command
pyinstaller -F -w hynium.py # -F means one file mode. -w means without terminal window when running. You can change.
dist/hynium.exe # Enjoy !
