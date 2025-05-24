import os
import traceback
import ctypes
from functools import partial
import win32con
import win32api
import win32gui
from win32gui import (
    CreateWindow, DestroyWindow, UpdateWindow, RegisterClass, WNDCLASS,
    LoadIcon, LoadImage, Shell_NotifyIcon, PostQuitMessage, GetModuleHandle,
    PumpMessages,
    NIF_ICON, NIF_MESSAGE, NIF_TIP, NIF_INFO, NIM_ADD, NIM_MODIFY, NIM_DELETE
)

NIN_BALLOONUSERCLICK = win32con.WM_USER + 5
user32 = ctypes.windll.user32

class WindowsBalloonTip:
    def __init__(self):
        self.callback = None

        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_USER + 20: self.OnTaskbarNotify,
            win32con.WM_TIMER: self.OnTimer,
        }
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbar"
        wc.lpfnWndProc = message_map
        self.classAtom = RegisterClass(wc)

    def ShowWindow(self, title, msg, timeout=8,
                   callback=None):
        self.callback = partial(callback, msg) if callback else None

        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        iconPathName = os.path.abspath('c2gFav.ico')
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, iconPathName,
                              win32con.IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            print("Failed to load icon:", e)
            traceback.print_exc()
            hicon = LoadIcon(0, win32con.IDI_APPLICATION)

        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)

        Shell_NotifyIcon(NIM_MODIFY,
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20,
                          hicon, "Balloon Title", msg, 200, title))

        user32.SetTimer(self.hwnd, 1, timeout * 1000, 0)

        PumpMessages()

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam == NIN_BALLOONUSERCLICK:
            if self.callback:
                self.callback()
            DestroyWindow(hwnd)
        return 0

    def OnTimer(self, hwnd, msg, wparam, lparam):
        user32.KillTimer(hwnd, wparam)
        DestroyWindow(hwnd)
        return 0

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)
        return 0
