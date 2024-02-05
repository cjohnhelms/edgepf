import webbrowser
import subprocess

def open_browser(local_port):
    url = 'https://localhost:' + str(local_port)
    webbrowser.open(url)

def open_remote_viewer(local_port):
    url = 'spice://localhost:' + str(local_port)
    subprocess.Popen(['remote-viewer', '--auto-resize=never', url], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
