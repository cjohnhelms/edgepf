import subprocess

def execute(host, cmd=''):
    cust = host[:3]
    result = subprocess.run(['ssh', '-q', '-A', '-J', f'jump2,login.{cust}', host, cmd], capture_output=True, text=True)
    return result

def get_vms(host):
    cust = host[:3]
    result = subprocess.run(['ssh', '-q', '-A', '-J', f'jump2,login.{cust}', host, 'sudo virsh list --name'], capture_output=True, text=True)
    return result

def get_vip(host):
    cust = host[:3]
    result = subprocess.run(['ssh','-q', '-A', '-J', f'jump2,login.{cust}', host, "ip a show br0 | grep secondary | awk '{ print $2 }' | awk -F '/' '{ print $1 }'"], capture_output=True, text=True)
    return result

def get_remote_port(host, vm):
    cust = host[:3]
    result = subprocess.run(['ssh', '-q', '-A', '-J', f'jump2,login.{cust}', host, f'sudo virsh dumpxml {vm} | grep spice | grep port | cut -d "\'" -f4'], capture_output=True, text=True)
    return result

def start_tunnel(host, vip, remote_port, local_port):
    cust = host[:3]
    subprocess.Popen(['ssh', '-AL', f'{local_port}:{vip}:{remote_port}', '-J', f'jump2,login.{cust}', host], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)