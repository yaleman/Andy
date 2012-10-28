tar c data/* > backups/`date +%Y-%m-%d`-data.tar
bzip2 -z backups/`date +%Y-%m-%d`-data.tar
