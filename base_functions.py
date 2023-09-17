"""
created matt_dumont 
on: 17/09/23
"""


def close_google_dirve():
    raise NotImplementedError

def restart_google_drive():
    raise NotImplementedError

def get_avalible_shared_drives():
    raise NotImplementedError

def get_rclone_config(email_address):
    # to allow mulitple users
    raise NotImplementedError

def authenticate(email_address):
    raise NotImplementedError

def mount_drive(email_address, drive_name):
    raise NotImplementedError

def list_paths_mount():
    # todo basically prime start mount so that it's not super laggy when first flying
    raise NotImplementedError

def list_active_drive_mounts():
    raise NotImplementedError

def get_user_shortcode():
    raise NotImplementedError

def set_user_shortcode():
    # short code to prepend to the mount name (e.g. hm for home users), user defined
    raise NotImplementedError

