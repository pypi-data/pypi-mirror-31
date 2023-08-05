# -*- coding: UTF-8 -*-
#   Copyright 2009-2018 Oli Schacher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

from fuglu.shared import ScannerPlugin, string_to_actioncode, DEFER, DUNNO, actioncode_to_string, apply_template
from fuglu.localStringEncoding import force_bString, force_uString
import socket
import os


#
# sssp_utils.py Some utility functions used by the SSSP python sampl apps.
#
# Copyright (c) 2006 Sophos Plc, www.sophos.com.
#


import re


# Regular Expressions defining some messages from the server.

acceptsyntax = re.compile(b"^ACC\s+(.*?)\s*$")
optionsyntax = re.compile(b"^(\w+):\s*(.*?)\s*$")
virussyntax = re.compile(b"^VIRUS\s+(\S+)\s+(.*)")
typesyntax = re.compile(b"^TYPE\s+(\w+)")
donesyntax = re.compile(b"^DONE\s+(\w+)\s+(\w+)\s+(.*?)\s*$")
eventsyntax = re.compile(b"^([A-Z]+)\s+(\w+)")


# Receives a line of text from the socket
# \r chars are discarded
# The line is terminated by a \n
# NUL chars indicate a broken socket

def receiveline(s):
    line = b''
    done = 0
    while not done:
        c = s.recv(1)
        if c == b'':
            return b''
        done = (c == b'\n')
        if not done and c != b'\r':
            line = line + c

    return line


# Receives a whole message. Messages are terminated by
# a blank line

def receivemsg(s):

    response = []
    finished = 0

    while not finished:
        msg = receiveline(s)
        finished = (len(msg) == 0)
        if not finished:
            response.append(msg)

    return response


# Receives the ACC message which is a single line
# conforming to the acceptsyntax RE.

def accepted(s):
    acc = receiveline(s)
    return acceptsyntax.match(acc)


# Reads a message which should be a list of options
# and transforms them into a dictionary

def readoptions(s):
    resp = receivemsg(s)
    opts = {}

    for l in resp:
        parts = optionsyntax.findall(l)
        for p in parts:
            p0 = force_uString(p[0])
            if p0 not in opts:
                opts[p0] = []

            opts[p0].append(force_uString(p[1]))

    return opts


# Performs the initial exchange of messages.

def exchangeGreetings(s):

    line = receiveline(s)

    if not line.startswith(b'OK SSSP/1.0'):
        return 0

    s.send(b'SSSP/1.0\n')

    if not accepted(s):
        print("Greeting Rejected!!")
        return 0

    return 1


# performs the final exchange of messages

def sayGoodbye(s):
    s.send(b'BYE\n')
    receiveline(s)


class SSSPPlugin(ScannerPlugin):

    """ This plugin scans the suspect using the sophos SSSP protocol.

Prerequisites: Requires a running sophos daemon with dynamic interface (SAVDI)
"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where the SSSP server runs',
            },

            'port': {
                'default': '4010',
                'description': "tcp port or path to unix socket",
            },

            'timeout': {
                'default': '30',
                'description': 'socket timeout',
            },

            'maxsize': {
                'default': '22000000',
                'description': "maximum message size, larger messages will not be scanned. ",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if infection is detected (DUNNO, REJECT, DELETE)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
        }
        self.logger = self._logger()

    def __str__(self):
        return "Sophos"

    def _problemcode(self):
        retcode = string_to_actioncode(
            self.config.get(self.section, 'problemaction'), self.config)
        if retcode is not None:
            return retcode
        else:
            # in case of invalid problem action
            return DEFER

    def examine(self, suspect):
        enginename = 'sophos'

        if suspect.size > self.config.getint(self.section, 'maxsize'):
            self.logger.info('Not scanning - message too big')
            return

        content = suspect.get_source()

        for i in range(0, self.config.getint(self.section, 'retries')):
            try:
                viruses = self.scan_stream(content)
                if viruses is not None:
                    self.logger.info(
                        "Virus found in message from %s : %s" % (suspect.from_address, viruses))
                    suspect.tags['virus'][enginename] = True
                    suspect.tags['%s.virus' % enginename] = viruses
                    suspect.debug('viruses found in message : %s' % viruses)
                else:
                    suspect.tags['virus'][enginename] = False

                if viruses is not None:
                    virusaction = self.config.get(self.section, 'virusaction')
                    actioncode = string_to_actioncode(virusaction, self.config)
                    firstinfected, firstvirusname = list(viruses.items())[0]
                    values = dict(
                        infectedfile=firstinfected, virusname=firstvirusname)
                    message = apply_template(
                        self.config.get(self.section, 'rejectmessage'), suspect, values)
                    return actioncode, message
                return DUNNO
            except Exception as e:
                self.logger.warning("Error encountered while contacting SSSP server (try %s of %s): %s" % (
                    i + 1, self.config.getint(self.section, 'retries'), str(e)))
        self.logger.error("SSSP scan failed after %s retries" %
                          self.config.getint(self.section, 'retries'))

        return self._problemcode()

    def scan_stream(self, buf):
        """
        Scan a buffer

        buffer (string) : buffer to scan

        return either :
          - (dict) : {filename1: "virusname"}
          - None if no virus found
        """

        s = self.__init_socket__()
        dr = {}

        # Read the welcome message

        if not exchangeGreetings(s):
            raise Exception("SSSP Greeting failed")

        # QUERY to discover the maxclassificationsize
        s.send(b'SSSP/1.0 QUERY\n')

        if not accepted(s):
            raise Exception("SSSP Query rejected")

        options = readoptions(s)

        # Set the options for classification
        enableoptions = [
            b"TnefAttachmentHandling",
            b"ActiveMimeHandling",
            b"Mime",
            b"ZipDecompression",
            b"DynamicDecompression",
        ]

        enablegroups = [
            b'GrpExecutable',
            b'GrpArchiveUnpack',
            b'GrpSelfExtract',
            b'GrpInternet',
            b'GrpSuper',
            b'GrpMisc',
        ]

        sendbuf = "OPTIONS\nreport:all\n"
        for opt in enableoptions:
            sendbuf += "savists: %s 1\n" % force_uString(opt)


        for grp in enablegroups:
            sendbuf += "savigrp: %s 1\n" % force_uString(grp)

        # all sent, add aditional newline
        sendbuf += "\n"

        s.send(force_bString(sendbuf))

        if not accepted(s):
            raise Exception("SSSP Options not accepted")

        resp = receivemsg(s)

        for l in resp:
            if donesyntax.match(l):
                parts = donesyntax.findall(l)
                if parts[0][0] != b'OK':
                    raise Exception("SSSP Options failed")
                break

        # Send the SCAN request

        s.send(force_bString('SCANDATA ' + str(len(buf)) + '\n'))
        if not accepted(s):
            raise Exception("SSSP Scan rejected")

        s.sendall(force_bString(buf))

        # and read the result
        events = receivemsg(s)

        for l in events:
            if virussyntax.match(l):
                parts = virussyntax.findall(l)
                virus = force_uString(parts[0][0])
                filename = force_uString(parts[0][1])
                dr[filename] = virus

        try:
            sayGoodbye(s)
            s.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            self.logger.warning('Error terminating connection: %s', str(e))
        finally:
            s.close()

        if dr == {}:
            return None
        else:
            return dr

    def __init_socket__(self):
        unixsocket = False

        try:
            int(self.config.get(self.section, 'port'))
        except ValueError:
            unixsocket = True

        if unixsocket:
            sock = self.config.get(self.section, 'port')
            if not os.path.exists(sock):
                raise Exception("unix socket %s not found" % sock)
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(self.config.getint(self.section, 'timeout'))
            try:
                s.connect(sock)
            except socket.error:
                raise Exception(
                    'Could not reach SSSP server using unix socket %s' % sock)
        else:
            host = self.config.get(self.section, 'host')
            port = int(self.config.get(self.section, 'port'))
            timeout = self.config.getint(self.section, 'timeout')
            try:
                s = socket.create_connection((host, port), timeout)
            except socket.error:
                raise Exception(
                    'Could not reach SSSP server using network (%s, %s)' % (host, port))

        return s

    def lint(self):
        viract = self.config.get(self.section, 'virusaction')
        print("Virusaction: %s" % actioncode_to_string(
            string_to_actioncode(viract, self.config)))
        allok = self.check_config() and self.lint_eicar()
        return allok

    def lint_eicar(self):
        stream = """Date: Mon, 08 Sep 2008 17:33:54 +0200
To: oli@unittests.fuglu.org
From: oli@unittests.fuglu.org
Subject: test eicar attachment
X-Mailer: swaks v20061116.0 jetmore.org/john/code/#swaks
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="----=_MIME_BOUNDARY_000_12140"

------=_MIME_BOUNDARY_000_12140
Content-Type: text/plain

Eicar test
------=_MIME_BOUNDARY_000_12140
Content-Type: application/octet-stream
Content-Transfer-Encoding: BASE64
Content-Disposition: attachment

UEsDBAoAAAAAAGQ7WyUjS4psRgAAAEYAAAAJAAAAZWljYXIuY29tWDVPIVAlQEFQWzRcUFpYNTQo
UF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCoNClBLAQIU
AAoAAAAAAGQ7WyUjS4psRgAAAEYAAAAJAAAAAAAAAAEAIAD/gQAAAABlaWNhci5jb21QSwUGAAAA
AAEAAQA3AAAAbQAAAAAA

------=_MIME_BOUNDARY_000_12140--"""

        result = self.scan_stream(force_bString(stream))
        if result is None:
            print("EICAR Test virus not found!")
            return False
        print("SSSP server found virus", result)
        return True

