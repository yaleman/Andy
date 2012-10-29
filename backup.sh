tar c data/* > backups/`date +%Y-%m-%d`-data.tar
rm backups/`date +%Y-%m-%d`-data.tar.bz2
bzip2 -z backups/`date +%Y-%m-%d`-data.tar
