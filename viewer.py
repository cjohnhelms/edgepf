import webbrowser
import subprocess

def open_browser(local_port):
    url = 'http://localhost:' + str(local_port)
    webbrowser.open(url)

def open_remote_viewer(local_port):
    url = 'http://localhost:' + str(local_port)
    subprocess.Popen(['remote_viewer', url])