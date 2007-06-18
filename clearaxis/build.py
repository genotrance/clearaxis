import defines
import distutils.core
import getopt
import glob
import os.path
import py2exe
import re
import sys
import types
import version
import _winreg

# Class to build application
class build:
    # Constructor
    def __init__(self):
        self.setup()
        self.get_dependencies()
        [p, u, n] = self.parse_arguments()
        
        if p: self.build_executable()
        if u: self.upx_compress()
        if n: 
            self.delete_older_packages()
            self.build_nsis_package()
        
    # Setup the build
    def setup(self):
        # Initialize
        self.py2exe = {}
        
        # Create manifest
        manifest = """
            <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <assembly xmlns="urn:schemas-microsoft-com:asm.v1"
            manifestVersion="1.0">
            <assemblyIdentity
                version="0.64.1.0"
                processorArchitecture="x86"
                name="Controls"
                type="win32"
            />
            <description>ClearAxis</description>
            <dependency>
                <dependentAssembly>
                    <assemblyIdentity
                        type="win32"
                        name="Microsoft.Windows.Common-Controls"
                        version="6.0.0.0"
                        processorArchitecture="X86"
                        publicKeyToken="6595b64144ccf1df"
                        language="*"
                    />
                </dependentAssembly>
            </dependency>
            </assembly>
        """
        
        # GUI executable
        self.py2exe['windows'] = [{
                         "script"          : "clearaxis.py",
                         "other_resources" : [(24, 1, manifest)]
                         }]
        
        # Py2Exe options
        self.py2exe['options'] = {
                        "py2exe": {
                                   "packages" : ["encodings"],
                                   "optimize" : 2,
                                   "compressed" : 1,
                                   "bundle_files" : 2
                                   }
                       }
        
        # Name of zip file to generate
        self.py2exe['zipfile'] = None
        
        # Specify py2exe as a command line option
        sys.argv.append('py2exe')
        
    # Parse arguments
    def parse_arguments(self):
        help = """
%s:
  build.py [%s]
  -p    %s
  -u    %s
  -n    %s""" % (
                 defines.USAGE,
                 defines.OPTIONS,
                 defines.BUILD_EXECUTABLE_USING_PY2EXE,
                 defines.COMPRESS_USING_UPX,
                 defines.CREATE_NSIS_PACKAGE
                 )
    
        # Set defaults
        if len(sys.argv) == 2:
            p = u = n = True
        else:
            p = u = n = False
            try:
                opts, args = getopt.getopt(sys.argv[1:], 'punh')
            except getopt.GetoptError:
                print help
                sys.exit(defines.ERROR_GETOPT)
    
            for o, a in opts:
                if o == '-p': p = True
                if o == '-u': u = True
                if o == '-n': n = True
                if o == '-h':
                    print help
                    sys.exit(defines.ERROR_HELP)
            
        return [p, u, n]
            
    # Get build dependencies
    def get_dependencies(self):
        self.upx = os.path.expandvars('${systemroot}\\upx.exe')
        if not os.path.exists(self.upx):
            self.error_out(defines.UPX_NOT_AVAILABLE)
            
        self.nsis = self.get_registry_key(_winreg.HKEY_LOCAL_MACHINE,
                                          'SOFTWARE\\NSIS',
                                          '') + os.path.sep + 'makensis.exe'
        if self.nsis == os.path.sep + 'makensis.exe' or not os.path.exists(self.nsis):
            self.error_out(defines.NSIS_NOT_AVAILABLE)
            
    # Execute Py2Exe to generate executables
    def build_executable(self):
        command = 'distutils.core.setup('
        for key in self.py2exe:
            if type(self.py2exe[key]) is types.StringType:
                command += key + ' = "' + self.py2exe[key] + '", '
            else:
                command += key + ' = ' + self.py2exe[key].__str__() + ', '
        command = command[:-2] + ')'
        eval(command)
        os.system('rd build /s /q')
        
    # Compressing executables with UPX
    def upx_compress(self):
        os.system('""' + self.upx + '" --best "dist' + os.path.sep + '*')
    
    # Delete older packages
    def delete_older_packages(self):
        appname = version.APPNAME.lower()
        files = glob.glob(appname + 'setup-*.exe')
        for file in files:
            print file
            os.remove(file)
    
    # Package with NSIS
    def build_nsis_package(self):
        appname = version.APPNAME.lower()
        lines = open(appname + 'setup.nsi').read()
        o = open('temp.nsi', 'w')
        o.write(re.sub('#VERSION#', version.APPVERSION, lines))
        o.close()
        os.system('""' + self.nsis + '" temp.nsi"')
        os.remove('temp.nsi')
        
    # Die on error
    def error_out(self, text):
        print text + '. ' + defines.BUILD_FAILED
        sys.exit(defines.ERROR_BUILD_FAILED)

    # Get data from the registry
    def get_registry_key(self, database, key, value):
        try:
            key = _winreg.OpenKey(database, key)
            data, temp = _winreg.QueryValueEx(key, value)
            _winreg.CloseKey(key)
        except WindowsError:
            data = ''
            
        return data
    
if __name__ == '__main__':
    build()