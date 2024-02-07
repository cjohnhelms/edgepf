import subprocess
import os

def mkconfig(host):
    cust = host[:3]
    tmp = '.ssh/tmp/'
    file_path = '.ssh/tmp/config'
    file_contents = f"""
    Host *
      ControlMaster auto
      ControlPersist 8h
      ServerAliveInterval 100
      ControlPath ~/.ssh/control/%h-%p-%r
      StrictHostKeyChecking no
      ForwardAgent yes
      IdentityFile ~/.ssh/id_rsa
      AddKeysToAgent yes
      PubkeyAcceptedKeyTypes +ssh-rsa
      HostKeyAlgorithms +ssh-dss,ssh-rsa
    Host login*
      ProxyJump jump2
    Host {cust}*
      ProxyJump login.{cust}
    """
    os.makedirs(tmp)
    f = open(file_path, 'a')
    f.write(file_contents)

def rmconfig():
    subprocess.run(['rm', '-rf', '.ssh'])

def execute(host, cmd=''):
    mkconfig(host)
    result = subprocess.run(['ssh', '-F', '.ssh/tmp/config', '-o', 'ConnectTimeout=60', '-q', host, cmd], capture_output=True, text=True)
    rmconfig()
    return result

def start_tunnel(host, vip, remote_port, local_port):
    mkconfig(host)
    subprocess.Popen(['ssh', '-F', '.ssh/tmp/config', '-AL', f'{local_port}:{vip}:{remote_port}', '-o', 'ConnectTimeout=60', host], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    rmconfig()