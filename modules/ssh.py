import subprocess

def execute(host, cmd=''):
    cust = host[:3]
    result = subprocess.run(['ssh', '-q', '-A', '-J', f'jump2,login.{cust}', host, cmd], capture_output=True, text=True)
    return result

def start_tunnel(host, vip, remote_port, local_port):
    cust = host[:3]
    subprocess.Popen(['ssh', '-AL', f'{local_port}:{vip}:{remote_port}', '-J', f'jump2,login.{cust}', host], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)