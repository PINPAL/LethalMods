import customtkinter
from PIL import Image

# Images
checkmark_off = customtkinter.CTkImage(dark_image=Image.open("assets/checkmark_off.png"),size=(24, 24))
checkmark_on = customtkinter.CTkImage(dark_image=Image.open("assets/checkmark_on.png"),size=(24, 24))

# Function called when "Install" button is pressed
def startInstallation():
    print("Installation started")
    # Hide Install Button
    installButton.grid_forget()
    # Show Progress Bar
    progressBar.grid(row=0, column=0, padx=0, pady=20, sticky="ewns")
    footerSeperator.grid_forget()
    # Update Progress Bar
    updateProgressCheck(0) 
    addConsoleText("Starting..", isHeader=True)

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
robotoFont = customtkinter.CTkFont(family="Roboto", size=16, weight="normal")
robotoFontMedium = customtkinter.CTkFont(family="Roboto-Medium", size=16, weight="bold")
robotoFontBold = customtkinter.CTkFont(family="Roboto-Bold", size=20, weight="bold")
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
        progressCheckLabel.configure(font=robotoFont)
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
title = customtkinter.CTkLabel(titleFrame, text="Lethal Company Mod Installer", font=robotoFontBold, text_color=consoleTextHeader)
title.grid(row=0, column=0, padx=0, pady=8)
# Add SubtitleFrame to TitleFrame
subtitleFrame = customtkinter.CTkFrame(titleFrame, fg_color="transparent")
subtitleFrame.grid(row=1, column=0, padx=0, pady=0, sticky="ewns")
subtitleFrame.columnconfigure(1, weight=1)
# Add Subtitle to Subtitle Frame
subtitle = customtkinter.CTkLabel(subtitleFrame, text="Created by PINPAL", font=robotoFont, text_color=consoleTextNormal)
subtitle.grid(row=0, column=0, padx=0, pady=0, sticky="w")
# Add Seperator to Subtitle Frame
subtitleSeperator = customtkinter.CTkLabel(subtitleFrame, text="-", font=robotoFontMedium, text_color=consoleTextNormal)
subtitleSeperator.grid(row=0, column=1, padx=4, pady=0, sticky="nesw")
# Add Link to Subtitle Frame
subtitleLink = customtkinter.CTkLabel(subtitleFrame, text="pinpal.github.io", font=robotoFont, text_color=sidebarBackground)
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
installButton.configure(font=robotoFont)
installButton.configure(fg_color="transparent")
installButton.configure(border_width=2)
installButton.configure(border_color=buttonBorder)
installButton.configure(hover_color=sidebarBackground)
installButton.configure(command=startInstallation)

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

# function to update progress bar
def updateProgressBar(progress:int):
    progressBar.set(progress)

# function to update progress check
def updateProgressCheck(index:int):
    progressChecks[index].configure(image=checkmark_on)
    progressChecks[index].configure(text_color="white")
    progressChecks[index].configure(font=robotoFontMedium)


# Run App
addConsoleText("Ready to Start..")
addConsoleText("Awaiting User Input..")

App.mainloop()
