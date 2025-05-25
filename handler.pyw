import sys
import pyperclip
import os

# Ensure the script works even when launched from C:\Windows\System32
os.chdir(os.path.dirname(__file__))

if len(sys.argv) > 1:
    reservation_id = sys.argv[1]
    pyperclip.copy(reservation_id)
