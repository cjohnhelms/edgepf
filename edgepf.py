from tkinter import *
from tkinter import ttk
from modules import ssh
from modules import viewer

# root window and frame
root = Tk()
root.title("EdgePF")
frame = ttk.Frame(root, padding=10)
frame.grid()

# def textvariables
node = StringVar()
local_port = StringVar()

# functions
def error_window(err):
    err_window = Toplevel()
    err_window.title('Hostname Error')
    err_frame = ttk.Frame(err_window, padding=10)
    err_frame.pack()
    ttk.Label(err_frame, text=err).pack()

def fetch():
    if not node.get().isalnum():
        error_window('Invalid characters in hostname')
    else:
        result = ssh.execute(node.get(), 'sudo virsh list --name')
        vip_output = ssh.execute(node.get(), "ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'")
        if 'Could not resolve hostname' in result.stderr or result.returncode == 255:
            error_window('Hostname resolution error. Please verify hostname and check VPN status.')
        elif vip_output.stdout == '' and vip_output.returncode == 0:
            error_window('Could not find VIP. Please confirm destination host is primary.')
        else:
            endpoints = sorted(result.stdout.strip().split('\n'))
            endpoints = ['RLSI'] + endpoints
            ttk.Label(frame, text="Select Endpoint: ", font=("Terminal", 12)).grid(column=0, row=3)
            for i in range(len(endpoints)):
                ttk.Button(frame, text=endpoints[i], command=lambda f=endpoints[i]: build(f, vip_output.stdout.strip())).grid(column=0, row=i+4)

def build(selected, vip):
    if selected == 'RLSI':
        viewer.open_browser(local_port.get())
        ssh.start_tunnel(node.get(), vip, '443', local_port.get())
    else:
        remote_port = ssh.execute(node.get(), selected, f'sudo virsh dumpxml {selected} | grep spice | grep port | cut -d "\'" -f4').stdout.strip()
        ssh.start_tunnel(node.get(), vip, remote_port, local_port.get())
        viewer.open_remote_viewer(local_port.get())

# define main window
ttk.Label(frame, text="Enter Hostname: ", font=("Terminal", 12)).grid(column=0, row=0)
ttk.Entry(frame, textvariable=node).grid(column=1, row=0)
ttk.Label(frame, text="Enter Personal Port: ", font=("Terminal", 12)).grid(column=0, row=1)
ttk.Entry(frame, textvariable=local_port).grid(column=1, row=1)
ttk.Button(frame, text="Fetch Data", command=fetch).grid(column=0, row=2)

# main
def main():
    root.mainloop()

main()
