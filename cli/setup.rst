just documenting the requirements

Functions:
===========

1. add-user [email_address] [shortcode]
2. remove-user [email_address]
3. ls-users # include authenticated or not...
4. remove-all-users
5. change-shortcode [email_address] [shortcode]
6. authenticate-user [email_address]
7. set-mount-options [optioncode]  # note that people are expected to write bespoke options themselves
8. ls-pos-drives [email_address|shortcode]
9. ls-mnt-drives [email_address|shortcode] # arg is optional
10. mount-drive [email_address|shortcode] [drive_name]
11. unmount-drive [email_address|shortcode] [drive_name]
12. open-in-drive [path]
13. get-file-id [path] # todo print and copy to clipboard (and linux middle clipboard)
14. get-dfolder-link [path] # todo print and copy to clipboard (and linux middle clipboard)
15. help

#todo
add to autostart
closure options
