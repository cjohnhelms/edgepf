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
            result = ssh.execute(node, 'sudo pcs status xml')
            if result.returncode == 255:
                controller.error_window('Hostname resolution error. Please verify hostname and check VPN status.')
            else:
                xml = result.stdout
                cluster = Cluster(xml)
                frame = DataPage(controller.container, controller, cluster, self.node.get(), self.local_port.get())
                controller.frames[DataPage] = frame
                controller.show_frame(DataPage)

class DataPage(tk.Frame):
    def __init__(self, parent, controller, cluster, node, local_port):
        tk.Frame.__init__(self, parent)
        self.grid(padx=10, pady=10)
        self.node = node
        self.local_port = local_port
        tk.Label(self, text=f'Node: {cluster.red0['name']}', font=("Terminal", 16), pady=3).grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self, text=f'Online: {cluster.red0['online']}', padding=1).grid(column=0, row=1, sticky=tk.W)
        ttk.Label(self, text=f'Standby: {cluster.red0['standby']}', padding=1).grid(column=0, row=2, sticky=tk.W)
        ttk.Label(self, text=f'Maintenance: {cluster.red0['maintenance']}', padding=1).grid(column=0, row=3, sticky=tk.W)
        ttk.Label(self, text=f'Unclean: {cluster.red0['unclean']}', padding=1).grid(column=0, row=4, sticky=tk.W)
        ttk.Label(self, text=f'Resources running: {cluster.red0['resources_running']}', padding=1).grid(column=0, row=5, sticky=tk.W)

        tk.Label(self, text=f'Node: {cluster.red1['name']}', font=("Terminal", 16), pady=3).grid(column=1, row=0, sticky=tk.W)
        ttk.Label(self, text=f'Online: {cluster.red1['online']}', padding=1).grid(column=1, row=1, sticky=tk.W)
        ttk.Label(self, text=f'Standby: {cluster.red1['standby']}', padding=1).grid(column=1, row=2, sticky=tk.W)
        ttk.Label(self, text=f'Maintenance: {cluster.red1['maintenance']}', padding=1).grid(column=1, row=3, sticky=tk.W)
        ttk.Label(self, text=f'Unclean: {cluster.red1['unclean']}', padding=1).grid(column=1, row=4, sticky=tk.W)
        ttk.Label(self, text=f'Resources running: {cluster.red1['resources_running']}', padding=1).grid(column=1, row=5, sticky=tk.W)

        self.show_endpoints(controller)

    def show_endpoints(self, controller):
        if not self.node.isalnum():
            controller.error_window('Invalid characters in hostname')
        else:
            self.result = ssh.execute(self.node, 'sudo virsh list --name')
            self.vip_output = ssh.execute(self.node, "ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'")
            self.vip = self.vip_output.stdout.strip()
            if 'Could not resolve hostname' in self.result.stderr or self.result.returncode == 255:
                controller.error_window('Hostname resolution error. Please verify hostname and check VPN status.')
            elif self.vip_output.stdout == '' and self.vip_output.returncode == 0:
                controller.error_window('Could not find VIP. Please confirm destination host is primary.')
            else:
                self.endpoints = sorted(self.result.stdout.strip().split('\n'))
                self.endpoints = ['RLSI'] + self.endpoints
                tk.Label(self, text="Select Endpoint: ", font=("Terminal", 16), pady=10).grid(column=0, row=7, sticky=tk.W)
                for i in range(len(self.endpoints)):
                    ttk.Button(self, text=self.endpoints[i], command=lambda f=self.endpoints[i]: self.build(f)).grid(column=0, row=i+8, sticky=tk.W)

    def build(self, selected):
        if selected == 'RLSI':
            viewer.open_browser(self.local_port)
            ssh.start_tunnel(self.node, self.vip, '443', self.local_port)
        else:
            self.remote_port = ssh.execute(self.node, f'sudo virsh dumpxml {selected} | grep spice | grep port | cut -d "\'" -f4').stdout.strip()
            ssh.start_tunnel(self.node, self.vip, self.remote_port, self.local_port)
            viewer.open_remote_viewer(self.local_port)

class Cluster():
    def __init__(self, xml):
        root = ET.fromstring(xml)
        self.red0 = root[1][0].attrib
        self.red1 = root[1][1].attrib

# main
def main():
    root = Window()
    root.mainloop()

if __name__ == "__main__":
    main()
