from tkinter import *
from tkinter import ttk
import ssh
import viewer

# root window and frame
root = Tk()
root.title("EdgePF")
frame = ttk.Frame(root, padding=10)
frame.grid()

# def textvariables
node = StringVar()
local_port = StringVar()
ports = {
        "RLSI": 443,
        "POS1": 5901,
        "POS2": 5904,
        "POS3": 5905,
        "POS4": 5906,
        "BOS": 5902,
        "Fuel": 5903,
        "OMS1": 5909
    }

# functions
def fetch():
    endpoints = ssh.get_vms(node.get()).split('\n')
    endpoints = ['RLSI'] + endpoints
    ttk.Label(frame, text="Select Endpoint: ", font=("Arial", 12)).grid(column=0, row=3)
    for i in range(len(endpoints)):
        print(endpoints[i])
        ttk.Button(frame, text=endpoints[i], command=lambda f=endpoints[i]: build(f)).grid(column=0, row=i+4)

def build(selected):
    port = ports[selected]
    vip = ssh.get_vip(node.get())
    ssh.start_tunnel(node.get(), vip, port, local_port.get())
    if selected == 'RLSI':
        viewer.open_browser(local_port.get())
    else:
        viewer.open_remote_viewer(local_port.get())

# define main window
ttk.Label(frame, text="Enter Hostname: ", font=("Arial", 12)).grid(column=0, row=0)
ttk.Entry(frame, textvariable=node).grid(column=1, row=0)
ttk.Label(frame, text="Enter Personal Port: ", font=("Arial", 12)).grid(column=0, row=1)
ttk.Entry(frame, textvariable=local_port).grid(column=1, row=1)
ttk.Button(frame, text="Fetch Data", command=fetch).grid(column=0, row=2)

# main
def main():
    root.mainloop()

main()