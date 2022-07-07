#! env python3 

import yaml 
import pathlib 
import subprocess 

secrets = pathlib.Path('./secrets')
if secrets.exists():
    print("Refusing to overwrite existing secrets.")
    quit(-1)

secrets.mkdir()
subprocess.run("ssh-keygen -t rsa -f ca_key -N ''", shell=True, cwd=secrets)
with open(secrets / "ca_key") as fh:
    priv = fh.read()
with open(secrets / "ca_key.pub") as fh:
    pub = fh.read()

ssh_config = {
    "ssh": {
        'ca_key_pub': pub,
        'ca_key': priv,
    }
}

with open(secrets / 'ssh-keys.yaml', 'w') as fh:
    fh.write(yaml.dump(ssh_config, default_style='|'))
