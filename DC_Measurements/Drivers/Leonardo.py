import numpy as np
import ctypes


class LeonardoInitException(Exception):
    def __init__(self, errorcode):
        msg = f"Unable to initialize Leonardo board. Driver returned an error code: {errorcode}"
        super().__init__(msg)


class LeonardoReadException(Exception):
    def __init__(self, errorcode):
        msg = f"Unable to read data from Leonardo board. Driver returned an error code: {errorcode}"
        super().__init__(msg)


class Leonardo:
    def __init__(self, channels=8, n_samples=500, verbose=True):
        self.__N_CHANNELS = channels
        self.__verbose = verbose
        self.__points = n_samples

        # Load wrapper DLL functions
        dll = ctypes.WinDLL('Leonardo_wrapper.dll')

        self.InitBoard = dll.InitBoard
        self.InitBoard.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        self.InitBoard.restype = ctypes.c_uint

        self.PerformRead = dll.PerformRead
        self.PerformRead.argtypes = [ctypes.c_uint, ctypes.POINTER(ctypes.c_double), ctypes.c_uint]
        self.PerformRead.restype = ctypes.c_uint

        self.FreeBoard = dll.FreeBoard
        self.FreeBoard.argtypes = [ctypes.c_uint]

        # Perform initialization steps
        if self.__verbose:
            print('Initializing Leonardo...')
        nSamples = 16
        hDeviceC = ctypes.c_int()
        ret = self.InitBoard(hDeviceC, nSamples)
        if ret == 0:
            if self.__verbose:
                print('Leonardo init success')
            self.hDevice = hDeviceC.value
        else:
            raise LeonardoInitException(ret)

    def MeasureNow(self, channel):
        nSamples = self.__points
        buff = (ctypes.c_double * (self.__N_CHANNELS * nSamples))()
        ret = self.PerformRead(self.hDevice, buff, nSamples)
        if ret == 0:
            data_read = np.array(buff).reshape(-1, self.__N_CHANNELS)
            return np.average(data_read, 0)[channel]
        else:
            raise LeonardoReadException(ret)

    def MeasureMany(self):
        nSamples = self.__points
        buff = (ctypes.c_double * (self.__N_CHANNELS * nSamples))()
        ret = self.PerformRead(self.hDevice, buff, nSamples)
        if ret == 0:
            data_read = np.array(buff).reshape(-1, self.__N_CHANNELS)
            return data_read
        else:
            raise LeonardoReadException(ret)

    def __del__(self):
        self.FreeBoard(self.hDevice)


class DebugLeonardoMeasurer:
    def __init__(self, channels=8, n_samples=500, verbose=True):
        self.__channels = channels
        self.__n_samples = n_samples
        print('Leonardo DEBUG mode, no real measurement will be done')

    def MeasureNow(self, channel):
        return (np.random.rand(1)[0]) * 100

    def MeasureMany(self):
        return np.random.rand(self.__n_samples, self.__channels)
