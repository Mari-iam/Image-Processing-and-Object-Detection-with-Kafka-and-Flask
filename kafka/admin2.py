#This script to make sure that they run at the same time 

import subprocess

subprocess.Popen(['python', 'producer.py'])
subprocess.Popen(['python', 'consumer.py'])
subprocess.Popen(['python', 'bw_consumer.py'])


