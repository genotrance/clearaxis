What is Clearaxis
-----------------

Clearaxis is a simple application that integrates the Araxis Merge diff
tool into ClearCase. Compare.exe that ships with Araxis works for
dynamic views but fails on snapshot views. Clearaxis just converts the
command line arguments from ClearCase into something that Compare.exe
can use.

How this works is already documented on Araxis.com at:
  http://www.araxis.com/merge/scm_integration.html

Clearaxis only solves the problem of packaging a tool that anybody can
easily download and install.

Clearaxis is written in Python. It is packaged using Py2Exe and
installed using NSIS.

Installation
------------

The Windows installer copies the executable files, source code and the
README to a directory of your choice. It then modifies the ClearCase map
file to point to Clearaxis for the file types selected during install.

The installer does not create any start menu shortcuts since Clearaxis
is to be invoked within ClearCase.

Clearaxis requires that both ClearCase and Araxis are installed on the
system in order to work.

Uninstallation
--------------

Clearaxis can be uninstalled from "Add or Remove Programs" in the
Control Panel.

License
-------

Clearaxis is being released under the GPL. The source code is included
in the installer.

Contact
-------

Contact genosha@genotrance.com for any questions regarding this program.

Links
-----

Clearaxis website
http://blog.genotrance.com/applications/clearaxis

Python
http://www.python.org

Py2Exe
http://www.py2exe.org

NSIS
http://nsis.sf.net