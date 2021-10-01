# raspi-backup
## Description:
Fast and easy way to create or restore a backup of your Raspberry Pi OS in using tar and pigz.

## Table of contents:
- [History](#history)
- [Main features](#main-features)
- [Installation](#installation)

## History:  
Switching operating systems usually involved a fresh install followed by all the necessary adaptions until a usable state was restored.  
  
Recommended use is to have a base system on the microSD card from which you can backup or restore the system on an USB attached storage.  
**raspi-backup can also create backups from the running system to a mounted network storage or other drive.**  
Note: The restore process cannot be done within a running system.  
  
  
## Main features:  
General  
- Backups/restores files necessary to maintain the current state  
- Checks if necessary apps are installed  
- Verbose on the files processed  
Backup  
- Excluding some non-essential folders to save space  
- Excluding target base directory and mounted drives  
- Multicore compression using tar and pigz  
Restore  
- Deleting target contents to avoid conflicts with existing files  
- Restore system to the state of the backup  
  
**Note: As the backup covers only files and no partitions, the target has to be, mounted as in the state of the backup.**  
Example: Second (root) partition to /mnt and first partition (boot) to /mnt/boot  
It is advised to additionally check fstab before reboot.  
  
## Installation:  
### Prequisits  
- Python3  
- python3-apt  
- tar  
- pigz (not pre-installed in default Raspberry Pi OS image)  
  
### Usage:  
Download raspi-backup.py.  
Make the file executable: `chmod +x raspi-backup.py`  
Run the script: `sudo raspi-backup.py <action> <source> <target>`  
**_Note_: Elevated privledges are needed for deleting target and copying files.**  
  
## Future plans:  
There are currently no future plans for the script.  
Note: The scripts was written and tested with Raspberry Pi OS but should work with other OS as well.  
