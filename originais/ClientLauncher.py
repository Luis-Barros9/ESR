import sys
from tkinter import Tk
from Client import Client

PORT = 5000  # Define a single, fixed port for all oNode instances
BOOTSTRAPPER_IP = '10.0.34.2'  # IP of the bootstrapper


if __name__ == "__main__":
	try:
		bootstraper = sys.argv[1]
	except:
		print("[Usage: ClientLauncher.py]\n")	
	
	# Send a message to bootstrapper to get server IP
	

	root = Tk()
	
	# Create a new client
	app = Client(root)
	app.master.title("RTPClient")	
	root.mainloop()
	