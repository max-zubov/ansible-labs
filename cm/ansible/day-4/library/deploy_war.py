#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

DOCUMENTATION = '''
---
module: deploy_war
version_added: historical
short_description: Deploy WAR file to Tomcat
options:
    url:
        version_added: "1.0"
        description:
            - "Tomcat URL"
        required: true
        default: 'None'
    username:
        version_added: "1.0"
        description:
            - "Username for authentication on Tomcat"
        required: true
        default: None
    password:
        version_added: "1.0"
        description:
            - "Password for authentication on Tomcat"
        required: true
        default: None
    context:
        version_added: "1.0"
        description:
            - "Deployable Context Target"
        required: false
        default: None
    war:
        version_added: "1.0"
        description:
            - "Path to artifact to be deployed"
        required: true
        default: None
requirments:
    - pip install requests
description:
    - This module can be used for Tomcat remote deployment
author:
    - "Siarhei Beliakou"
    - "Vitali Ulantsau"
    - make change "Maxim Zubov"
'''

EXAMPLES = """
# Standalone mode launch.
ansible localhost -c local -m deploy_war -a "url=http://192.168.56.100:8080 username=admin password=secret context=/helloworld src=/tmp/hello.war"
# Running module as task inside a playbook. 
# Ensure that vm(s) specified in provided Vagrantfile is running
- name: create host 
  deploy_war:
    url: http://192.168.56.100:8080
    username: admin
    password: secret
    context: /helloworld
    src: /tmp/hello.war
"""

from ansible.module_utils.basic import *
import subprocess
import requests
import os
import datetime

def main():

  module = AnsibleModule(
    argument_spec = dict(
      url       = dict(required=True, type='str'),
      username  = dict(required=True, type='str'),
      password  = dict(required=True, type='str'),
      context   = dict(required=False, type='str'),
      war       = dict(required=True, type='str')
    )
  )

  url = module.params["url"]
  username = module.params["username"]
  password = module.params["password"]
  war = os.path.abspath(module.params["war"])
  if module.params["context"]:
    context = module.params["context"]
  else: 
    context="/" + war.split('/')[-1]

  result = dict(
      msg='',
      changed=False,
      application_url="{}{}".format(url,context),
      war_path="{}".format(war),
      info=''
  )

  if module.check_mode:
    return result

  if os.path.isfile(war) == False:
    result['msg'] = 'FAIL - File not found - {}'.format(war)
    module.fail_json(**result)

  files = {'file': (os.path.basename(war), open(war, 'rb'))}
  deploy_url = "{}/manager/text/deploy?path={}&update=true".format(url, context)

  r = requests.put(url=deploy_url, auth=(username, password), files=files)
  
#  with open('./deploy-info.txt', 'a') as info_file:
#    info_file.write('Deploy Time: ' + datetime.datetime.today().strftime('%Y/%m/%d-%H:%M') \
#      + '  Deploy User: ' + username + '\n')
 
  if r.status_code == 200:
    result['msg'] = "OK - Deployed application at context path [{}]".format(context)
    result['changed'] = True
    result['info'] =  'Deploy Time: ' + datetime.datetime.today().strftime('%Y/%m/%d-%H:%M') \
                   + '  Deploy User: ' + username + '\n'
  else:
    result['msg'] = 'FAIL - Deployment Failed at context path [{}]'.format(context)
    module.fail_json(**result)
    

  module.exit_json(**result)
  
# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()