import customtkinter
import os
import winreg
import vdf
import zipfile
import shutil
import subprocess
import threading
from urllib.request import urlopen
from PIL import Image

# python -m PyInstaller main.py -y --onefile -n LC-Mod-Installer --add-data "assets;assets" --icon assets/favicon.ico --noconsole --version-file version.txt
# todo:
# - add progress bar to sidebar
# - add sounds
# - add antialiasing to GUI (maybe?)

# Images
checkmark_off = customtkinter.CTkImage(dark_image=Image.open("assets/checkmark_off.png"),size=(24, 24))
checkmark_on = customtkinter.CTkImage(dark_image=Image.open("assets/checkmark_on.png"),size=(24, 24))

totalProgress = 0

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def findInstallPath():
    addConsoleText("Searching for Steam Install Path", isHeader=True)
    # read the InstallPath key from the registry
    try:
        #connecting to key in registry
        theRegistry = winreg.ConnectRegistry(None,winreg.HKEY_LOCAL_MACHINE)
        registryLocation = winreg.OpenKey(theRegistry,r"SOFTWARE\WOW6432Node\Valve\Steam")
        steamInstallPathArray = winreg.QueryValueEx(registryLocation,"InstallPath")
        steamInstallPath = steamInstallPathArray[0]
    except:
        addConsoleText("Steam Install Path not found in registry", type="error")
    # print the value
    addConsoleText("Steam is installed at: " + steamInstallPath + "\n")
    updateProgressCheck(0)

    lethalCompanySteamId = "1966720"

    # Read the libraryfolders.vdf file
    addConsoleText("Searching for Lethal Company in Steam Libraries", isHeader=True)
    try:
        vdfFile = vdf.parse(open(steamInstallPath + r"\steamapps\libraryfolders.vdf"))
    except:
        addConsoleText("Could not find libraryfolders.vdf", type="error")
    # loop through the dictionary of dictionaries to libraries
    for libraryKey, libraryValues in vdfFile["libraryfolders"].items():
        # print the path value of the library
        addConsoleText("Searching for Lethal Company in: " + libraryValues["path"])
        # loop through the apps dictionary and find the lethal company steam id
        for appKey, appValue in libraryValues["apps"].items():
            if appKey == lethalCompanySteamId:
                lethalCompanyPath = libraryValues["path"] + r"\steamapps\common\Lethal Company"
                addConsoleText("--> Found Lethal Company in " + libraryValues["path"])
                updateProgressCheck(1)
                break
        else:
            continue

    addConsoleText("Checking Installation is Valid", isHeader=True)
    addConsoleText("Checking in: " + lethalCompanyPath)
    # Check if Lethal Company.exe exists
    if not (os.path.isfile(lethalCompanyPath + r"\Lethal Company.exe")):
        addConsoleText("Lethal Company.exe not found in \n" + lethalCompanyPath, type="error")
    else:
        addConsoleText("Lethal Company.exe found in \n" + lethalCompanyPath)
        updateProgressCheck(2)
        return lethalCompanyPath

def download(url: str, filename: str):
    readBytes = 0
    chunkSize = 1024
    # Open the URL address.
    with urlopen(url) as r:
        totalSize = 0
        previousSize = 0
        try:
            totalSize = int(r.info()["Content-Length"])
            addConsoleText("Total: " + str(round(totalSize / 1024 / 1024, 2)) + "MB")
        except:
            addConsoleText("Could not get Content-Length", type="error")
            addConsoleText("Downloading anyway..")
        with open(filename, "ab") as f:
            while True:
                # Read a piece of the file we are downloading.
                chunk = r.read(chunkSize)
                # If the result is `None`, that means data is not
                # downloaded yet. Just keep waiting.
                if chunk is None:
                    continue
                # If the result is an empty `bytes` instance, then
                # the file is complete.
                elif chunk == b"":
                    break
                # Write into the local file the downloaded chunk.
                f.write(chunk)
                readBytes += chunkSize
                # Check if the last update was more than 500KB ago
                if (previousSize + 512000) < readBytes :
                    # Tell the window how many bytes we have received.
                    updateDownloadProgress(readBytes, totalSize)
                    previousSize = readBytes

# Function called when "Install" button is pressed
# ================================================
# main program
# ================================================
def startInstallation():
    installFailed = False
    # Hide Install Button
    installButton.grid_forget()
    # Show Progress Bar
    progressBar.grid(row=0, column=0, padx=0, pady=20, sticky="ewns")
    footerSeperator.grid_forget()
    # Update Progress Bar
    addConsoleText("Chcecking if Lethal Company is running", isHeader=True)
    if (process_exists("Lethal Company.exe")):
        addConsoleText("Lethal Company is running, please close the game and try again", type="error")
        return
    else:
        addConsoleText("Lethal Company is not running")
        addConsoleText("Starting Installation")
    lethalCompanyPath = findInstallPath()

    addConsoleText("Downloading Mods", isHeader=True)
    addConsoleText("Please wait, this may take a while..")
    pathToZipFile = lethalCompanyPath + r"\LethalMods.zip"
    download("https://codeload.github.com/PINPAL/LethalMods/zip/refs/heads/main", pathToZipFile)
    if (os.path.isfile(pathToZipFile)):
        addConsoleText("Mods downloaded to: " + pathToZipFile)
    else:
        addConsoleText("Failed to download Mods", type="error")
        installFailed = True

    addConsoleText("Extracting Mods", isHeader=True)
    # extract the zip file
    try:
        with zipfile.ZipFile(pathToZipFile, 'r') as zip_ref:
            zip_ref.extractall(lethalCompanyPath + r"\LethalMods")
    except:
        addConsoleText("Failed to extract Mods", type="error")
        installFailed = True
    updateProgressCheck(3)
    addConsoleText("Deleting Old Mods", isHeader=True)
    # delete BepInEx folder
    try:
        shutil.rmtree(lethalCompanyPath + r"\BepInEx")
        addConsoleText("BepInEx deleted")
    except:
        addConsoleText("BepInEx Folder not found", type="error")
    # delete doorstop_config.ini
    try:
        os.remove(lethalCompanyPath + r"\doorstop_config.ini")
        addConsoleText("doorstop_config.ini deleted")
    except:
        addConsoleText("doorstop_config.ini not found", type="error")
    # delete winhttp.dll
    try:
        os.remove(lethalCompanyPath + r"\winhttp.dll")
        addConsoleText("winhttp.dll deleted")
    except:
        addConsoleText("winhttp.dll not found", type="error")

    updateProgressCheck(4)
    addConsoleText("Moving new LethalMods", isHeader=True)
    try:
        # move the new BepInEx folder
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\BepInEx", lethalCompanyPath)
        addConsoleText("BepInEx moved")
        # move the new doorstop_config.ini
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\doorstop_config.ini", lethalCompanyPath)
        addConsoleText("doorstop_config.ini moved")
        # move the new winhttp.dll
        shutil.move(lethalCompanyPath + r"\LethalMods\LethalMods-main\LethalCompany\winhttp.dll", lethalCompanyPath)
        addConsoleText("winhttp.dll moved")
    except:
        addConsoleText("Failed to move files", type="error")
        installFailed = True

    updateProgressCheck(5)
    addConsoleText("Cleaning up Installer Files", isHeader=True)
    try:
        shutil.rmtree(lethalCompanyPath + r"/LethalMods")
        addConsoleText("LethalMods deleted")
    except:
        addConsoleText("Failed to delete extracted LethalMods", type="error")
    try:
        os.remove(lethalCompanyPath + r"/LethalMods.zip")
        addConsoleText("LethalMods.zip deleted") 
    except:
        addConsoleText("Failed to delete LethalMods.zip", type="error")
    updateProgressCheck(6)

    # finished
    updateProgressCheck(7)
    if installFailed:
        addConsoleText("Installation Failed", isHeader=True, type="error")
        updateProgressBar(100)
        progressBar.configure(progress_color=consoleTextError)
    else:
        addConsoleText("LethalMods installed successfully", isHeader=True, type="success")
        updateProgressBar(100)

# color variables
mainBackground = "#1a1b26"
consoleBackground = "#31323c"
consoleTextNormal = "#a4a8ac"
consoleTextHeader = "#ffffff"
consoleTextError = "#c95862"
consoleTextSuccess = "#9dcc67"
sidebarBackground = "#5cabed"
sidebarForeground = "#a3e0f7"
buttonBorder = "#53545c"

# Define App
App = customtkinter.CTk()
App.iconbitmap("assets/favicon.ico")
App.title("Lethal Company Mod Installer")
App._set_appearance_mode("dark")
App.geometry("960x540")
App.minsize(960, 540)
App.grid_rowconfigure(0, weight=1) # full height 
App.grid_columnconfigure(1, weight=1) # make main content fill width

# font variables
fontNormal  = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=15, weight="normal")
fontMedium  = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=16, weight="bold")
fontBold    = customtkinter.CTkFont(family="Arial Rounded MT Bold", size=20, weight="bold")
consoleFont = customtkinter.CTkFont(family="Consolas", size=12, weight="normal")

# Define Sidebar
sidebar = customtkinter.CTkFrame(App, fg_color=sidebarBackground, corner_radius=0)
sidebar.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
sidebar.rowconfigure(0, weight=1)
    
# Add Content to Sidebar
progressChecks = []
progressChecksText = ["Finding Steam Path", "Finding Lethal Company", "Checking Installation", "Downloading Mods", "Extracting Mods", "Installing Mods", "Cleaning Up", "Complete"]
for progressCheck in progressChecksText:
        sidebarIndex = progressChecksText.index(progressCheck)
        progressCheckLabel = customtkinter.CTkLabel(sidebar)
        progressCheckLabel.configure(image=checkmark_off)
        progressCheckLabel.configure(compound="left")
        progressCheckLabel.configure(padx=12)
        progressCheckLabel.configure(text=progressCheck)
        progressCheckLabel.configure(font=fontNormal)
        progressCheckLabel.configure(fg_color="transparent")
        progressCheckLabel.configure(text_color=sidebarForeground)
        progressCheckLabel.configure(corner_radius=0)
        progressChecks.append(progressCheckLabel)
        progressChecks[sidebarIndex].grid(row=sidebarIndex+1, column=0, padx=24, pady=16, sticky="wns")
# Add Seperator to Sidebar
sidebarSeperator = customtkinter.CTkLabel(sidebar, text=" ")
sidebarSeperator.grid(row=sidebarIndex+2, column=0, padx=24, pady=0, sticky="ewns")
sidebar.rowconfigure(sidebarIndex+2, weight=1)

# Define Main Content
mainContent = customtkinter.CTkFrame(App, fg_color=mainBackground, corner_radius=0)
mainContent.grid(row=0, column=1, padx=0, pady=0, sticky="ewns")
mainContent.grid_columnconfigure(0, weight=1)
mainContent.grid_rowconfigure(1, weight=1)

# Add Header to Main Content
mainContentHeader = customtkinter.CTkFrame(mainContent, fg_color="transparent")
mainContentHeader.grid(row=0, column=0, padx=24, pady=18, sticky="ewns")
mainContentHeader.columnconfigure(1, weight=1)
# Add Frame for Title and Subtitle
titleFrame = customtkinter.CTkFrame(mainContentHeader, fg_color="transparent")
titleFrame.grid(row=0, column=0, padx=0, pady=0)
# Add Title to TitleFrame
title = customtkinter.CTkLabel(titleFrame, text="Lethal Company Mod Installer", font=fontBold, text_color=consoleTextHeader)
title.grid(row=0, column=0, padx=0, pady=8)
# Add SubtitleFrame to TitleFrame
subtitleFrame = customtkinter.CTkFrame(titleFrame, fg_color="transparent")
subtitleFrame.grid(row=1, column=0, padx=0, pady=0, sticky="ewns")
subtitleFrame.columnconfigure(1, weight=1)
# Add Subtitle to Subtitle Frame
subtitle = customtkinter.CTkLabel(subtitleFrame, text="Created by PINPAL", font=fontNormal, text_color=consoleTextNormal)
subtitle.grid(row=0, column=0, padx=0, pady=0, sticky="w")
# Add Seperator to Subtitle Frame
subtitleSeperator = customtkinter.CTkLabel(subtitleFrame, text="-", font=fontMedium, text_color=consoleTextNormal)
subtitleSeperator.grid(row=0, column=1, padx=4, pady=0, sticky="nesw")
# Add Link to Subtitle Frame
subtitleLink = customtkinter.CTkLabel(subtitleFrame, text="pinpal.github.io", font=fontNormal, text_color=sidebarBackground)
subtitleLink.grid(row=0, column=2, padx=0, pady=0, sticky="e")
# Add Logo to Main Content Header
logo = customtkinter.CTkLabel(mainContentHeader, text="")
logo.configure(image=customtkinter.CTkImage(dark_image=Image.open("assets/favicon.ico"),size=(48, 48)))
logo.grid(row=0, column=2, padx=0, pady=0, sticky="e")

# Add "console" to Main Content
console = customtkinter.CTkScrollableFrame(mainContent)
console.configure(fg_color=consoleBackground)
console.configure(scrollbar_fg_color=consoleBackground)
console.configure(scrollbar_button_color=consoleBackground)
console.grid(row=1, column=0, padx=24, pady=2, sticky="ewns")
console.columnconfigure(0, weight=1)

# Add Footer to Main Content
mainContentFooter = customtkinter.CTkFrame(mainContent)
mainContentFooter.configure(fg_color="transparent")
mainContentFooter.grid(row=2, column=0, padx=24, pady=4, sticky="ewns")
mainContentFooter.grid_columnconfigure(0, weight=1)
# Add Progress Bar to Footer 
progressBar = customtkinter.CTkProgressBar(mainContentFooter)
progressBar.configure(mode="determinate")
progressBar.configure(height=12)
progressBar.configure(determinate_speed=0)
progressBar.configure(fg_color=consoleBackground)
progressBar.configure(progress_color=sidebarBackground)
progressBar.stop()
progressBar.set(0)
# Add Seperator to Footer
footerSeperator = customtkinter.CTkLabel(mainContentFooter)
footerSeperator.configure(text=" ")
footerSeperator.grid(row=0, column=0, padx=4, pady=0, sticky="ewns")
# Add Button to Footer
installButton = customtkinter.CTkButton(mainContentFooter)
installButton.grid(row=0, column=2, padx=0, pady=12, sticky="wns")
installButton.configure(text="Start Installation")
installButton.configure(font=fontNormal)
installButton.configure(fg_color="transparent")
installButton.configure(border_width=2)
installButton.configure(border_color=buttonBorder)
installButton.configure(hover_color=sidebarBackground)
installButton.configure(command=threading.Thread(target=startInstallation).start)

# Function to add text to console
global currentConsoleRow
currentConsoleRow = 0
def addConsoleText(text:str, isHeader: bool = False, type: {"normal", "error", "success"} = "normal"):
    global currentConsoleRow
    # Handle Custom Colors for Type
    textColor = consoleTextNormal
    if (type == "normal" and isHeader):
        textColor = consoleTextHeader
    elif (type == "error"):
        textColor = consoleTextError
    elif (type == "success"):
        textColor = consoleTextSuccess
    # Create Label
    consoleText = customtkinter.CTkLabel(console)
    consoleText.configure(text=text)
    consoleText.configure(font=consoleFont)
    consoleText.configure(height=20)
    consoleText.configure(fg_color="transparent")
    consoleText.configure(text_color=textColor)
    consoleText.configure(justify="left")
    consoleText.configure(corner_radius=0)
    # Handle Seperator for Header
    if (isHeader):
        consoleTextSeperator = customtkinter.CTkFrame(console)
        consoleTextSeperator.configure(fg_color=textColor)
        consoleTextSeperator.configure(height=2)
        consoleTextSeperator.grid(row=currentConsoleRow, column=0, padx=8, pady=4, sticky="ew")
        currentConsoleRow += 1
    # Add Label to Console 
    consoleText.grid(row=currentConsoleRow, column=0, padx=8, pady=0, sticky="w")
    currentConsoleRow += 1
    # Handle Seperator for Header
    if (isHeader):
        consoleTextSeperator = customtkinter.CTkFrame(console)
        consoleTextSeperator.configure(fg_color=textColor)
        consoleTextSeperator.configure(height=2)
        consoleTextSeperator.grid(row=currentConsoleRow, column=0, padx=8, pady=4, sticky="ew")
        currentConsoleRow += 1
    # Scroll to Bottom
    console._parent_canvas.yview_moveto(1.0)

# function to update progress bar
def updateProgressBar(progress:int):
    progressBar.set(progress / 100)
def updateDownloadProgress(readBytes:float, totalSize:float):
    global progressChecksText
    global totalProgress
    currentMB = round(readBytes / 1024 / 1024, 2)
    currentMBFormatted = "{:.2f}".format(currentMB)
    if (currentMB < 10):
        currentMBFormatted = "0" + currentMBFormatted
    if (totalSize > 1):
        progress = round(readBytes / totalSize * 100)
        totalMB = "{:.2f}".format(round(totalSize / 1024 / 1024, 2))
        addConsoleText("Downloading: " + currentMBFormatted + " / " + str(totalMB) + " MB  |  " + str(progress) + "%)")
        # update progress bar
        downloadProgressAsPortionOfTotalProgress = round(((1 / (len(progressChecksText) )) * 100) * (progress / 100))
        updateProgressBar(totalProgress + downloadProgressAsPortionOfTotalProgress)
    else:
        addConsoleText("Downloading: " + currentMBFormatted + " MB of unknown size")

# function to update progress check
def updateProgressCheck(index:int):
    progressChecks[index].configure(image=checkmark_on)
    progressChecks[index].configure(text_color="white")
    progressChecks[index].configure(font=fontMedium)

    # update progress bar
    global totalProgress
    global progressChecksText
    totalProgress += round((1 / (len(progressChecksText))) * 100)
    updateProgressBar(totalProgress)


# Run App
addConsoleText("Ready to Start..")
addConsoleText("Awaiting User Input..")

App.mainloop()
