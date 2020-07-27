#!/usr/bin/python
# -*- coding: utf-8 -*-
#License: Public Domain
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['labwork']
                   }
DOCUMENTATION = r'''
---
module: win_vagr
short_description: Scripted by PowerShell. Manages Vagrant on Windows host with VirtualBox installed, by WinRM connection.

description:
  - Running virtual machine and return retrieved configuration values 
  - Setting virtual machine to shutdown mode, even it not been created
  - Destroying virtual machine
options:
  path:
    description:
      - Path to vagrantfile in windows style on uppercase
    default: None
  vmname:
    description:
      - The name virtual machine in Vagrant
    default: default
  state:
    description:
      - One from started, stopped, destroyed
    default: None
author:
- Max
'''
 
EXAMPLES = r'''
# Example Ansible adhoc
ansible win -i inventory -M ./library -m win_vagr -a "path=D:\VAGRANT vmname=vm state=started" 
'''
 
RETURN = '''
    description: Output of state and virtual machine parameters in JSON format
    returned: 
        "changed": result flag
        "ipaddr": ip address guest network interface
        "iploc": ip address vagrant host interface
        "port": port vagrant host
        "keypath": path to private_key in linux
        "os_name": guest os name
        "ramsize": ram size
        "state": guest machine state
        "userlogin": guest machine login user name 
    type: JSON string
'''