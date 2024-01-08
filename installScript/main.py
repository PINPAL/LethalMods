import os
import sys
import winreg
import vdf
import ctypes
import logging
import subprocess
from shutil import which
# from git import Repo

logging.basicConfig(filename="logfile.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)

# function to print a nice header
def printHeader(headerText):
    print("\n======================================================================================")
    print(headerText)
    print("======================================================================================")

# function to print an error message
def printMessage(messageContent, isError):
    ICON_ERROR = 0x30
    ICON_INFO = 0x40
    if (isError):
        messageHeader = "Error!"
        messageContent = messageContent + "\n\n Tell Josh the script is broken!"
        icon = ICON_ERROR
    else:
        messageHeader = "Success!"
        icon = ICON_INFO
    ctypes.windll.user32.MessageBoxW(0, messageContent, messageHeader, 0x0 | icon)
    # crash the program
    if (isError):
        sys.exit()

def findInstallPath():
    printHeader("Searching for Steam Install Path")
    # read the InstallPath key from the registry
    try:
        #connecting to key in registry
        theRegistry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        registryLocation = winreg.OpenKey(theRegistry,r"SOFTWARE\WOW6432Node\Valve\Steam")
        steamInstallPathArray = winreg.QueryValueEx(registryLocation,"InstallPath")
        steamInstallPath = steamInstallPathArray[0]
    except:
        printMessage("Steam Install Path not found in registry", True)
    # print the value
    print("Steam is installed at: " + steamInstallPath + "\n")

    lethalCompanySteamId = "1966720"

    # Read the libraryfolders.vdf file
    printHeader("Searching for Lethal Company in Steam Libraries")
    try:
        vdfFile = vdf.parse(open(steamInstallPath + r"\steamapps\libraryfolders.vdf"))
    except:
        printMessage("Could not find libraryfolders.vdf", True)
    # loop through the dictionary of dictionaries to libraries
    for libraryKey, libraryValues in vdfFile["libraryfolders"].items():
        # print the path value of the library
        print("Searching for Lethal Company in: " + libraryValues["path"])
        # loop through the apps dictionary and find the lethal company steam id
        for appKey, appValue in libraryValues["apps"].items():
            if appKey == lethalCompanySteamId:
                lethalCompanyPath = libraryValues["path"] + r"\steamapps\common\Lethal Company"
                print("--> Found Lethal Company in " + libraryValues["path"])
                break
        else:
            continue

    printHeader("Checking Installation is Valid")
    print("Checking in: " + lethalCompanyPath)
    # Check if Lethal Company.exe exists
    if not (os.path.isfile(lethalCompanyPath + r"\Lethal Company.exe")):
        printMessage("Lethal Company.exe not found in \n" + lethalCompanyPath, True) 
    else:
        return lethalCompanyPath

# def cloneRepo():
#     printHeader("Cloning Repo")
#     # clone the repo
#     try:
#         Repo.clone_from("https://github.com/PINPAL/LethalMods", lethalCompanyPath + r"\LethalMods")
#     except:
#         printMessage("Failed to clone repo", True)

def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

def isGitInstalled():
    if (which("git") is not None) :
        print("Git is installed")
    else :
        print("Git is not installed")
        # install it automatically
        printHeader("Installing Git\nPlease wait...")
        installGitCommand = run("winget install --id Git.Git -e --source winget")
        if installGitCommand.returncode != 0:
            errorlog = str(installGitCommand.stdout, 'utf-8')
            printMessage("Failed to install Git" + errorlog, True)
        else:
            printHeader("Git Installed Successfully")



# main program
# ==============================
try:
    lethalCompanyPath = findInstallPath()
    printMessage("Lethal Company.exe found in \n" + lethalCompanyPath, False)
    isGitInstalled()
    input()
    sys.exit()
except:
    logging.exception("Something awful happened!")