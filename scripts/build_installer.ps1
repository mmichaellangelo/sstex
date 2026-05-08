# SsTeX - Screenshot to LaTeX tool
# Copyright (C) 2026 mmichaellangelo
# 
# This script runs InnoSetup to build the program's installer.
# ISCC.exe must be added to PATH before running this script
#
# InnoSetup v6 was used in development, I do not know if other
# versions will work.

cp .\THIRD-PARTY-NOTICES.txt .\assets\
ISCC.exe setup\setup.iss