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
# This tool is part of WhatsApp Forensic (https://github.com/sch3m4/wforensic)
#
# Version: 0.3
#

try:
    import os
    import sys
    import errno
    import sqlite3
    from Crypto.Cipher import AES
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)
    
key = "\x34\x6a\x23\x65\x2a\x46\x39\x2b\x4d\x73\x25\x7c\x67\x31\x7e\x35\x2e\x33\x72\x48\x21\x77\x65\x2c"
aes = None

def getinfo(path):
    db = sqlite3.connect(path)
    cur = db.cursor()
    res = cur.execute("SELECT COUNT(*) FROM messages UNION ALL SELECT COUNT(DISTINCT key_remote_jid) FROM chat_list;").fetchall()
    cur.close()
    db.close()
    
    return (res[0][0],res[1][0])

def decrypt_file(path,dest):
    global aes
    
    if aes is None:
        # shoulds never fail
        print "[i] Setting AES key......." ,
        try:
            aes = AES.new(key,AES.MODE_ECB)
            print "OK"
        except Exception,e:
            print "ERROR: %s" % e.msg
            sys.exit(-4)
    
    # open input file
    print "\n[+] Decrypting %s (%s) ->" % (os.path.basename(path),os.path.basename(dest)) ,
    sys.stdout.flush()
    
    try:
        ctext = open(path,'rb')
    except Exception , e:
        print "ERROR: %s" % e.msg
        sys.exit(-5)
    
    # open output file
    try:
        ptext = open(dest,"wb")
    except Exception,e:
        print "ERROR: %s" % e.msg
        ctext.close()
        sys.exit(-6)

    # read input file and outputs decrypted block to output file
    cbytes = 0
    backwards = 0
    for block in iter(lambda: ctext.read(AES.block_size), ''):
        ptext.write(aes.decrypt(block))
        cbytes += AES.block_size

        for i in range(backwards):
            sys.stdout.write("\b")
        backwards = len(str(cbytes)) + len(" Bytes")
        
        print "%d Bytes" % cbytes ,
        sys.stdout.flush()

    ctext.close()
    ptext.close()
    
    totmsg,peermsg = getinfo(dest)
    print "\n\t+ %d Messages from %d contacts" % (totmsg,peermsg)
    sys.stdout.flush()

def decrypt_dir(path,dest):
    global aes

    # shoulds never fail
    print "[i] Setting AES key......." ,
    try:
        aes = AES.new(key,AES.MODE_ECB)
        print "OK"
    except Exception,e:
        print "ERROR: %s" % e.msg
        sys.exit(-4)
        
    for filename in os.listdir(path):
        if not os.path.isfile(path + filename):
            continue
        
        decrypt_file(path+filename,dest+filename.replace(".crypt",""))

    return

def usage(base):
    print "[i] Usage: %s [options] <output>" % base
    print "\n+ Options:"
    print "\t-f | --file <path> --------> Path to file to be decrypted"
    print "\t-d | --dir <path> ---------> Directory containing encrypted 'msgstore' files"
    print "\n+ Example: %s -f msgstore-2012-05-07.1.db.crypt msgstore-2012-05-07.1.db" % base
    print "+ Example: %s -d msgFiles/ plain/\n" % base
    sys.exit(0)
        
if __name__ == "__main__":
    print """
    #######################################
    #      WhatsApp Forensic Tool  0.3    #
    #-------------------------------------#
    #  Decrypts encrypted msgstore files  #
    #   This tool is part of WForensic    #
    # https://github.com/sch3m4/wforensic #
    #######################################
    """
    
    if not len(sys.argv) is 4:
        usage(sys.argv[0])
    
    if not sys.argv[1] in ["-f","--file","-d","--dir"]:
        usage(sys.argv[0])
    
    sys.argv[1] = sys.argv[1].replace("--file","-f")
    sys.argv[1] = sys.argv[1].replace("--dir","-d")
    
    # decrypt the whole directory
    if sys.argv[1] == "-d":
        
        if sys.argv[2][-1:] != '/':
            sys.argv[2] += '/'

        if sys.argv[3][-1:] != '/':
            sys.argv[3] += '/'
                        
        if not os.path.isdir(sys.argv[2]):
            print "[e] Input directory not found!"
            sys.exit(-1)
        
        try:
            os.makedirs(os.path.dirname(sys.argv[3]))
        except OSError as err:
            if err.errno == errno.EEXIST:
                pass
            else:
                print "[e] Error creating output directory: %s\n"
                sys.exit(-2)
                
        decrypt_dir ( sys.argv[2] , sys.argv[3] )
    elif not os.path.isfile(sys.argv[2]):
        print "[e] Input file not found!"
        sys.exit(-3)
    else: # decrypt a single file
        decrypt_file ( sys.argv[2] , sys.argv[3] )

    print "\n[+] Done!\n"        
    sys.exit(0)
    