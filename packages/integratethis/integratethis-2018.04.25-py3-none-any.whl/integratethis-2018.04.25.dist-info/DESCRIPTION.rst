This program integrates arbitrary commands to various tools.
For example, you can add a program named "filetags" to the "Send to"
folder of the context menu of the Windows File explorer via
    integratethis filetags

The integration method used differs from tool to tool. For the Windows Explorer,
a batch file is placed within the AppData\Roaming folder in case of additional
parameters have to be added to the command and a lnk file to it is created in
the "Send to" folder so that you can use the command from the context menu of
the Windows Exporer. If no additional parameters are required, a lnk file to the
command itself is placed in the "Send to" folder. For details, please look at
the source code or read the help info for the --into parameter.

You can overwrite pre-configured parameters using the command line options.

- Target group: users who are able to use command line tools
- Hosted and documented on github: https://github.com/novoid/integratethis


