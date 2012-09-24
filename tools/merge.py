#!/usr/bin/env python
#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2012, Chema Garcia
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    Neither the name of the SafetyBits nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
# Written by Chema Garcia
#      http://safetybits.net
#      http://twitter.com/sch3m4
#
# This tool is part of WhatsApp Forensic (https://github.com/sch3m4/wforensic)
#
# Version: 0.2b
#

try:
    import os
    import re
    import sys
    import shutil
    import sqlite3
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)

def merge(path,pattern,dest):
    """
    Reads from files in 'path' and dumps its contents to 'dest'
    """

    first = 0
    output = None
    mtableid = 0

    for filename in os.listdir(path):
        if not os.path.isfile(path + filename) or not re.match(pattern, filename):
            continue

        print "\n+ Merging: %s" % filename ,
        sys.stdout.flush()

        if first == 0:
            shutil.copy2 (path + filename, dest)
            first += 1
            continue
        elif output is None:
            output = sqlite3.connect(dest)
            wcursor = output.cursor()

        ccontacts = 0
        cmessages = 0

        # get all remote_key_jid values from messages table
        orig = sqlite3.connect(path + filename)
        rcursor = orig.cursor()

        if mtableid == 0:
            # get biggest message_table_id value (what is this column for? :-/ )
            wcursor.execute("SELECT MAX(message_table_id) FROM chat_list")
            try:
                mtableid = wcursor.fetchone()[0]
            except:
                print "\n\t- Error getting MAX(message_table_id), skipping file..."
                continue

        # get all key_remote_jid from the current file
        rcursor.execute("SELECT DISTINCT key_remote_jid FROM chat_list")

        # if each item from the above query does not exists, insert it
        for krjid in rcursor:
            wcursor.execute("SELECT key_remote_jid FROM chat_list WHERE key_remote_jid=?",krjid)
            try:
                if len(wcursor.fetchone()[0]) > 0:
                    continue
            except:
                try:
                    mtableid += 1  # increments message_table_id
                    data = (krjid[0], mtableid)
                    wcursor.execute("INSERT INTO chat_list (key_remote_jid,message_table_id) VALUES (?,?)", data)
                    ccontacts += 1
                except:
                    pass

        # get all messages from messages table
        rcursor.execute("SELECT key_remote_jid,key_from_me,key_id,status,needs_push,data,timestamp,media_url,media_mime_type,media_wa_type,media_size,media_name,latitude,longitude,thumb_image,remote_resource,received_timestamp,send_timestamp,receipt_server_timestamp,receipt_device_timestamp,raw_data FROM messages")
        messages = rcursor.fetchall()
        for msg in messages:
            try:
                wcursor.execute("INSERT INTO messages(key_remote_jid,key_from_me,key_id,status,needs_push,data,timestamp,media_url,media_mime_type,media_wa_type,media_size,media_name,latitude,longitude,thumb_image,remote_resource,received_timestamp,send_timestamp,receipt_server_timestamp,receipt_device_timestamp,raw_data) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",msg)
                cmessages += 1
            except:
                pass

        output.commit()

        print " (Merged %d contacts and %d messages)" % (ccontacts,cmessages) ,
        sys.stdout.flush()

        orig.close()

    if output is not None:
        output.close()
    return

if __name__ == "__main__":
    print """
    #######################################
    #  WhatsApp Msgstore Merge Tool 0.2b  #
    #-------------------------------------#
    # Merges WhatsApp message files into  #
    #           a single one.             #
    #   This tool is part of WForensic    #
    # https://github.com/sch3m4/wforensic #
    #######################################
    """

    if len(sys.argv) != 4:
        print "Usage: %s /path/to/databases/to/be/merged/ files_pattern /path/to/output\n" % sys.argv[0]
        sys.exit(-1)

    if sys.argv[1][-1:] != '/':
        sys.argv[1] += '/'

    dir = os.path.dirname(sys.argv[3])

    if len(dir) > 0 and not os.path.isdir(dir):
        print "[e] Error: Directory \"%s\" does not exists\n" % sys.argv[3]
        sys.exit(-2)

    if not os.path.isdir(sys.argv[1]):
        print "[e] Error: \"%s\" is not a directory\n" % sys.argv[1]
        sys.exit(-3)

    print "[i] Origin: %s%s" % ( sys.argv[1] , sys.argv[2] )
    print "[i] Output file: %s" % sys.argv[3]

    merge(sys.argv[1],sys.argv[2], sys.argv[3])
    print "\n"
    sys.exit(0)
