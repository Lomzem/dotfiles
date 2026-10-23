"""Laptop package configuration for decman 1.2.2."""

import decman

from source.applications import ApplicationsModule
from source.base import BaseModule
from source.browsers import BrowsersModule
from source.desktop import DesktopModule
from source.development import DevelopmentModule
from source.embedded import EmbeddedModule
from source.fonts import FontsModule
from source.services import ServicesModule
from source.shell import ShellModule
from source.t3code import T3CodeModule

decman.modules = [
    BaseModule(),
    DesktopModule(),
    FontsModule(),
    ShellModule(),
    DevelopmentModule(),
    T3CodeModule(),
    EmbeddedModule(),
    BrowsersModule(),
    ApplicationsModule(),
    ServicesModule(),
]

# Chezmoi owns dotfiles. Keep existing system files and service enablement intact.
decman.execution_order = ["pacman", "aur"]

if decman.pacman is None or decman.aur is None:
    raise decman.SourceError("The decman-pacman plugin is required.")
