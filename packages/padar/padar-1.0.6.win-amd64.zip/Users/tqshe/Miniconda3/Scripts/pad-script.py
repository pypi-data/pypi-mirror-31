#!C:\Users\tqshe\Miniconda3\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'padar==1.0.6','console_scripts','pad'
__requires__ = 'padar==1.0.6'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('padar==1.0.6', 'console_scripts', 'pad')()
    )
