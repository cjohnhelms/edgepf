import subprocess

def get_vms(host):
    result = subprocess.run(['ssh', '-q', '-A', '-J', 'jump2,login.cgs', host, 'sudo virsh list --name'], capture_output=True, text=True)
    return result

def get_vip(host):
    result = subprocess.run(['ssh','-q', '-A', '-J', 'jump2,login.cgs', host, "ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'"], capture_output=True, text=True)
    return result.stdout.strip()

def get_remote_port(host, vm):
    result = subprocess.run(['ssh', '-q', '-A', '-J', 'jump2,login.cgs', host, f'sudo virsh dumpxml {vm} | grep spice | grep port | cut -d "\'" -f4'], capture_output=True, text=True)
    return result.stdout.strip()

def start_tunnel(host, vip, remote_port, local_port):
    subprocess.Popen(['ssh', '-AL', f'{local_port}:{vip}:{remote_port}', '-J', 'jump2,login.cgs', host])