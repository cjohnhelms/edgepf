from sshtunnel import SSHTunnelForwarder
from fabric import Connection

def get_vms(host):
    vms = Connection(host).run('sudo virsh list --name', hide=True)
    return vms.stdout.strip()

def get_vip(host):
    vip = Connection(host).run("ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'")
    return vip.stdout.strip()

def start_tunnel(host, remote_port, local_port):
    server = SSHTunnelForwarder(
        host,
        remote_bind_address=('', remote_port),
        local_bind_address=('0.0.0.0', local_port)
    )
    server.start()
    while True:
        pass