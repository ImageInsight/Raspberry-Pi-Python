import pysftp
import paramiko
import socket
import os
import datetime
import time
import multiprocessing
from base64 import decodebytes
video_extension = "m4v"
current_video_directory = "/home/pi/Documents/Current_Video"
poll_wait = 30
file_wait = 30
host = "myhost.com"
username = "user"
password = "Password"
keydata = b"""ZzCQRHfPRfnaMX6a+X1EWd1YbDHKeQiVjONlCH3v63HFjNnlYofuhM2TA30RHV/jKwnvPrBz09hpaQU539ljNZEIbLyjbHwJi4JLAVX77QguB6/p9H4DKv"""
cpuserial = "0000000000000000"
try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
except:
    cpuserial = "ERROR000000000"
print(cpuserial)

hostname = socket.gethostname()

def loop_video():
    path = (current_video_directory + "/" + i)
    syntax = "omxplayer -b " + path + " --loop"
    os.system(syntax)

key = paramiko.RSAKey(data=decodebytes(keydata))
cnopts = pysftp.CnOpts()
cnopts.hostkeys.add('myhost.com', 'ssh-rsa', key)

file = os.listdir(current_video_directory)
i = file[0]
process = multiprocessing.Process(target=loop_video)
process.start()

while true:
    file = os.listdir(current_video_directory)
    current_video = file[0]
    
    srv = pysftp.Connection(host=host, username=username, password=password, cnopts = cnopts)

    srv.chdir("Pi")
    srv.chdir(hostname)
    data = srv.listdir()

    for i in data:
        if i.endswith(video_extension):
            if current_video == i:
                print ("current!")
            else:
                print (i)
                time.sleep(file_wait) 
                temp_file = (current_video_directory + "/" + "temp" + "." + video_extension)
                try:
                    srv.get(i, temp_file)
                    os.remove((current_video_directory + "/" + current_video))
                    os.rename((temp_file), (current_video_directory + "/" + i))
                    os.system("pkill omxplayer")
                    os.system("killall omxplayer")
                    process = multiprocessing.Process(target=loop_video) 
                    process.start()
                    logstamp = ("SUCCESS_" + cpuserial + "_" +(datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")))
                    os.system("touch " + logstamp)
                    srv.put(logstamp)
                    os.remove(logstamp)
                    print(logstamp)
                except:
                    print ("There was an error importing the new file")
                    os.remove(temp_file)
                    logstamp = ("ERROR_" + cpuserial + "_" + (datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")))
                    os.system("touch " + logstamp)
                    srv.put(logstamp)
                    os.remove(logstamp)
                    print(logstamp)
                break
    srv.close()    
    time.sleep(poll_wait)    