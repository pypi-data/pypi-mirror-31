#!/usr/bin/env python

'''

Copyright (C) 2018 The Board of Trustees of the Leland Stanford Junior
University.
Copyright (C) 2018 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

from stools.version import __version__
from stools.clair.image import export_to_targz
from stools.clair.api import Clair
from multiprocessing import Process
import argparse
import os
import requests
import shutil
import sys
import tempfile
import time


def get_parser():
    parser = argparse.ArgumentParser(description="Singularity Clair Scanner")

    parser.add_argument('--version', dest="version", 
                        help="show version and exit.", 
                        default=False, action='store_true')

    parser.add_argument('--start-server', dest="server", 
                        help="If running natively, start the web server too.", 
                        default=True, action='store_true')

    parser.add_argument("images", nargs='*',
                         help='Singularity images to scan.', 
                         type=str)

    parser.add_argument("--port", default=8080,
                      help='port to serve application (default 8080)', 
                      type=int)

    parser.add_argument("--host", default="127.0.0.1",
                         help='host to serve application (default 127.0.0.1)', 
                         type=str)

    parser.add_argument("--clair-port", default=6060,
                      help='port Clair is running on (default 6060)', 
                      type=int, dest="clair_port")

    parser.add_argument("--clair-host", default="127.0.0.1",
                         help='host Clair running from (default clair-scanner)', 
                         type=str, dest="clair_host")

    return parser

def version():
    print("\nSingularity Clair Scanner v%s" %__version__)


def main():

    parser = get_parser()

    def help(retval=0):
        '''print help, including the software version and active client 
           and exit with return code.
        '''
        version()
        parser.print_help()
        sys.exit(retval)
    

    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()
    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    if args.version is True:
        version()
        sys.exit(0)

    # Generate Clair controller
    clair = Clair(args.clair_host, args.clair_port)
    if not clair.ping():
        sys.exit(1)

    print(clair)
    
    # Local Server
    webroot = '/var/www/images'
    server = 'http://%s:%s/' %(args.host, args.port)

    # Start the server and serve static files from root

    if args.server is True:
        from stools.clair.server import start
        print('\n1. Starting server...')
        webroot = tempfile.mkdtemp()
        process = Process(target=start, args=(args.port, args.host, webroot))
        # start(port=args.port, host=args.host, static_folder=webroot)
        process.daemon = True
        process.start()
        time.sleep(1)

    # Check health of server
    print('\n1. Checking server...')
    response = requests.get(server)
    if response.status_code != 200:
        print('Server not found running at %s' %server)
        sys.exit(1)

    print('2. Processing images!')
    for image in args.images:

        # 1. decompress to sandbox --> tar.gz
        targz = export_to_targz(image, via_build=False)
        print("...exported %s to %s" %(image, targz))

        # 2. Move to webroot
        targz_web = os.path.join(webroot, os.path.basename(targz))
        os.rename(targz, targz_web)
        targz_url = "%simages/%s" %(server, os.path.basename(targz))

        # 3. Scan with Clair, use image name
        print("...serving %s to Clair" %(targz_url))
        clair.scan(targz_web, os.path.basename(image))

        # 4. Generate report
        print('3. Generating report!')
        report = clair.report(os.path.basename(image))
        clair.print(report)

    # Shut down temporary server
    process.terminate()
    shutil.rmtree(webroot)
    
if __name__ == '__main__':
    main()
