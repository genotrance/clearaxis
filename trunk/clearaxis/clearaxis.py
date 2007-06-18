import os
import re
import sys
import _winreg

# Common strings
ARAXIS_DIFF    = 'compare.exe'
CLEARCASE_DIFF = 'cleardiffmrg.exe'

# Potential matches
TEXT_FILE_DELTA_XCOMPARE = "(^text_file_delta\s+xcompare\s+)(\.\.\\\.\.\\\\bin\\\\cleardiffmrg\.exe)"
HTML_XCOMPARE            = "(^_html[2]*\s+xcompare\s+)(\.\.\\\.\.\\\\bin\\\\htmlmgr\.exe)"
XML_XCOMPARE             = "(^_xml[2]*\s+xcompare\s+)(\.\.\\\.\.\\\\bin\\\\cleardiffmrg\.exe)"
XML_XCOMPARE_7           = "(^_xml[2]*\s+xcompare\s+)(\.\.\\\.\.\\\\bin\\\\xmldiffmrg\.exe)"

# Error codes
INSUFFICIENT_ARGUMENTS        = 100
ARAXIS_NOT_INSTALLED          = 101
CLEARCASE_NOT_INSTALLED       = 102
CLEARCASE_MAP_FILE_MISSING    = 103

# Error strings
ERROR_STRINGS = {
                 INSUFFICIENT_ARGUMENTS        : 'Insufficient arguments provided',
                 ARAXIS_NOT_INSTALLED          : 'Araxis Merge is not installed',
                 CLEARCASE_NOT_INSTALLED       : 'Rational ClearCase is not installed',
                 CLEARCASE_MAP_FILE_MISSING    : 'ClearCase map file could not be found'
                 }

class Clearaxis:
    # Setup clearaxis
    def __init__(self):
        # Get Araxis path
        self.get_araxis_path()

        # Get ClearCase path
        self.get_clearcase_path()

        # Check dependencies
        self.check_dependencies()

        # Parse command line arguments
        self.parse_command_line()

        # Execute diff
        self.execute_diff()

    # Get Araxis path from the registry
    def get_araxis_path(self):
        path = self.get_registry_key(_winreg.HKEY_CLASSES_ROOT, 'CLSID\\{6bc05a94-8ec8-11d2-b346-0000e835aa2c}\\LocalServer32', None)
        self.araxis_path = re.sub(os.path.basename(path), '', path)

    # Get ClearCase path from the registry
    def get_clearcase_path(self):
        path = self.get_registry_key(_winreg.HKEY_LOCAL_MACHINE, 'Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\cleartool.exe', None)
        self.clearcase_path = re.sub('cleartool.exe', '', path)

    # Get a registry value
    def get_registry_key(self, HKEY, node, sub_node):
        try:
            key = _winreg.OpenKey(HKEY, node)
            value, temp = _winreg.QueryValueEx(key, sub_node)
            _winreg.CloseKey(key)
        except WindowsError:
            value = ''

        return value

    # Check that both Araxis and ClearCase are installed
    def check_dependencies(self):
        if self.clearcase_path == '':
            self.die(CLEARCASE_NOT_INSTALLED)
        elif self.araxis_path == '':
            self.die(ARAXIS_NOT_INSTALLED)

    # Parse command line options
    def parse_command_line(self):
        # Remove command from sys.argv
        self.clearaxis_path = os.path.abspath(sys.argv.pop(0))

        # If insufficient arguments, return
        if len(sys.argv) == 0:
            self.die(INSUFFICIENT_ARGUMENTS)

        # Check if a request to install or uninstall
        if sys.argv[0] == '-install':
            # Figure out what file types to support
            self.text_xcompare = True
            self.html_xcompare = False
            self.xml_xcompare = False
            for arg in sys.argv:
                if arg == '-html_xcompare':
                    self.html_xcompare = True
                elif arg == '-xml_xcompare':
                    self.xml_xcompare = True

            # Do the install
            self.install_clearaxis()
        elif sys.argv[0] == '-uninstall':
            # Restore map file
            self.uninstall_clearaxis()

        # Translate arguments as needed
        i = t = 0
        self.args = []
        while i < len(sys.argv):
            # Set title if provided
            if (sys.argv[i] == '-fname'):
                t += 1
                i += 1
                self.args.append('/title' + t.__str__() + ':"' + sys.argv[i] + '"')
            else:
                self.args.append('"' + sys.argv[i] + '"')

            i += 1

    # Execute the diff
    def execute_diff(self):
        # Run diff command depending on whether Araxis is installed
        if self.araxis_path != '':
            self.args.insert(0, ARAXIS_DIFF)
            self.args.append('/wait')
            os.spawnv(os.P_WAIT, self.araxis_path + ARAXIS_DIFF, self.args)
        elif self.clearcase_path != '':
            sys.argv.insert(0, CLEARCASE_DIFF)
            os.spawnv(os.P_WAIT, self.clearcase_path + CLEARCASE_DIFF, sys.argv)

    # Install clearaxis
    def install_clearaxis(self):
        self.get_map_files()
        self.backup_map_file()
        self.update_map_file()
        sys.exit(0)

    # Uninstall clearaxis
    def uninstall_clearaxis(self):
        self.get_map_files()
        self.restore_map_file()
        sys.exit(0)

    # Get the map file in ClearCase and check that it exists
    def get_map_files(self):
        self.map = self.clearcase_path + '..\lib\mgrs\map'
        self.map_bak = os.path.dirname(self.clearaxis_path) + '\map.bak'
        if not os.path.exists(self.map):
            self.die(CLEARCASE_MAP_FILE_MISSING)

    # Backup the map file to the clearaxis directory
    def backup_map_file(self):
        if not os.path.exists(self.map_bak):
            import shutil
            shutil.copyfile(self.map, self.map_bak)
            shutil.copystat(self.map, self.map_bak)

    # Restore the map file from the clearaxis directory
    def restore_map_file(self):
        if os.path.exists(self.map_bak):
            import shutil
            shutil.copyfile(self.map_bak, self.map)
            shutil.copystat(self.map_bak, self.map)
            os.remove(self.map_bak)

    # Update map file to include clearaxis
    def update_map_file(self):
        # Open map files
        mp = open(self.map, 'w')
        mb = open(self.map_bak, 'r')

        # Parse all the lines
        out = ''
        for line in mb:
            # Text xcompare
            if (self.text_xcompare):
                m = re.match(TEXT_FILE_DELTA_XCOMPARE, line)
                if m != None:
                    out += m.groups()[0] + self.clearaxis_path + "\n"
                    continue

            # Html xcompare
            if (self.html_xcompare):
                m = re.match(HTML_XCOMPARE, line)
                if m != None:
                    out += m.groups()[0] + self.clearaxis_path + "\n"
                    continue

            # Xml xcompare
            if (self.xml_xcompare):
                m = re.match(XML_XCOMPARE, line)
                if m != None:
                    out += m.groups()[0] + self.clearaxis_path + "\n"
                    continue
                m = re.match(XML_XCOMPARE_7, line)
                if m != None:
                    out += m.groups()[0] + self.clearaxis_path + "\n"
                    continue

            # Unrelated line, pass through
            out += line

        # Write updated map
        mp.write(out)

        # Close files
        mp.close()
        mb.close()

    # Error mapper
    def die(self, code):
        print ERROR_STRINGS[code]
        sys.exit(code)

if __name__ == '__main__':
    # Run clearaxis
    clearaxis = Clearaxis()