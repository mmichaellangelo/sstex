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
This file provides a class used for configuring SsTeX.  
It provides methods to load, save, and modify the system's configuration.
"""

import os
import json
from pathlib import Path
from pydantic import BaseModel, Field, PrivateAttr
from typing import Annotated
from threading import Lock

class ConfigSettings(BaseModel):
    # Gemini API key
    api_key: Annotated[str, Field(default='', description="Gemini API key"), 'HIDDEN']
    # Allow notifications
    notify: bool = Field(default=True, description="Enable notifications")
    # Left-click icon to parse equation
    default_latex: bool = Field(default=True, description="Left-click icon action (requires restart)")

class SsTeXConfig(BaseModel):
    """ SsTex Program Configuration """
    
    # Allow pydantic arbitrary types
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    # Mutex lock
    _lock: Lock = PrivateAttr(default_factory=lambda: Lock())

    # Path to config file. Don't save in config file itself.
    config_filepath: Path = Field(default_factory=lambda: SsTeXConfig.get_default_path(), exclude=True)
    
    # Configuration settings
    settings: ConfigSettings = Field(default_factory=ConfigSettings)

    @staticmethod
    def get_default_path():
        """ Get the path to the program's config file """
        # Points to C:\Users\Username\AppData\Roaming\YourAppName
        app_data = os.getenv('APPDATA')
        config_dir = Path(app_data) / 'SsTeX'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'

    @classmethod
    def load(cls) -> SsTeXConfig:
        """ 
        Factory method for getting SsTeX config
        from the configuration file. 
        Returns a fresh SsTeXConfig instance if 
        config file doesn't exist or can't be read.
        """
        path = cls.get_default_path()
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return cls.model_validate(data)
        except:
            new_cfg = cls()
            new_cfg.save()
            return new_cfg
        
    def save(self):
        """ Saves current configuration to file. """
        with self._lock, open(self.config_filepath, 'w') as f:
            json.dump(self.model_dump(mode='json'), f, indent=4)
