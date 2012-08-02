This project also provides tools for decrypting msgstored files and to merge many msgstore database files into a single one

## Spanish post @ Security By Default
http://www.securitybydefault.com/2012/05/whatsapp-forensics.html

**IMPORTANT:** The path of msgstore.db and wa.db has been changed to the directory "databases/" inside the project root.


## Getting the source

    ~$ git clone git://github.com/sch3m4/wforensic.git
    Cloning into 'wforensic'...
    remote: Counting objects: 288, done.
    remote: Compressing objects: 100% (222/222), done.
    remote: Total 288 (delta 82), reused 221 (delta 50)
    Receiving objects: 100% (288/288), 987.14 KiB | 229 KiB/s, done.
    Resolving deltas: 100% (82/82), done.
    ~$

## Retrieving msgstore.db and wa.db files

Although there are many ways to get the needed files msgstore.db and wa.db (the last one is not really required), you can use the example application from PyADB project available here: https://github.com/sch3m4/pyadb
So once it is installed, you can continue as follows:

    ~/pyadb/example$ python whatsapp.py 
        [+] Using PyADB version 0.1.0
        [+] Verifying ADB path... OK
        [+] ADB Version: 1.0.29
        
        [+] Restarting ADB server...
        [+] Detecting devices... OK
            0: XXXXXXXXXXXX
        
        [+] Using "XXXXXXXXXXXX" as target device
        [+] Looking for 'su' binary:  /system/xbin/su
        [+] Checking if 'su' binary can give root access:
            - Yes
        
        [+] Copying Whatsapp data folder
            - Local destination [/home/sch3m4/pyadb/example]: 
        
        [+] Creating remote tar file: /sdcard/whatsapp_JKsBgtryAa.tar
            - Command: /system/xbin/su -c 'tar -c /data/data/com.whatsapp -f /sdcard/whatsapp_JKsBgtryAa.tar'
        
        [+] Retrieving remote file: /sdcard/whatsapp_JKsBgtryAa.tar
        [+] Removing remote file: /sdcard/whatsapp_JKsBgtryAa.tar
        
        [+] Remote Whatsapp files from device memory are now locally accessible at "/home/sch3m4/pyadb/example/databases/whatsapp_JKsBgtryAa.tar"
        
        [+] Looking for 'tar' binary... /system/xbin/tar
        
        [+] Creating remote tar file: /sdcard/whatsapp_VFeCdqTSCg.tar
            + Command: /system/xbin/tar -c /sdcard/WhatsApp -f /sdcard/whatsapp_VFeCdqTSCg.tar
        
        [+] Remote tar file created: /sdcard/whatsapp_VFeCdqTSCg.tar
            - Local destination [/home/sch3m4/pyadb/example]: 
         
        [+] Retrieving remote file: /sdcard/whatsapp_VFeCdqTSCg.tar...
        
        [+] WhatsApp SDcard folder is now available in tar file: /home/sch3m4/pyadb/example/whatsapp_VFeCdqTSCg.tar
        
        ~/pyadb/example$

**IMPORTANT:** This application example does not belongs to WForensic project, may be in the future?

Once you have exported the needed files, you'll need to change the files & folder owner and untar the files:

    ~/pyadb/example$ tar xf whatsapp_VFeCdqTSCg.tar
    ~/pyadb/example$ sudo chown -R sch3m4:sch3m4 sdcard/
    ~/pyadb/example$ sudo chown -R sch3m4:sch3m4 databases/
    ~/pyadb/example$ tar xf databases/whatsapp_JKsBgtryAa.tar
    ~/pyadb/example$ sudo chown -R sch3m4:sch3m4 data/
    ~/pyadb/example$ sudo chmod -R 755 sdcard/ data/

And you'll get the msgstore & wa.db files at:

    ~/pyadb/example$ ls -l sdcard/WhatsApp/Databases/ data/data/com.whatsapp/databases/
    data/data/com.whatsapp/databases/:
    total 1732
    -rwxr-xr-x 1 sch3m4 sch3m4 1740800 jul 30 13:32 msgstore.db
    -rwxr-xr-x 1 sch3m4 sch3m4   26624 jul 30 13:32 wa.db
    
    sdcard/WhatsApp/Databases/:
    total 13060
    -rwxr-xr-x 1 sch3m4 sch3m4 1575952 jul 22 04:00 msgstore-2012-07-23.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1613840 jul 24 04:00 msgstore-2012-07-24.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1640464 jul 24 17:22 msgstore-2012-07-25.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1653776 jul 25 04:00 msgstore-2012-07-27.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1680400 jul 27 04:00 msgstore-2012-07-28.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1697808 jul 28 04:00 msgstore-2012-07-29.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1723408 jul 29 04:00 msgstore-2012-07-30.1.db.crypt
    -rwxr-xr-x 1 sch3m4 sch3m4 1736720 jul 30 04:00 msgstore.db.crypt

## Decrypting many msgstore files

Following the above instructions, the next step is to decrypt all the *.crypt files. To do that, follow the next steps:

    $ cd ~/wforensic/tools/
    ~/wforensic/tools$ python decrypt.py -d ~/pyadb/example/sdcard/WhatsApp/Databases/ ./plain/
    
        #######################################
        #      WhatsApp Forensic Tool  0.3    #
        #-------------------------------------#
        #  Decrypts encrypted msgstore files  #
        #   This tool is part of WForensic    #
        # https://github.com/sch3m4/wforensic #
        #######################################
        
    [i] Setting AES key....... OK
    
    [+] Decrypting msgstore-2012-07-25.1.db.crypt (msgstore-2012-07-25.1.db) -> 1640464 Bytes 
        + 6246 Messages from 32 contacts
    
    [+] Decrypting msgstore-2012-07-28.1.db.crypt (msgstore-2012-07-28.1.db) -> 1680400 Bytes 
        + 6435 Messages from 32 contacts
    
    [+] Decrypting msgstore-2012-07-23.1.db.crypt (msgstore-2012-07-23.1.db) -> 1575952 Bytes 
        + 6042 Messages from 30 contacts
    
    [+] Decrypting msgstore-2012-07-24.1.db.crypt (msgstore-2012-07-24.1.db) -> 1613840 Bytes 
        + 6218 Messages from 31 contacts
    
    [+] Decrypting msgstore.db.crypt (msgstore.db) -> 1736720 Bytes 
        + 6681 Messages from 33 contacts
    
    [+] Decrypting msgstore-2012-07-27.1.db.crypt (msgstore-2012-07-27.1.db) -> 1653776 Bytes 
        + 6289 Messages from 32 contacts
    
    [+] Decrypting msgstore-2012-07-29.1.db.crypt (msgstore-2012-07-29.1.db) -> 1697808 Bytes 
        + 6516 Messages from 32 contacts
    
    [+] Decrypting msgstore-2012-07-30.1.db.crypt (msgstore-2012-07-30.1.db) -> 1723408 Bytes 
        + 6607 Messages from 32 contacts
    
    [+] Done!
    
    ~/wforensic/tools$

## Merging all msgstore files into a single one

At this step, you'll get many msgstore files, so to merge them you can use another tool located at wforensic/tools called 'merge.py':

    ~/wforensic/tools$ cp ~/pyadb/example/data/data/com.whatsapp/databases/msgstore.db plain/msgstore1.db
    ~/wforensic/tools$ python merge.py plain/ msgstore* ./msgstore.db
    
        #######################################
        #  WhatsApp Msgstore Merge Tool 0.2b  #
        #-------------------------------------#
        # Merges WhatsApp message files into  #
        #           a single one.             #
        #   This tool is part of WForensic    #
        # https://github.com/sch3m4/wforensic #
        #######################################
        
    [i] Origin: plain/msgstore*
    [i] Output file: ./msgstore.db
    
    + Merging: msgstore.db 
    + Merging: msgstore-2012-07-29.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore-2012-07-28.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore-2012-07-24.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore-2012-07-23.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore-2012-07-27.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore1.db  (Merged 0 contacts and 11 messages) 
    + Merging: msgstore-2012-07-30.1.db  (Merged 0 contacts and 0 messages) 
    + Merging: msgstore-2012-07-25.1.db  (Merged 0 contacts and 0 messages)
    
    ~/wforensic/tools$

At this point, the final msgstore.db file is located at "~/wforensic/tools/msgstore.db"

## Environment schema

The last point, is to move/copy/link the needed files (remember, wa.db is not really needed but useful) to the correct path:

    ~/wforensic/tools$ cp msgstore.db ../databases
    ~/wforensic/tools$ cp ~/pyadb/example/data/data/com.whatsapp/databases/wa.db ../databases/
    ~/wforensic$ cd .. && ls -1
    CHANGELOG
    databases
    LICENSE
    README
    tools
    wforensic
    ~/wforensic$ ls -1 databases/
    msgstore.db
    wa.db
    ~/wforensic$

## Running DJango

    ~/wforensic$ python wforensic/manage.py runserver
    Validating models...
    
    0 errors found
    Django version 1.4, using settings 'wforensic.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.
