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

try:
    from Crypto.Cipher import AES
    from os.path import isfile,dirname,exists
    import sys
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)
    
key = "\x34\x6a\x23\x65\x2a\x46\x39\x2b\x4d\x73\x25\x7c\x67\x31\x7e\x35\x2e\x33\x72\x48\x21\x77\x65\x2c"

def main():
    print """
    #######################################
    #        WhatsApp Forensic Tool       #
    #-------------------------------------#
    #  Decrypts encrypted msgstore files  #
    #   This tool is part of WForensic    #
    # https://github.com/sch3m4/wforensic #
    #######################################
    """
    
    if not len(sys.argv) is 3:
        print "[i] Usage: %s <encrypted_file> <output_file>" % sys.argv[0]
        print "\nExample: %s msgstore-2012-05-07.1.db.crypt msgstore-2012-05-07.1.db\n" % sys.argv[0]
        sys.exit(0)
        
    if not isfile(sys.argv[1]) or not exists(sys.argv[1]):
        print "[e] Cannot access to \"%s\"\n" % sys.argv[1]
        sys.exit(-2)
    
    dname = dirname(sys.argv[2])
    if len(dname) > 0 and not exists(dname):
        print "[e] Path \"%s\" does not exists!\n" % sys.argv[2]
        sys.exit(-3)
    
    # shoulds never fail
    print "[i] Setting AES key......." ,
    try:
        aes = AES.new(key,AES.MODE_ECB)
        print "OK"
    except Exception,e:
        print "ERROR: %s" % e.msg
        sys.exit(-4)
    
    # open input file
    print "[i] Opening input file...." ,
    try:
        ctext = open(sys.argv[1],'rb')
        print "OK"
    except Exception , e:
        print "ERROR: %s" % e.msg
        sys.exit(-5)
    
    # open output file
    print "[i] Opening output file..." ,
    try:
        ptext = open(sys.argv[2],"wb")
        print "OK"
    except Exception,e:
        print "ERROR: %s" % e.msg
        ctext.close()
        sys.exit(-6)

    # read input file and outputs decrypted block to output file
    print "[i] Decrypting............" ,
    cbytes = 0    
    for block in iter(lambda: ctext.read(AES.block_size), ''):
        ptext.write(aes.decrypt(block))
        cbytes += AES.block_size
    
    ctext.close()
    ptext.close()
    
    print "OK (%d bytes)\n" % cbytes

if __name__ == "__main__":
    main()
    sys.exit(0)
    