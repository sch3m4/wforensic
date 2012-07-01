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
# Version: 0.1
#

try:
    import os
    import re
    import sys
    import sqlite3
except ImportError,e:
    print "[f] Required module missing. %s" % e.args[0]
    sys.exit(-1)
    
# method "iterdump" from sqlite3 currently fails (http://bugs.python.org/issue15109)
# renamed "iterdump" from python-pysqlite2
def dump_iterator(connection):
    """
    Returns an iterator to the dump of the database in an SQL text format.

    Used to produce an SQL dump of the database.  Useful to save an in-memory
    database for later restoration.  This function should not be called
    directly but instead called from the Connection method, iterdump().
    """

    cu = connection.cursor()
    yield('BEGIN TRANSACTION;')

    # sqlite_master table contains the SQL CREATE statements for the database.
    q = """
        SELECT name, type, sql
        FROM sqlite_master
            WHERE sql NOT NULL AND
            type == 'table'
        """
    schema_res = cu.execute(q)
    for table_name, type, sql in schema_res.fetchall():
        if table_name == 'sqlite_sequence':
            yield('DELETE FROM sqlite_sequence;')
        elif table_name == 'sqlite_stat1':
            yield('ANALYZE sqlite_master;')
        elif table_name.startswith('sqlite_'):
            continue
        # NOTE: Virtual table support not implemented
        #elif sql.startswith('CREATE VIRTUAL TABLE'):
        #    qtable = table_name.replace("'", "''")
        #    yield("INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)"\
        #        "VALUES('table','%s','%s',0,'%s');" %
        #        qtable,
        #        qtable,
        #        sql.replace("''"))
        else:
            yield('%s;' % sql)

        # Build the insert statement for each row of the current table
        res = cu.execute("PRAGMA table_info('%s')" % table_name)
        column_names = [str(table_info[1]) for table_info in res.fetchall()]
        q = "SELECT 'INSERT INTO \"%(tbl_name)s\" VALUES("
        q += ",".join(["'||quote(" + col + ")||'" for col in column_names])
        q += ")' FROM '%(tbl_name)s'"
        query_res = cu.execute(q % {'tbl_name': table_name})
        for row in query_res:
            #yield("%s;" % row[0])
            yield(row[0] + ';')

    # Now when the type is 'index', 'trigger', or 'view'
    q = """
        SELECT name, type, sql
        FROM sqlite_master
            WHERE sql NOT NULL AND
            type IN ('index', 'trigger', 'view')
        """
    schema_res = cu.execute(q)
    for name, type, sql in schema_res.fetchall():
        yield('%s;' % sql)

    yield('COMMIT;')

def merge(path,pattern,dest):
    
    output = sqlite3.connect(dest)
    
    len1 = 0 # current file
    len2 = 0 # output file
    backwards = 0

    for filename in os.listdir(path):
        if not os.path.isfile(path + filename) or not re.match(pattern,filename):
            continue
        
        len1 = 0
        
        print "+ Merging: %s -> " % filename ,
        sys.stdout.flush()
        
        orig = sqlite3.connect(path + filename)
        
        for line in dump_iterator(orig):
            try:
                lenline = len(str(line))
                
                if str(line).lower() == "commit;":
                    continue
            except:
                lenline = 0
                pass
            
            len1 += lenline
            len2 += lenline
            
            output.execute(line)
            
            # print progress
            for i in range(backwards):
                sys.stdout.write("\b")
                
            backwards = len(str(len1)) + len(str(len2)) + len("R: W:  / Bytes") + 1
            
            print "R: %d / W: %d Bytes" % (len1,len2) ,
            sys.stdout.flush()
            
        output.commit()
        orig.close()
        
        print ""

    output.close()
    return

if __name__ == "__main__":
    print """
    #######################################
    #   SQLite3 Database Merge Tool 0.1   #
    #-------------------------------------#
    # Merges SQLite3 database files into  #
    #           a single one.             #
    #   This tool is part of WForensic    #
    # https://github.com/sch3m4/wforensic #
    #######################################\n
    """
    
    if len(sys.argv) != 4:
        print "Usage: %s /path/to/databases/to/be/merged/ files_pattern /path/to/output\n" % sys.argv[0]
        sys.exit(-1)
    
    if sys.argv[1][-1:] != '/':
        sys.argv[1] += '/'
        
    if not os.path.isdir(os.path.dirname(sys.argv[3])):
        print "[e] Error: Directory \"%s\" does not exists\n" % sys.argv[3]
        sys.exit(-2)
        
    if not os.path.isdir(sys.argv[1]):
        print "[e] Error: \"%s\" is not a directory\n" % sys.argv[1]
        sys.exit(-3)
        
    print "[i] Origin: %s%s" % ( sys.argv[1] , sys.argv[2] )
    print "[i] Output file: %s\n" % sys.argv[3]
    
    merge(sys.argv[1],sys.argv[2], sys.argv[3])
    print ""
    sys.exit(0)