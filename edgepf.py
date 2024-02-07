import tkinter as tk
from tkinter import ttk
import xml.etree.ElementTree as ET
from modules import ssh
from modules import viewer

class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("EdgePF")

        self.container = tk.Frame(self, height=400, width=600)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        frame = MainPage(self.container, self)
        self.frames[MainPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)

    def error_window(self, err):
        err_window = tk.Toplevel()
        err_window.title('Error')
        err_frame = ttk.Frame(err_window, padding=10)
        err_frame.pack()
        ttk.Label(err_frame, text=err).pack()
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid(padx=10, pady=10)
        self.node = tk.StringVar()
        self.local_port = tk.StringVar()
        tk.Label(self, text="Enter Hostname: ", font=("Terminal", 12), padx=10).grid(column=0, row=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.node).grid(column=1, row=0)
        tk.Label(self, text="Enter Personal Port: ", font=("Terminal", 12), padx=10).grid(column=0, row=1, sticky=tk.W)
        ttk.Entry(self, textvariable=self.local_port).grid(column=1, row=1)
        ttk.Button(self, text="Fetch Data", command=lambda: self.fetch(self.node.get(), controller)).grid(column=0, row=2)

    def fetch(self, node, controller):
        if not node.isalnum():
            controller.error_window('Invalid characters in hostname')
        else:
            ssh_test = ssh.execute(self.node.get(), 'sudo pcs status | grep "Current DC"')
            if ssh_test.returncode == 255:
                controller.error_window('Hostname resolution error. Please verify hostname and check VPN status.')
            elif self.node.get() not in ssh_test.stdout.strip():
                controller.error_window('The selected node is not primary. Please try other node in cluster.')
            else:
                xml = ssh.execute(node, 'sudo pcs status xml').stdout
                cluster = Cluster(xml, self.node.get())
                frame = DataPage(controller.container, cluster, self.node.get(), self.local_port.get())
                controller.frames[DataPage] = frame
                controller.show_frame(DataPage)

class DataPage(tk.Frame):
    def __init__(self, parent, cluster, node, local_port):
        tk.Frame.__init__(self, parent)
        self.grid(padx=10, pady=10)
        self.node = node
        self.local_port = local_port
        tk.Label(self, text="Cluster Status:", font=("Terminal", 16), pady=10).grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self, text=f"Node: {cluster.red0['name']}", padding=1).grid(column=0, row=1, sticky=tk.W)
        ttk.Label(self, text=f"Online: {cluster.red0['online']}", padding=1).grid(column=0, row=2, sticky=tk.W)
        ttk.Label(self, text=f"Standby: {cluster.red0['standby']}", padding=1).grid(column=0, row=3, sticky=tk.W)
        ttk.Label(self, text=f"Maintenance: {cluster.red0['maintenance']}", padding=1).grid(column=0, row=4, sticky=tk.W)
        ttk.Label(self, text=f"Unclean: {cluster.red0['unclean']}", padding=1).grid(column=0, row=5, sticky=tk.W)
        ttk.Label(self, text=f"Resources running: {cluster.red0['resources_running']}", padding=1).grid(column=0, row=6, sticky=tk.W)

        ttk.Label(self, text='       ', padding=1).grid(column=1, row=1, sticky=tk.W)

        ttk.Label(self, text=f"Node: {cluster.red1['name']}", padding=1).grid(column=2, row=1, sticky=tk.W)
        ttk.Label(self, text=f"Online: {cluster.red1['online']}", padding=1).grid(column=2, row=2, sticky=tk.W)
        ttk.Label(self, text=f"Standby: {cluster.red1['standby']}", padding=1).grid(column=2, row=3, sticky=tk.W)
        ttk.Label(self, text=f"Maintenance: {cluster.red1['maintenance']}", padding=1).grid(column=2, row=4, sticky=tk.W)
        ttk.Label(self, text=f"Unclean: {cluster.red1['unclean']}", padding=1).grid(column=2, row=5, sticky=tk.W)
        ttk.Label(self, text=f"Resources running: {cluster.red1['resources_running']}", padding=2).grid(column=2, row=6, sticky=tk.W)

        Journal(cluster)

        self.show_endpoints(cluster)

    def show_endpoints(self, cluster):
        tk.Label(self, text="Select Endpoint: ", font=("Terminal", 16), pady=10).grid(column=0, row=7, sticky=tk.W)
        for i in range(len(cluster.endpoints)):
            ttk.Button(self, text=cluster.endpoints[i], command=lambda f=cluster.endpoints[i]: self.build(f, cluster)).grid(column=0, row=i+8, sticky=tk.W)

    def build(self, selected, cluster):
        if selected == 'RLSI':
            ssh.start_tunnel(self.node, cluster.vip, '443', self.local_port)
            viewer.open_browser(self.local_port)
        else:
            self.remote_port = ssh.execute(self.node, f'sudo virsh dumpxml {selected} | grep spice | grep port | cut -d "\'" -f4').stdout.strip()
            ssh.start_tunnel(self.node, cluster.vip, self.remote_port, self.local_port)
            viewer.open_remote_viewer(self.local_port)

class Journal(tk.Toplevel):
    def __init__(self, cluster):
        tk.Toplevel.__init__(self)
        self.wm_title("Cluster Journal")

        self.container = tk.Frame(self, height=400, width=600)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        notebook = ttk.Notebook(self.container)
        notebook.pack(pady=10, expand=True)
        frames = {}
        for tab in ['DRBD', 'DU', 'CLUSTER', 'STONITH']:
            frames[tab] = ttk.Frame(notebook, width=400, height=280)
            frames[tab].pack(fill='both', expand=True)
            notebook.add(frames[tab], text=tab)
            ttk.Label(frames[tab], text=getattr(cluster, tab)).pack(anchor=tk.W)


class Cluster():
    def __init__(self, xml, node):
        xmlroot = ET.fromstring(xml)
        self.red0 = xmlroot[1][0].attrib
        self.red1 = xmlroot[1][1].attrib
        self.vip = ssh.execute(node, "ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'").stdout.strip()
        self.endpoints = sorted(ssh.execute(node, 'sudo virsh list --name').stdout.strip().split('\n'))
        self.endpoints = ['RLSI'] + self.endpoints
        self.DRBD = ssh.execute(node, 'sudo drbd-overview').stdout.strip()
        self.DU = ssh.execute(node, 'df -h').stdout.strip()
        self.CLUSTER = ssh.execute(node, 'sudo rvc cluster status').stdout.strip()
        self.STONITH = ssh.execute(node, 'sudo pcs stonith history').stdout.strip()

# main
def main():
    root = Window()
    root.mainloop()

if __name__ == "__main__":
    main()
