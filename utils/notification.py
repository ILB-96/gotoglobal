import os
import traceback
import ctypes
from functools import partial
import win32con
from win32gui import (
    CreateWindow, DestroyWindow, UpdateWindow, RegisterClass, WNDCLASS,
    LoadIcon, LoadImage, Shell_NotifyIcon, PostQuitMessage, GetModuleHandle,
    PumpMessages,
    NIF_ICON, NIF_MESSAGE, NIF_TIP, NIF_INFO, NIM_ADD, NIM_MODIFY, NIM_DELETE
)

NIN_BALLOONUSERCLICK = win32con.WM_USER + 5
user32 = ctypes.windll.user32


class WindowsBalloonTip:
    _classAtom = None

    def __init__(self):
        self.hinst = GetModuleHandle(None)
        self.class_name = "PythonTaskbar"
        if not WindowsBalloonTip._classAtom:
            wc = WNDCLASS()
            wc.hInstance = self.hinst
            wc.lpszClassName = self.class_name
            wc.lpfnWndProc = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_USER + 20: self.OnTaskbarNotify,
                win32con.WM_TIMER: self.OnTimer,
            }
            WindowsBalloonTip._classAtom = RegisterClass(wc)
            
    def ShowWindow(self, title, msg, timeout=8, callback=None):
        self.callback = partial(callback, msg) if callback else None

        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(
            WindowsBalloonTip._classAtom, "Taskbar", style,
            0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
            0, 0, self.hinst, None
        )
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

        # Add the icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)

        # Show the balloon
        Shell_NotifyIcon(NIM_MODIFY,
                         (self.hwnd, 0, NIF_INFO, win32con.WM_USER + 20,
                          hicon, "Balloon Title", msg, 200, title))

        # Set timeout
        user32.SetTimer(self.hwnd, 1, timeout * 1000, 0)

        # Start message loop
        PumpMessages()

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam == NIN_BALLOONUSERCLICK:
            if self.callback:
                self.callback()
            DestroyWindow(hwnd)
        return 0

    def OnTimer(self, hwnd, msg, wparam, lparam):
        if wparam == 1:
            user32.KillTimer(hwnd, 1)
            user32.SetTimer(hwnd, 2, 3000, 0)
        elif wparam == 2:
            user32.KillTimer(hwnd, 2)
            DestroyWindow(hwnd)
        return 0

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        try:
            Shell_NotifyIcon(NIM_DELETE, (self.hwnd, 0))
        except Exception as e:
            pass
        PostQuitMessage(0)
        return 0
