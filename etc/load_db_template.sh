#!/bin/bash
# Use this script to dump the live database and load it into your local vagrant
# I will drop the existing vagrant database and then load the dump and run migrations

# example utils/load_db.sh cms-crop wil_dev 

DEVOPS_DIR='YOUR DEVOPS PATH GOES HERE'
PROJECT_DIR='YOUR PROJECT ROOT GOES HERE'

[[ $# -gt 0 ]] || { 
    echo "Load a deployed DB in to your local vgrant. You can use to 'no-dump' options is you don't want to re-dump the DB. Usage: load_db viewpoint vagrant"; 
    exit 1; 
}

SRC_SITE=$1
NO_DUMP=$2
FNAME=$SRC_SITE.apps.pointnineseven.com_latest.dump



if [ "$NO_DUMP" == "no-dump" ]; then
    echo "No dump specified. Using $DEVOPS/backups/$FNAME if it exists."
else
    echo "Dumping database from $SRC_SITE"
    # DUMP THE LIVE DB TO DEVOPS_DIR/backups
    cd $DEVOPS_DIR
    ansible-playbook -i hosts.ini provisioning/backup.yml -l $SRC_SITE.apps.pointnineseven.com --ask-vault-pass
fi


# LOAD THE FILE 
echo "Loading $DEVOPS_DIR/backups/$FNAME"
cd $PROJECT_DIR
fab vagrant restore_db:$DEVOPS_DIR/backups/$FNAME




LIVE_SITE='ftmlive'
OUTFILE='dump.sql'