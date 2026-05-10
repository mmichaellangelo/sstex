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
This file holds the Settings GUI, written with Tkinter.
"""

import tkinter as tk

import config
import ctypes
import webbrowser
from PIL import Image, ImageTk
import util

# Set app ID for custom taskbar icon
myappid = 'mmichaellangelo.sstex.v1' 
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class SettingsGUI:
    root: tk.Tk
    icon: Image
    cfg: config.SsTeXConfig

    def _pack_settings(self):
        for name, info in config.ConfigSettings.model_fields.items():
            frame = tk.Frame(self.root)
            frame.pack(fill='x', padx=5, pady=5)
            label_text = info.description or name.replace("_", " ").title()
            tk.Label(master=frame, text=label_text).pack(side='left')
            current_value = getattr(self.cfg.settings, name)

            if info.annotation is bool:
                var = tk.BooleanVar(value=current_value)
                widget = tk.Checkbutton(master=frame, variable=var)

                def update(*args, n=name, v=var):
                    setattr(self.cfg.settings, n, v.get())
                    self.cfg.save()

                var.trace_add('write', update)
                widget.pack(side='right')
            else:
                var = tk.StringVar(value=current_value)
                widget = tk.Entry(master=frame, textvariable=var)
                if 'HIDDEN' in info.metadata:
                    widget.config(show='*')

                def update(n=name, v=var):
                    setattr(self.cfg.settings, n, v.get())
                    self.cfg.save()

                widget.pack(side='left')
                save_button = tk.Button(master=frame, text="Save", command=update)
                save_button.pack(side='right')

    def __init__(self, config: config.SsTeXConfig):
        self.cfg = config

        # Initialize and configure window
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title('SsTeX Settings')
        self.root.config(padx=20, pady=20)
        self.root.resizable(False, False)
        self.root.attributes('-toolwindow', True) # Only show 'X'
        self.icon = ImageTk.PhotoImage(Image.open(util.resource_path('assets/icon.ico')))
        self.root.iconphoto(True, self.icon)
        # Hide window when "X" is clicked
        self.root.protocol("WM_DELETE_WINDOW", self.hide)

        # Pack Gemini API key link
        label_link_apikey = tk.Label(self.root, text="Get a Gemini API key", cursor='hand2', fg='blue')
        label_link_apikey.pack()
        label_link_apikey.bind('<Button-1>', lambda e: webbrowser.open('https://ai.google.dev/gemini-api/docs/api-key'))

        # Link and pack system settings to UI layout
        self._pack_settings()

        # Pack 3rd party notices link
        label_link_thirdparty = tk.Label(self.root, text="Third Party Licenses", cursor='hand2', fg='blue')
        label_link_thirdparty.pack()
        label_link_thirdparty.bind('<Button-1>', lambda e: webbrowser.open(util.resource_path('assets/THIRD-PARTY-NOTICES.txt')))

    def start(self):
        """
        Starts the GUI, hidden.  
        Blocking -- run on main thread.
        """
        self.root.bind("<<ToggleSettings>>", func=self.show)
        self.root.mainloop()

    def show(self, event=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        self.root.withdraw()
