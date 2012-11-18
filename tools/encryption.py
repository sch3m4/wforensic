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
# Thanks to Alejandro Ramos
#    www.securitybydefault.com
#    http://twitter.com/aramosf
#
# This tool is part of WhatsApp Forensic / https://sch3m4.github.com/wforensic
#
# Version: 0.4
#
#


try:
    import os
    import sys
    import errno
    import sqlite3
    import argparse
    from Crypto.Cipher import AES
except ImportError, e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)

key = "\x34\x6a\x23\x65\x2a\x46\x39\x2b\x4d\x73\x25\x7c\x67\x31\x7e\x35\x2e\x33\x72\x48\x21\x77\x65\x2c"
aes = None

MODE_ENCRYPT = 1
MODE_DECRYPT = 2

mode = None

total_msg = 0
total_contacts = 0


def getinfo(path):
    global total_msg
    global total_contacts
    
    db = sqlite3.connect(path)
    cur = db.cursor()
    res = cur.execute("SELECT COUNT(*) FROM messages UNION ALL SELECT COUNT(DISTINCT key_remote_jid) FROM chat_list").fetchall()
    cur.close()
    db.close()
    
    total_msg += res[0][0]
    total_contacts += res[1][0]

    return (res[0][0], res[1][0])


def set_aes():
    global aes
    if aes is None:
        # shoulds never fail
        print "[i] Setting AES key.......",
        try:
            aes = AES.new(key, AES.MODE_ECB)
            print "OK"
        except Exception, e:
            print "ERROR: %s" % e.msg
            sys.exit(-4)
    
    
def work_file(path, dest):
    global aes
    global mode
    global MODE_ENCRYPT
    global MODE_DECRYPT

    set_aes()

    # open input file
    try:
        ctext = open(path, 'rb')
    except Exception, e:
        print "ERROR: %s" % e.msg
        sys.exit(-5)

    # open output file
    try:
        dfile = os.path.basename(path)
        if mode == MODE_DECRYPT:
            dest += dfile.replace('.crypt', '')
        else:
            dest += dfile + '.crypt'
        ptext = open(dest, "wb")
    except Exception, e:
        print "ERROR: %s" % e.msg
        ctext.close()
        sys.exit(-6)

    if mode == MODE_ENCRYPT:
        print "\n[+] Encrypting",
    else:
        print "\n[+] Decrypting",
        
    print "%s (%s) ->" % (os.path.basename(path), os.path.basename(dest)),
    sys.stdout.flush()
    
    # read input file and outputs decrypted block to output file
    cbytes = 0
    backwards = 0
    for block in iter(lambda: ctext.read(AES.block_size), ''):
        if mode == MODE_ENCRYPT:
            ptext.write(aes.encrypt(block))
        else:
            ptext.write(aes.decrypt(block))

        cbytes += AES.block_size

        for i in range(backwards):
            sys.stdout.write("\b")
        backwards = len(str(cbytes)) + len(" Bytes")

        print "%d Bytes" % cbytes,
        sys.stdout.flush()

    ctext.close()
    ptext.close()

    if mode == MODE_DECRYPT:
        totmsg, peermsg = getinfo(dest)
        print "\n\t+ %d Messages from %d contacts" % (totmsg, peermsg)
        sys.stdout.flush()


def work_dir(path, dest):

    set_aes()

    aux = []
    
    # find and store files
    for root, dirs, files in os.walk(path):
        for file in files:
                aux.append(os.path.join(root,file))
          
    filenames = sorted(aux)

    for filename in filenames:
        work_file( filename, dest )

    return


if __name__ == "__main__":    
    print """
    #######################################
    #    WhatsApp Encryption Tool 0.4     #
    #-------------------------------------#
    #  Decrypts encrypted msgstore files  #
    #   This tool is part of WForensic    #
    # https://sch3m4.github.com/wforensic #
    #######################################
    """
    
    # specify what arguments do we accept
    parser = argparse.ArgumentParser()
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--encrypt', help='Encryption mode', dest='operation' ,  action='store_const', const='encrypt')
    group1.add_argument('--decrypt', help='Decryption mode', dest='operation' ,  action='store_const', const='decrypt')
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument('--file', type=str, help='Encryption mode', dest='file' ,  action='store')
    group2.add_argument('--dir', type=str, help='Decryption mode', dest='dir' ,  action='store')
    parser.add_argument('--output-dir', type=str , help='Output directory' , dest='output', action='store' , required = True)
    args = parser.parse_args()

    if args.operation == 'encrypt':
        mode = MODE_ENCRYPT
    else:
        mode = MODE_DECRYPT
        
    if args.output[:1] == '.':
        args.output += '/'
            
    # directory
    if args.dir is not None:

        if args.dir[-1:] != '/':
            args.dir += '/'

        if args.output[-1:] != '/':
            args.output += '/'
        
        if not os.path.isdir(args.dir):
            print "[e] Input directory not found!"
            sys.exit(-1)
                
    elif not os.path.isfile(args.file):
        print "[e] Input file not found!"
        sys.exit(-3)

    try:
        os.makedirs(os.path.dirname(args.output))
    except OSError as err:
        if err.errno == errno.EEXIST:
            pass
        else:
            print "[e] Error creating output directory: %s\n"
            sys.exit(-2)
                
    if args.dir is not None:
        work_dir(args.dir, args.output)
    else:  # single file
        work_file(args.file, args.output )
        
    print "\n[i] Gathered %d messages from %d contacts!" % (total_msg,total_contacts)

    print "\n[+] Done!\n"
    sys.exit(0)
