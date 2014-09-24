#!/usr/bin/python 
import paramiko
#psftp so1@209.235.210.84 -pw so1@northgrum1
host = "209.235.210.84"                    #hard-coded
port = 22
transport = paramiko.Transport((host, port))

password = "so1@northgrum1"                #hard-coded
username = "so1"                #hard-coded
transport.connect(username = username, password = password)

sftp = paramiko.SFTPClient.from_transport(transport)

import sys
sftp.chdir('Outgoing\TestListings')

for x in sftp.listdir():
    if x.endswith('.csv'):
       sys.exit(0)
    else:
       sys.exit(1)
 
