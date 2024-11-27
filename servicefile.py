import os
import sys
import servicemanager
import win32event
import win32service
import win32serviceutil

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Esp32updatedservice"
    _svc_display_name_ = "ESP 32 updated Service"
    _svc_description_ = "This is a ESP32 python service that runs my script in the background."
    _svc_type_ = win32service.SERVICE_AUTO_START

    # Use one of the following.
    # _svc_account_ = "username"
    # _svc_account_ = "username@activedirectorydomain.com"
    _svc_account_ = "desktop-09f2feq\\prabhakaran"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        self.main()

    def main(self):
        # Add your Python script code here
        print('Starting Service...')
        import ESP32
        ESP32.main()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyService)
