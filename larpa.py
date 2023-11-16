"""

"""
import argparse
import subprocess

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

DEVICE_NAME = "pixma:04A918AA_2067EE"
OUT = "out.jpeg"
SCAN_CMD = "scanimage --device-name={} --format=jpeg --calibrate=Always > {}".format( DEVICE_NAME, OUT )
PRINT_CMD = "lp {}".format( OUT )

DEFAULT_OSC_SERVER_HOST = "0.0.0.0"
DEFAULT_OSC_SERVER_PORT = 13000
DEFAULT_OSC_CLIENT_HOST = "127.0.0.1"

def scanner_magic( args ):
  print( "Scanning..." )
  subprocess.run( SCAN_CMD, shell=True )

  if args.print:
    print( "Printing..." )
    subprocess.run( PRINT_CMD, shell=True )


# ====================================================== OSC Callback Functions

def echo_callback( _address, body ):
  """ Prints the contents of the OSC message to the console. """
  print( "> {}".format( body ) )

# ========================================================================= CLI

def start_handler( args ):
  """ CLI handler for the start subparser. """
  dispatcher = Dispatcher()
  dispatcher.map( "/echo", echo_callback )

  server = ThreadingOSCUDPServer( ( args.host, args.port ), dispatcher )
  print( "Serving on {}...".format( server.server_address ) )
  server.serve_forever()

def echo_handler( args ):
  """ CLI handler for the echo subparser. """
  client = SimpleUDPClient( args.host, args.port )
  client.send_message( "/echo", args.body )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if __name__ == "__main__":
  parser = argparse.ArgumentParser( description="Larpa Scanner x4000" )
  subparsers = parser.add_subparsers( dest="action", help="Available commands:" )
  subparsers.required = True

  """
  parser.add_argument( "--print", action="store_true", default=False,
    help="Will include the print command." )
  parser.add_argument( "--host", default="0.0.0.0",
    help="The ip to listen on" )
  parser.add_argument( "--port", type=int, default=13000, 
    help="The port to listen on." )
  parser.add_argument( "--start-server" )
  """

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
    help="Emits an echo OSC call to test the OSC server." )
  echo_parser.add_argument( "--host", default=DEFAULT_OSC_CLIENT_HOST,
    help="The host address that the OSC server will listen on." )
  echo_parser.add_argument( "--port", type=int, default=DEFAULT_OSC_SERVER_PORT, 
    help="The port that the OSC server will listen on." )
  echo_parser.add_argument( "body", default="Hello, world!",
    help="The message to echo." )
  echo_parser.set_defaults( func=echo_handler )

  args = parser.parse_args()
  args.func( args )