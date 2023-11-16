"""
Larpa Fruit Printing Routines

First-time setup:
  > cd <repo>
  > python3 -m venv .venv
  > source .venv/bin/activate
  > pip install -r requirements.txt 

Activating the Python virtual environment:
  > cd <repo>
  > source .venv/bin/activate

  This is required each time you need to run this script. The virtual
  environment is activated when your console is prefixed with `(.venv)`.

To start the OSC server:
  > python larpa.py start

  Optionally, you can override the server configuration using the `--host` and
  `--port` arguments. Use Ctrl+C to kill the server.

How to test the OSC server:
  Open a new console and activate the virtual environment. Run:

  > python larpa.py echo "Hello, World!!"

  On success, you'll see "Hello, World!!" printed in the SERVER console. This
  confirms that the server can receive OSC client requests.

How to test a scan via the CLI:
  > python larpa.py scan

How to test a scan-and-print via the CLI:
  > python larpa.py scan_and_print

Once all of the above is tested and confirmed operational, TouchOSC can be
configured to communicate with the OSC server:
  Server: <Raspberry Pi IP Address>
  Port: 13000
  Available Endpoints:
    /echo (for testing)
    /scan
    /scan_and_print
"""
import argparse
import subprocess
from threading import Lock

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

DEFAULT_OSC_SERVER_HOST = "0.0.0.0"
DEFAULT_OSC_SERVER_PORT = 13000
DEFAULT_OSC_CLIENT_HOST = "127.0.0.1"

# The scanner to target. Use `scanimage -L` to list all available devices.
SCANNER_DEVICE_NAME = "pixma:04A918AA_2067EE"

# The file that the scanner will write to.
OUT_FILE = "out.jpeg"

# Global lock that ensures that we only attempt to scan/print once-at-a-time.
MUTEX = Lock()


# ============================================================= Device Commands

def execute_scan():
  """ Executes a scan command. """
  print( "> Scanning..." )
  subprocess.run( "scanimage --device-name={} --format=jpeg --calibrate=Always > {}".format( SCANNER_DEVICE_NAME, OUT_FILE ), shell=True )

def execute_print():
  """ Executes a print command. Be sure to set a printer as the default in
  system settings """
  print( "> Printing..." )
  subprocess.run( "lp {}".format( OUT_FILE ), shell=True )


# ====================================================== OSC Callback Functions

def echo_callback( _address, msg ):
  """ Prints the contents of the OSC message to the console. """
  print( "> {}".format( msg ) )

def scan_callback( _address, _msg ):
  """ Prints the contents of the OSC message to the console. """
  if MUTEX.locked():
    print( "> Scan ignored, a process lock has already been acquired..." )
  else:
    with MUTEX:
      execute_scan()

def scan_and_print_callback( _address, _msg ):
  if MUTEX.locked():
    print( "> Scan and print ignored, a process lock has already been acquired..." )
  else:
    with MUTEX:
      execute_scan()
      execute_print()


# ================================================================ CLI Handlers

def start_handler( args ):
  """ CLI handler for the start subparser. Starts an OSC server with the
  defined routes."""
  dispatcher = Dispatcher()
  dispatcher.map( "/echo", echo_callback )
  dispatcher.map( "/scan", scan_callback )
  dispatcher.map( "/scan_and_print", scan_and_print_callback )

  server = ThreadingOSCUDPServer( ( args.host, args.port ), dispatcher )
  print( "Serving on {}...".format( server.server_address ) )
  server.serve_forever()

def echo_handler( args ):
  """ CLI handler for the echo subparser. Emits a message to the /echo 
  receiver. """
  client = SimpleUDPClient( args.host, args.port )
  client.send_message( "/echo", args.msg )

def scan_handler( args ):
  """ CLI handler for the scan subparser. Will execute a scanning action. """
  execute_scan()

def scan_and_print_handler( args ):
  """ CLI handler for the scan_and_print subparser. Will execute a scanning and
  print action. """
  execute_scan()
  execute_print()


# ========================================================================= CLI

if __name__ == "__main__":
  parser = argparse.ArgumentParser( description="Larpa Fruit Printing Routines" )
  subparsers = parser.add_subparsers( dest="action", help="Available commands:" )
  subparsers.required = True

  # Start
  start_parser = subparsers.add_parser( "start",
    help="Starts the OSC server." )
  start_parser.add_argument( "--host", default=DEFAULT_OSC_SERVER_HOST,
    help="The host address that the OSC server will listen on." )
  start_parser.add_argument( "--port", type=int, default=DEFAULT_OSC_SERVER_PORT, 
    help="The port that the OSC server will listen on." )
  start_parser.set_defaults( func=start_handler )

  # Echo
  echo_parser = subparsers.add_parser( "echo",
    help="For testing. Will emit an echo OSC call to the OSC server." )
  echo_parser.add_argument( "--host", default=DEFAULT_OSC_CLIENT_HOST,
    help="The host address that the OSC server will listen on." )
  echo_parser.add_argument( "--port", type=int, default=DEFAULT_OSC_SERVER_PORT, 
    help="The port that the OSC server will listen on." )
  echo_parser.add_argument( "msg", default="Hello, world!",
    help="The message to echo." )
  echo_parser.set_defaults( func=echo_handler )

  # Scan
  scan_parser = subparsers.add_parser( "scan",
    help="For testing. Will execute a scan-only action." )
  scan_parser.set_defaults( func=scan_handler )

  # Scan & Print
  scan_and_print_parser = subparsers.add_parser( "scan_and_print",
    help="For testing. Will execute a scan-and-print action." )
  scan_and_print_parser.set_defaults( func=scan_and_print_handler )

  args = parser.parse_args()
  args.func( args )