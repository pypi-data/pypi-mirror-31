# -*- coding: UTF-8 -*- #   Copyright 2009-2018 Oli Schacher
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
from fuglu.shared import ScannerPlugin, DUNNO, DEFER, Suspect, string_to_actioncode, apply_template
from fuglu.extensions.sql import DBConfig, get_session, SQL_EXTENSION_ENABLED
from fuglu.localStringEncoding import force_bString, force_uString
from string import Template
import time
import socket
import email
import re
import os
import sys


GTUBE = """Date: Mon, 08 Sep 2008 17:33:54 +0200
To: oli@unittests.fuglu.org
From: oli@unittests.fuglu.org
Subject: test scanner

  XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X
"""



class SAPlugin(ScannerPlugin):

    """This plugin passes suspects to a spamassassin daemon.

Prerequisites: SPAMD must be installed and running (not necessarily on the same box as fuglu)

Notes for developers:

if forwardoriginal=False, the message source will be completely replaced with the answer from spamd.

Tags:

 * reads ``SAPlugin.skip``, (boolean) skips scanning if this is True
 * reads ``SAPlugin.tempheader``, (text) prepends this text to the scanned message (use this to pass temporary headers to spamassassin which should not be visible in the final message)
 * sets ``spam['spamassassin']`` (boolean)
 * sets ``SAPlugin.spamscore`` (float) if possible
 * sets ``SAPlugin.skipreason`` (string) if the message was not scanned (fuglu >0.5.0)
 * sets ``SAPlugin.report``, (string) report from spamd or spamheader (where score was found) depending on forwardoriginal setting
"""

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'host': {
                'default': 'localhost',
                'description': 'hostname where spamd runs',
            },

            'port': {
                'default': '783',
                'description': "tcp port number or path to spamd unix socket",
            },

            'timeout': {
                'default': '30',
                'description': 'how long should we wait for an answer from sa',
            },

            'maxsize': {
                'default': '256000',
                'description': "maximum size in bytes. larger messages will be skipped",
            },

            'strip_oversize':{
                'default': '0',
                'description': "enable scanning of messages larger than maxsize. all attachments will be stripped and only headers, plaintext and html part will be scanned. If message is still oversize it will be truncated. Also enable forwardoriginal or truncated version of large messages will be forwarded",
            },

            'retries': {
                'default': '3',
                'description': 'how often should fuglu retry the connection before giving up',
            },

            'scanoriginal': {
                'default': '1',
                'description': "should we scan the original message as retreived from postfix or scan the current state \nin fuglu (which might have been altered by previous plugins)\nonly set this to disabled if you have a custom plugin that adds special headers to the message that will be \nused in spamassassin rules",
            },

            'forwardoriginal': {
                'default': '0',
                'description': """forward the original message or replace the content as returned by spamassassin\nif this is set to True/1/Yes , no spamassassin headers will be visible in the final message.\n"original" in this case means "as passed to spamassassin", eg. if 'scanoriginal' is set to 0 above this will forward the\nmessage as retreived from previous plugins """,
            },

            'spamheader': {
                'default': 'X-Spam-Status',
                'description': """what header does SA set to indicate the spam status\nNote that fuglu requires a standard header template configuration for spamstatus and score extraction\nif 'forwardoriginal' is set to 0\neg. start with _YESNO_ or _YESNOCAPS_ and contain score=_SCORE_""",
            },

            'peruserconfig': {
                'default': '1',
                'description': 'enable user_prefs in SA. This hands the recipient address over the spamd connection which allows SA to search for configuration overrides',
            },

            'highspamlevel': {
                'default': '15',
                'description': 'spamscore threshold to mark a message as high spam',
            },

            'highspamaction': {
                'default': 'DEFAULTHIGHSPAMACTION',
                'description': "what should we do with high spam (spam score above highspamlevel)",
            },

            'lowspamaction': {
                'default': 'DEFAULTLOWSPAMACTION',
                'description': "what should we do with low spam (eg. detected as spam, but score not over highspamlevel)",
            },

            'problemaction': {
                'default': 'DEFER',
                'description': "action if there is a problem (DUNNO, DEFER)",
            },

            'rejectmessage': {
                'default': 'message identified as spam',
                'description': "reject message template if running in pre-queue mode",
            },

            'check_sql_blacklist': {
                'default': '0',
                'description': "consult spamassassins(or any other) sql blacklist for messages that are too big for spam checks\nrequires the sql extension to be enabled",
            },

            'sql_blacklist_dbconnectstring': {
                'default': 'mysql:///localhost/spamassassin',
                'description': "sqlalchemy db connect string",
                'confidential': True,
            },

            'sql_blacklist_sql': {
                'default': """SELECT value FROM userpref WHERE prefid='blacklist_from' AND username in ('$GLOBAL',concat('%',${to_domain}),${to_address})""",
                'description': "SQL query to get the blacklist entries for a suspect\nyou may use template variables: ${from_address} ${from_domain} ${to_address} ${to_domain}",
            },

        }
        self.logger = self._logger()


    def __str__(self):
        return "SpamAssassin"


    def lint(self):
        allok = self.check_config() and self.lint_ping() and self.lint_spam() and self.lint_blacklist()
        return allok


    def lint_blacklist(self):
        if not self.config.has_option(self.section, 'check_sql_blacklist') or not self.config.getboolean(self.section, 'check_sql_blacklist'):
            return True

        if not SQL_EXTENSION_ENABLED:
            print("SQL Blacklist requested but SQLALCHEMY is not enabled")
            return False

        session = get_session(self.config.get(self.section, 'sql_blacklist_dbconnectstring'))
        suspect = Suspect('dummy@example.com', 'dummy@example.com', '/dev/null')
        conf_sql = self.config.get(self.section, 'sql_blacklist_sql')
        sql, params = self._replace_sql_params(suspect, conf_sql)
        try:
            session.execute(sql, params)
            print("Blacklist SQL Query OK")
            return True
        except Exception as e:
            print(e)
            return False


    def lint_ping(self):
        """ping sa"""
        retries = self.config.getint(self.section, 'retries')
        for i in range(0, retries):
            try:
                self.logger.debug('Contacting spamd (Try %s of %s)' % (i + 1, retries))
                s = self.__init_socket()
                s.sendall(b'PING SPAMC/1.2')
                s.sendall(b"\r\n")
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line = force_uString(socketfile.readline())
                line = line.strip()
                answer = line.split()
                if len(answer) != 3:
                    print("Invalid SPAMD PONG: %s" % line)
                    return False

                if answer[2] != "PONG":
                    print("Invalid SPAMD Pong: %s" % line)
                    return False
                print("Got: %s" % line)
                return True
            except socket.timeout:
                print('SPAMD Socket timed out.')
            except socket.herror as h:
                print('SPAMD Herror encountered : %s' % str(h))
            except socket.gaierror as g:
                print('SPAMD gaierror encountered: %s' % str(g))
            except socket.error as e:
                print('SPAMD socket error: %s' % str(e))

            time.sleep(1)
        return False


    def lint_spam(self):
        spamflag, score, rules = self.safilter_symbols(GTUBE, 'test')
        if 'GTUBE' in rules:
            print("GTUBE Has been detected correctly")
            return True
        else:
            print("SA did not detect GTUBE")
            return False


    def _replace_sql_params(self, suspect, conf_sql):
        """replace template variables in sql with parameters and set sqlalchemy parameters from suspect"""
        values = {}
        values['from_address'] = ':fromaddr'
        values['to_address'] = ':toaddr'
        values['from_domain'] = ':fromdomain'
        values['to_domain'] = ':todomain'

        template = Template(conf_sql)

        sql = template.safe_substitute(values)

        params = {
            'fromaddr': suspect.from_address,
            'toaddr': suspect.to_address,
            'fromdomain': suspect.from_domain,
            'todomain': suspect.to_domain,
        }

        return sql, params


    def check_sql_blacklist(self, suspect, runtimeconfig=None):
        """Check this message against the SQL blacklist. returns highspamaction on hit, DUNNO otherwise"""
        #work in progress
        if not self.config.has_option(self.section, 'check_sql_blacklist') or not self.config.getboolean(self.section, 'check_sql_blacklist'):
            return DUNNO

        if not SQL_EXTENSION_ENABLED:
            self.logger.error('Cannot check sql blacklist, SQLALCHEMY extension is not available')
            return DUNNO

        try:
            dbsession = get_session(self.config.get(self.section, 'sql_blacklist_dbconnectstring'))
            conf_sql = self.config.get(self.section, 'sql_blacklist_sql')
            sql, params = self._replace_sql_params(suspect, conf_sql)
            resultproxy = dbsession.execute(sql, params)
        except Exception as e:
            self.logger.error('Could not read blacklist from DB: %s' % e)
            suspect.debug('Blacklist check failed: %s' % e)
            return DUNNO

        for result in resultproxy:
            dbvalue = result[0]  # this value might have multiple words
            allvalues = dbvalue.split()
            for blvalue in allvalues:
                self.logger.debug(blvalue)
                # build regex
                # translate glob to regexr
                # http://stackoverflow.com/questions/445910/create-regex-from-glob-expression
                regexp = re.escape(blvalue).replace(r'\?', '.').replace(r'\*', '.*?')
                self.logger.debug(regexp)
                pattern = re.compile(regexp)

                if pattern.search(suspect.from_address):
                    self.logger.debug('%s Blacklist match : %s for sa pref %s' % (suspect.id, suspect.from_address, blvalue))
                    confcheck = self.config
                    if runtimeconfig is not None:
                        confcheck = runtimeconfig
                    configaction = string_to_actioncode(confcheck.get(self.section, 'highspamaction'), self.config)
                    suspect.tags['spam']['SpamAssassin'] = True
                    prependheader = self.config.get( 'main', 'prependaddedheaders')
                    suspect.addheader("%sBlacklisted" % prependheader, blvalue)
                    suspect.debug('Sender is Blacklisted: %s' % blvalue)
                    if configaction is None:
                        return DUNNO
                    return configaction

        return DUNNO


    def _problemcode(self):
        retcode = string_to_actioncode(
            self.config.get(self.section, 'problemaction'), self.config)
        if retcode is not None:
            return retcode
        else:
            # in case of invalid problem action
            return DEFER


    def _extract_spamstatus(self, msgrep, spamheadername, suspect):
        """
        extract spamstatus and score from messages returned by spamassassin
        Assumes a default spamheader configuration, eg
        add_header spam Flag _YESNOCAPS_
        or
        add_header all Status _YESNO_, score=_SCORE_ required=_REQD_ tests=_TESTS_ autolearn=_AUTOLEARN_ version=_VERSION_

        :param msgrep: email.message.Message object built from the returned source
        :param spamheadername: name of the header containing the status information
        :return: tuple isspam,spamscore . isspam is a boolean, spamscore a float or None if the spamscore can't be extracted
        """
        isspam = False
        spamheader = msgrep[spamheadername]

        spamscore = None
        if spamheader is None:
            self.logger.warning('%s Did not find Header %s in returned message from SA' % (suspect.id, spamheadername))
        else:
            if re.match(r"""^YES""", spamheader.strip(), re.IGNORECASE) is not None:
                isspam = True

            patt = re.compile('Score=([\-\d.]{1,10})', re.IGNORECASE)
            m = patt.search(spamheader)

            if m is not None:
                spamscore = float(m.group(1))
                self.logger.debug('%s Spamscore: %s' % (suspect.id, spamscore))
                suspect.debug('Spamscore: %s' % spamscore)
            else:
                self.logger.warning('%s Could not extract spam score from header: %s' % (suspect.id, spamheader))
                suspect.debug( 'Could not read spam score from header %s' % spamheader)
            return isspam, spamscore, spamheader
        return isspam, spamscore


    def _strip_attachments(self, content, maxsize):
        """
        strip all attachments from multipart mails except for plaintext and html text parts.
        if message is still too long, truncate.

        Args:
            content: string containing message source
            maxsize: integer of maximum message size accepted by spamassassin

        Returns: stripped and truncated message content

        """

        msgrep = email.message_from_string(content)

        if msgrep.is_multipart():
            new_src = ''
            for hdr, val in msgrep.items():
                headerline = '%s: %s\r\n' % (hdr, val)
                new_src += headerline
            new_src += '\r\n'
            for part in msgrep.walk():
                # only plaintext and html parts but no text attachments
                if part.get_content_maintype() == 'text' and part.get_filename() is None:
                    new_src += part.as_string()
                    new_src += '\r\n\r\n'
        else:
            # text only mail - keep full content and truncate later
            new_src = content

        if len(new_src) > maxsize:
            # truncate to maxsize
            new_src = new_src[:maxsize-1]

        return new_src

    # helper to get diff from two lists/dicts
    def diff(self, new, old):
        old = set(old)
        return [item for item in new if item not in old]

    def examine(self, suspect):
        # check if someone wants to skip sa checks
        if suspect.get_tag('SAPlugin.skip') is True:
            self.logger.debug('%s Skipping SA Plugin (requested by previous plugin)' % suspect.id)
            suspect.set_tag('SAPlugin.skipreason', 'requested by previous plugin')
            return DUNNO

        runtimeconfig = DBConfig(self.config, suspect)

        spamsize = suspect.size
        maxsize = self.config.getint(self.section, 'maxsize')
        strip_oversize = self.config.getboolean(self.section, 'strip_oversize')

        if spamsize > maxsize and not strip_oversize:
            self.logger.info('%s Size Skip, %s > %s' % (suspect.id, spamsize, maxsize))
            suspect.debug('Too big for spamchecks. %s > %s' % (spamsize, maxsize))
            prependheader = self.config.get('main', 'prependaddedheaders')
            suspect.addheader("%sSA-SKIP" % prependheader, 'Too big for spamchecks. %s > %s' % (spamsize, maxsize))
            suspect.set_tag('SAPlugin.skipreason', 'size skip')
            return self.check_sql_blacklist(suspect)

        if self.config.getboolean(self.section, 'scanoriginal'):
            content = suspect.get_original_source()
        else:
            content = suspect.get_source()

        stripped = False
        if spamsize > maxsize:
            stripped = True
            # keep copy of original content before stripping
            content_orig = content
            content = self._strip_attachments(content, maxsize)

        # stick to bytes
        content = force_bString(content)

        # prepend temporary headers set by other plugins
        tempheader = suspect.get_tag('SAPlugin.tempheader')
        if tempheader is not None:
            if isinstance(tempheader, list):
                tempheader = "\r\n".join(tempheader)
            tempheader = tempheader.strip()
            if tempheader != '':
                content = force_bString(tempheader + '\r\n') + content

        forwardoriginal = self.config.getboolean(self.section, 'forwardoriginal')
        if forwardoriginal:
            ret = self.safilter_report(content, suspect.to_address)
            if ret is None:
                suspect.debug('SA report Scan failed - please check error log')
                self.logger.error('%s SA report scan FAILED' % suspect.id)
                suspect.addheader('%sSA-SKIP' % self.config.get('main', 'prependaddedheaders'), 'SA scan failed')
                suspect.set_tag('SAPlugin.skipreason', 'scan failed')
                return self._problemcode()
            isspam, spamscore, report = ret
            suspect.tags['SAPlugin.report'] = report

        else:
            filtered = self.safilter(content, suspect.to_address)
            if filtered is None:
                suspect.debug('SA Scan failed - please check error log')
                self.logger.error('%s SA scan FAILED' % suspect.id)
                suspect.addheader('%sSA-SKIP' % self.config.get('main', 'prependaddedheaders'), 'SA scan failed')
                suspect.set_tag('SAPlugin.skipreason', 'scan failed')
                return self._problemcode()
            else:
                if stripped:
                    # create msgrep of filtered msg
                    msgrep_filtered = email.message_from_string(filtered)
                    header_new = []
                    header_old = []
                    # create a msgrep from original msg
                    msgrep_orig = email.message_from_string(content_orig)
                    # read all headers from after-scan and before-scan
                    for h,v in msgrep_filtered.items():
                        header_new.append(h.strip() + ': ' + v.strip())
                    for h,v in msgrep_orig.items():
                        header_old.append(h.strip() + ': ' + v.strip())
                    # create a list of headers added by spamd
                    # header diff between before-scan and after-scan msg
                    header_new = reversed(self.diff(header_new, header_old))
                    # add headers to msg
                    for i in header_new:
                        if re.match('^Received: ', i, re.I):
                            continue
                        # in case of stripped msg add header to original content
                        content_orig = i + '\r\n' + content_orig
                    content = content_orig
                else:
                    content = filtered
            if sys.version_info > (3,):
                # Python 3 and larger
                # the basic "str" type is unicode
                if isinstance(content,str):
                    newmsgrep = email.message_from_string(content)
                else:
                    newmsgrep = email.message_from_bytes(content)
            else:
                # Python 2.x
                newmsgrep = email.message_from_string(content)
            suspect.set_source(content)
            spamheadername = self.config.get(self.section, 'spamheader')
            isspam, spamscore, report = self._extract_spamstatus(newmsgrep, spamheadername, suspect)
            suspect.tags['SAPlugin.report'] = report
            self.logger.debug('suspect %s %s %s %s' % (suspect.id, isspam, spamscore, suspect.get_tag('SAPlugin.report')))

        action = DUNNO
        message = None

        if isspam:
            self.logger.debug('%s Message is spam' % suspect.id)
            suspect.debug('Message is spam')

            configaction = string_to_actioncode(
                runtimeconfig.get(self.section, 'lowspamaction'), self.config)
            if configaction is not None:
                action = configaction
            values = dict(spamscore=spamscore)
            message = apply_template(
                self.config.get(self.section, 'rejectmessage'), suspect, values)
        else:
            self.logger.debug('%s Message is not spam' % suspect.id)
            suspect.debug('Message is not spam')

        suspect.tags['spam']['SpamAssassin'] = isspam
        suspect.tags['highspam']['SpamAssassin'] = False
        if spamscore is not None:
            suspect.tags['SAPlugin.spamscore'] = spamscore
            highspamlevel = runtimeconfig.getfloat(self.section, 'highspamlevel')
            if spamscore >= highspamlevel:
                suspect.tags['highspam']['SpamAssassin'] = True
                configaction = string_to_actioncode(runtimeconfig.get(self.section, 'highspamaction'), self.config)
                if configaction is not None:
                    action = configaction
        return action, message


    def __init_socket(self):
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
                raise Exception('Could not reach spamd using unix socket %s' % sock)
        else:
            host = self.config.get(self.section, 'host')
            port = int(self.config.get(self.section, 'port'))
            timeout = self.config.getint(self.section, 'timeout')
            try:
                s = socket.create_connection((host, port), timeout)
            except socket.error:
                raise Exception('Could not reach spamd using network (%s, %s)' % (host, port))

        return s


    def safilter(self, messagecontent, user):
        """pass content to sa, return sa-processed mail"""
        retries = self.config.getint(self.section, 'retries')
        peruserconfig = self.config.getboolean(self.section, 'peruserconfig')
        spamsize = len(messagecontent)
        for i in range(0, retries):
            try:
                self.logger.debug('Contacting spamd (Try %s of %s)' % (i + 1, retries))
                s = self.__init_socket()
                s.sendall(force_bString('PROCESS SPAMC/1.2'))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("Content-length: %s" % spamsize))
                s.sendall(force_bString("\r\n"))
                if peruserconfig:
                    s.sendall(force_bString("User: %s" % user))
                    s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(messagecontent))
                self.logger.debug('Sent %s bytes to spamd' % spamsize)
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line1_info = socketfile.readline()
                line1_info = force_uString(line1_info)  # convert to unicode string
                self.logger.debug(line1_info)
                line2_contentlength = socketfile.readline()
                line3_empty = socketfile.readline()
                content = socketfile.read()
                self.logger.debug('Got %s message bytes from back from spamd' % len(content))
                answer = line1_info.strip().split()
                if len(answer) != 3:
                    self.logger.error("Got invalid status line from spamd: %s" % line1_info)
                    continue

                version, number, status = answer
                if status != 'EX_OK':
                    self.logger.error("Got bad status from spamd: %s" % status)
                    continue

                return content
            except socket.timeout:
                self.logger.error('SPAMD Socket timed out.')
            except socket.herror as h:
                self.logger.error('SPAMD Herror encountered : %s' % str(h))
            except socket.gaierror as g:
                self.logger.error('SPAMD gaierror encountered: %s' % str(g))
            except socket.error as e:
                self.logger.error('SPAMD socket error: %s' % str(e))
            except Exception as e:
                self.logger.error(str(e))

            time.sleep(1)
        return None


    def safilter_symbols(self, messagecontent, user):
        """Pass content to sa, return spamflag, score, rules"""
        ret = self._safilter_content(messagecontent, user, 'SYMBOLS')
        if ret is None:
            return None

        status, score, content = ret

        content = force_uString(content)
        rules = content.split(',')
        return status, score, rules


    def safilter_report(self, messagecontent, user):
        return self._safilter_content(messagecontent, user, 'REPORT')


    def _safilter_content(self, messagecontent, user, command):
        """pass content to sa, return body"""
        assert command in ['SYMBOLS', 'REPORT', ]
        retries = self.config.getint(self.section, 'retries')
        peruserconfig = self.config.getboolean(self.section, 'peruserconfig')
        spamsize = len(messagecontent)
        for i in range(0, retries):
            try:
                self.logger.debug('Contacting spamd  (Try %s of %s)' % (i + 1, retries))
                s = self.__init_socket()
                s.sendall(force_bString('%s SPAMC/1.2' % command))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("Content-length: %s" % spamsize))
                s.sendall(force_bString("\r\n"))
                if peruserconfig:
                    s.sendall(force_bString("User: %s" % user))
                    s.sendall(force_bString("\r\n"))
                s.sendall(force_bString("\r\n"))
                s.sendall(force_bString(messagecontent))
                self.logger.debug('Sent %s bytes to spamd' % spamsize)
                s.shutdown(socket.SHUT_WR)
                socketfile = s.makefile("rb")
                line1_info = force_uString(socketfile.readline())
                self.logger.debug(line1_info)
                line2_spaminfo = force_uString(socketfile.readline())

                line3 = force_uString(socketfile.readline())
                content = socketfile.read()
                content = content.strip()

                self.logger.debug('Got %s message bytes from back from spamd' % len(content))
                answer = line1_info.strip().split()
                if len(answer) != 3:
                    self.logger.error("Got invalid status line from spamd: %s" % line1_info)
                    continue

                (version, number, status) = answer
                if status != 'EX_OK':
                    self.logger.error("Got bad status from spamd: %s" % status)
                    continue

                self.logger.debug('Spamd said: %s' % line2_spaminfo)
                spamword, spamstatusword, colon, score, slash, required = line2_spaminfo.split()
                spstatus = False
                if spamstatusword == 'True':
                    spstatus = True

                return spstatus, float(score), content
            except socket.timeout:
                self.logger.error('SPAMD Socket timed out.')
            except socket.herror as h:
                self.logger.error('SPAMD Herror encountered : %s' % str(h))
            except socket.gaierror as g:
                self.logger.error('SPAMD gaierror encountered: %s' % str(g))
            except socket.error as e:
                self.logger.error('SPAMD socket error: %s' % str(e))

            time.sleep(1)
        return None


    def debug_proto(self, messagecontent, command='SYMBOLS'):
        """proto debug.. only used for development"""
        command = command.upper()
        assert command in ['CHECK', 'SYMBOLS', 'REPORT',
                           'REPORT_IFSPAM', 'SKIP', 'PING', 'PROCESS', 'TELL']

        host = "127.0.0.1"
        port = 783
        timeout = 20

        spamsize = len(messagecontent)

        s = socket.create_connection((host, port), timeout)
        s.sendall('%s SPAMC/1.2' % command)
        s.sendall("\r\n")
        s.sendall("Content-length: %s" % spamsize)
        s.sendall("\r\n")
        s.sendall("\r\n")
        s.sendall(messagecontent)
        s.shutdown(socket.SHUT_WR)
        socketfile = s.makefile("rb")
        gotback = socketfile.read()
        print(gotback)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print('need command argument')
        sys.exit(1)
    plugin = SAPlugin(None)
    print("sending...")
    print("--------------")
    plugin.debug_proto(GTUBE, sys.argv[1])
    print("--------------")


