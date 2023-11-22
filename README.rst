Google Drive for Linux
############################

this was built to support in house use, so it has not been fully tested with a range of distros/versions; however it is basically a python wrapper for the google api and Rclone (https://rclone.org/) so maybe don't despair for other use cases.

Note the use of the google drive logo in the app icon is for internal recognition only and is not intended to imply any affiliation with, support from, or endorsement by google.

There are 2 basic ways to use this:
1. a panel applet that will streamline mounting google drives from rclone. (e.g. Gui)
2. a command line tool that will allow you to mount google drives from rclone. (e.g. Cli)

.. contents:: Table of Contents
   :local:
   :depth: 3

Tested Distros
==================

Below is a non-exhaustive list of distros that this has been tested on. If you have tested this on a distro not listed below, please let me know so I can add it to the list.

* Xubuntu 22.04 (will likely work on all ubuntu based distros)

yep that's it sorry!


Linux Dependencies
====================

There are several linux packages that are required for this to work.  These can be installed with the following commands:

.. code-block:: bash

    sudo apt update
    sudo apt install grep
    sudo apt install rclone
    sudo apt install tmux

# todo check on fresh install

Installation Applet
======================

Applet python environment
---------------------------

* python 3.9+
* PyQt6 (pip install PyQt6)
* python-fire  (pip install fire)

The python environment and lgdrive can be installed with the following commands (conda):

.. code-block:: bash

    conda create -n google_drive --channel conda-forge python fire
    conda activate google_drive
    pip install PyQt6
    pip install git+https://github.com/Komanawa-Solutions-Ltd/google_drive_linux


Setting up auto start for the applet
--------------------------------------

The applet launch script can be created by:

.. code-block:: bash

    echo '#!'"$HOME/miniconda3/envs/google_drive/bin/python" >>~/.local/bin/lgdrive_gui.py
    echo "from lgdrive.gui import launch_panel_app" >>~/.local/bin/lgdrive_gui.py
    echo "if __name__ == '__main__':" >>~/.local/bin/lgdrive_gui.py
    echo "    launch_panel_app()" >>~/.local/bin/lgdrive_gui.py
    chmod +x ~/.local/bin/lgdrive_gui.py

Add the following to autostart:

.. code-block::
    ~/.local/bin/lgdrive_gui.py

Note that you may need to pass absolute paths if the .bashrc has not been sourced yet.


Installation Command line interface (CLI)
======================================

CLI python environment / install
-------------------------------------

* python 3.9+
* python-fire (pip install fire)

The python environment and lgdrive can be installed with the following commands (conda):

.. code-block:: bash

    conda create -n google_drive --channel conda-forge python fire
    conda activate google_drive
    pip install git+https://github.com/Komanawa-Solutions-Ltd/google_drive_linux


Make easy executable
-------------------------------------

To make the easy executable run the following command:

.. code-block:: bash

    echo '#!'"$HOME/miniconda3/envs/google_drive/bin/python" >>~/.local/bin/lgdrive
    # note you can substitute the path to the python interpreter for the above "$HOME/miniconda3/envs/google_drive/bin/python"

    wget -O - https://raw.githubusercontent.com/Komanawa-Solutions-Ltd/google_drive_linux/main/src/lgdrive/launch_cli.py >> ~/.local/bin/lgdrive
    chmod +x ~/.local/bin/lgdrive


Ensure that ~/.local/bin is in your path.  If it is not add the following to your ~/.bashrc:
# todo
To launch the CLI run the following command:

.. code-block:: bash

    lgdrive


CLI autostart
--------------

.. code-block::

    echo "lgdrive start_google_drive" >> ~/.bashrc


Method / Structure
=====================

The basic structure for this app/rclone wrapper is as follows:

file structure
------------------

All components are hosted in the mount dir: ~/google_mount_point

This directory holds:
1. a cache dir for the google api (~/google_mount_point/.cache)
2. a config dir for rclone (~/google_mount_point/.config) which contains:
    1. a master config file
    2. a config file for each user/email address, this is just used to save the team drive ids and is not used in the rclone mount
    3. a text file with rclone mount options to use (~/google_mount_point/.config/.mount_options)
    4. a text file with a list of shortcodes for each user/email address (~/google_mount_point/.config/.shortcodes)
    5. a text file that holds a list of the mounted drives (~/google_mount_point/.config/.mounted_drives) which is used for system startup
    6. a text file that holds the trayapp state (~/google_mount_point/.config/.trayapp_state) which is used for system startup
    7. a text file to hold the google client ID and secret (~/google_mount_point/.config/.google_client).
3. a mount dir for each mounted drive

Google client ID and secret
------------------------------

When you use rclone with Google drive in its default configuration you are using rclone's client_id. This is shared between all the rclone users. There is a global rate limit on the number of queries per second that each client_id can do set by Google. rclone already has a high quota and I will continue to make sure it is high enough by contacting Google.

It is strongly recommended to use your own client ID as the default rclone ID is heavily used. If you have multiple services running, it is recommended to use an API key for each service. The default Google quota is 10 transactions per second so it is recommended to stay under that number as if you use more than that, it will cause rclone to rate limit and make things slower.

For information on how to create a client ID and secret see: https://rclone.org/drive/#making-your-own-client-id


Definitions
------------------
* **user/email address** - the email address of the user (e.g. jojo@gmail.coms)
* **Shortcode** - a short code that is used to identify a user/email address (either user specified or email_address.split('@')[0])
* **Mount_name/drive** - the name of the directory where the google drive will be mounted and the name of the drive. This is defined as "{short_code}@{drive_name}" (e.g. 'jojo@My_Drive') note spaces are replaced with underscores
* **raw_drive_name** - the name of the google drive as held in google (e.g. 'My Drive')

Permissions/config management
--------------------------------

The app is designed to allow multiple simultaneous google drives/users to be mounted. To do this, the app:

1. creates/updates a master config file (~/google_mount_point/.config/.master_config) that holds a rclone config for each user/email address with the mount name being the email address.  This master config file is only edited by the app to add/remove users and to list the available drives for each user.  This config is also used to mount the drives via rclone and the --drive-server-side-across-configs flag and {source},team_drive={drive_id}:
2. there is a config file for each user/email address (~/google_mount_point/.config/.{email_address}) that holds the rclone config for that user/email address. This file is frequently re-generated by the app to ensure that all drives are available to be mounted.  Note that this config file only holds data for the mounts, it is not used for mounting and does not have any permissions. the remote name is the mount name "{short_code}@{drive_name}" (e.g. 'jojo@My_Drive')
3. when a drive is mounted a new tmux session is created with the name "*gd@{shortcode}@{drive_name}" (e.g. '*gd@jojo@My_Drive') and the mount is run in that session.  This allows multiple drives to be mounted simultaneously and allows the user to investigate any issues with the mount.  The * is used to ensure that the tmux session appears at the top of the tmux ls list so that it does not make tmux harder to use.

The permissions for all of the config files are set to 600 so that only the user can read/write to them.  This is done to ensure that the user can not accidentally expose their google drive to other users on the system.  That being said these files are not encrypted (as per normal Rclone config files) so if you are worried about someone getting access to your files you should encrypt your drive (e.g. whole disk encryption).


Usage
==================

Panel Applet
------------------

The panel applet is meant to be a lightweight way to mount google drives.  It is designed to be used with the following workflow:

1. Launch the applet (or have it launch on startup) --> see installation
2. Add a user/email address and shortcode
    1. The shortcode is used to identify the user/email address in the applet and in the file manager, ideally keep it short and memorable.  The mounted drive names will be "{short_code}@{drive_name}" (e.g. 'jojo@My_Drive')
    2. The applet will then have rclone authenticate the user/email address and list the available drives
3. Add a drive --> email address --> Add/Remove drives for []
    1. This will open a qt window that will list the available drives for the user/email address and allow you to select the drives to mount/unmount
    2. The applet will keep track of these drives and mount them on startup
4. That's it your drives will now be mounted and you can access them in your file manager

There are some additional functionalities
1. you can set Rclone mount options for your drives --> Set Rclone options
    1. This will open a qt window that will allow you to set the rclone mount options for the drive
    2. There are currently only two default options that can be set this way: "default" and "light", these are defined in the applet code.  you are also welcome to set your own options by modifying the google_mount_point/.config/.mount_options file
    3. The applet will keep track of these options and use them when mounting the drive
    4. You can set the google client ID and secret for the applet to use --> see Google client ID and secret for more information.
2. There is "Drive path support" which launches a qt window that lets you:
    1. Get the google object ID from your file.
    2. Open the file's folder in google drive (launches your browser)
    3. Copy the path to the path's folder (or the path if it is a directory) to your clipboard
    4. This window can be modified to add additional functionality --> see Extending path support


Command line interface
------------------------

The command line interface is a python fire wrapper for the LGDrive class.  It is designed to be used with the following workflow.  For more information using python fire see: https://github.com/google/python-fire

Importantly the a -h flag following the command will give you more information about the command and its arguments.

1. start LGDrive --> lgdrive start_google_drive  (or add this to auto start)
2. add a user/email address --> lgdrive add_user [email_address] [shortcode]
    1. The shortcode is used to identify the user/email address in the applet and in the file manager, ideally keep it short and memorable.  The mounted drive names will be "{short_code}@{drive_name}" (e.g. 'jojo@My_Drive')
    2. The CLI will then have rclone authenticate the user/email address and list the available drives
    3. Note the local arg
3. list available drives --> ls_pos_drives [email|shortcode]
4. mount a drive --> lgdrive mount_drive [drive_name]
    1. This will open a qt window that will list the available drives for the user/email address and allow you to select the drives to mount/unmount
    2. The applet will keep track of these drives and mount them on startup
5. close LGDrive --> lgdrive close_google_drive
    1. this will close all of the tmux sessions and unmount all of the drives, but the listed drives will be saved and will be mounted on lgdrive start_google_drive

Extending path support
========================

The panel app has a 'Drive Path Support' option that allows you to copy and or open files in Google Drive
based on the path of the file in the local file system.  This is done by leveraging rclone lsjson and getting the google ID.

There could be merits in extending the options available in this window to allow for more complex path support related to your use case.  If you want to do this you are able to pass a custom Gpath object to the app.  This object must be a subclass of gui.gpath_support_gui.Gpath.  You will need to override the "add_buttons" method to allow for the creation of new buttons/feature in the window.

Possible Issues
==================

In the past I have had problems with rclone/google and IPv6. If you are having issues with rclone/google you may want to try disabling IPv6 on your system.  This can be done by:

.. code-block:: bash

    # from: https://linuxconfig.org/how-to-disable-ipv6-address-on-ubuntu-20-04-lts-focal-fossa
    # in /etc/default/grub
    # FROM:
    # GRUB_CMDLINE_LINUX_DEFAULT=""
    # TO:
    # GRUB_CMDLINE_LINUX_DEFAULT="ipv6.disable=1"  (space delim)
    # sudo update-grub

Possible Improvements
======================

This is a space for me to keep track of possible improvements to the app.  If you have any suggestions please feel free to open an issue on the github page.

* add a refresh mount option (e.g. via rclone rc vfs/refresh)


Contributing
==================

If you would like to contribute to this project please feel free to fork the repo and submit a pull request.  If you have any questions or issues please feel free to open an issue on the github page. If you have any suggestions for improvements please open an issue on the github page. I obviously can't promise that I will implement them but I will try to take them into consideration.

Distro Specific Notes
=======================

This is a place holder


