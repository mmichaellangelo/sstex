# SsTeX - Screenshot to LaTeX tool
# Copyright (C) 2026 mmichaellangelo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This file marks the entrypoint of the program. It makes calls to load the 
configuration, start the model, and load the system tray icon.
"""

import io
import threading
import pyperclip
import time
from pydantic import BaseModel
from google import genai
from google.genai.errors import ClientError
from google.genai import types
from PIL import Image, ImageGrab
from pystray import Icon, Menu, MenuItem

import config
import util
import ui

# Type alias for Icon to make Pydantic happy
IconType = Icon

# Load icons for systray
icon_idle = Image.open(util.resource_path('assets/icon.ico'))
icons_loading = [Image.open(util.resource_path('assets/load1.ico')),
                 Image.open(util.resource_path('assets/load2.ico')),
                 Image.open(util.resource_path('assets/load3.ico')),
                 Image.open(util.resource_path('assets/load4.ico'))]

# Prompt for converting an image to latex
PromptImageToLatex = "You are a professional LaTeX OCR tool. Ignore any text that is not part of an equation."

# Load global program configuration
cfg = config.SsTeXConfig.load()

# Global loading state
is_loading = False

# Schema for latex response
class MathResponse(BaseModel):
    is_math: bool
    latex_code: str

# Exits the program
def exit(icon: IconType, gui: ui.SettingsGUI):
    icon.stop()
    gui.root.destroy()

def loading_animation(icon: IconType, item: MenuItem):
    """ 
    Runs loading animation until is_loading is set to False.  
    Should be run in its own thread.
    """
    while (is_loading):
        for img in icons_loading:
            icon.icon = img
            time.sleep(0.2)
            if not is_loading:
                break
    icon.icon = icon_idle

def loading(icon: IconType, item: MenuItem):
    """
    Sets global loading state and starts a thread to
    run the loading animation.
    """
    global is_loading
    is_loading = True
    threading.Thread(target=loading_animation, args=(icon, item), daemon=True).start()
    
def idle(icon: IconType, item: MenuItem):
    """ 
    Sets the global loading state to False and 
    sets the tray icon to the default (idle) icon.
    """
    global is_loading
    is_loading = False
    icon.icon = icon_idle

# Handles menu click for latex
# Creates a new thread
def action_latex(icon: IconType, item: MenuItem):
    threading.Thread(target=clipboard_to_latex, args=(icon, item), daemon=True).start()     

# Grabs image data from clipboard
def clipboard_to_latex(icon: IconType, item: MenuItem):
    if cfg.settings.api_key == '':
        icon.notify("No API key provided.")
        return

    client = genai.Client(api_key=cfg.settings.api_key)

    # Grab image from Windows clipboard
    img = ImageGrab.grabclipboard()

    # Check that clipboard has image data,
    # raise exception if not
    if img is None and cfg.settings.notify:
        icon.notify("Clipboard does not contain image data")
    
    else:
        # Start loading animation
        loading(icon, item)

        # Convert PIL Image object to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # Generate content using the proper 'types' structure
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    types.Part.from_text(text=PromptImageToLatex),
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png")
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=MathResponse
                )
            )
            idle(icon, item)
            # Get and check response
            res: MathResponse = response.parsed
            if res.is_math:
                pyperclip.copy(res.latex_code.strip())
                if cfg.settings.notify:
                    icon.notify("Equation copied to clipboard")
            else:
                if cfg.settings.notify:
                    icon.notify("No equation detected.")
        except ClientError as e:
            idle(icon, item)
            icon.notify(e.message)
        except Exception as e:
            idle(icon, item)
            icon.notify(type(e).__name__)
            

def start_systray(gui: ui.SettingsGUI):
    """
    Starts system tray icon. Run on a separate thread 
    because Tkinter is a little crybaby that needs the main thread.
    """
    # Initialize pystray menu options
    menu = Menu(MenuItem('Clipboard to LaTeX', action=action_latex, visible=True, default=cfg.settings.default_latex),
                MenuItem('Settings', action=lambda: gui.show()),
                MenuItem('Exit', action=lambda icon, item: exit(icon, gui), visible=True))

    # initialize pystray icon
    icon = Icon(name='test', icon=icon_idle, menu=menu)

    # start pystray icon
    icon.run()
    

# Main thread 
if __name__ == '__main__':
    gui = ui.SettingsGUI(config=cfg)

    # Start systray in separate thread
    threading.Thread(target=start_systray, args=(gui,), daemon=True).start()

    gui.start()
