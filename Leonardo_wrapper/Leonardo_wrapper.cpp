#pragma comment (lib, "RshUniDriver.lib")
#include "stdafx.h"
#include "Leonardo_wrapper.h"

//constants
#define BOARD_NAME "LEONARDO2PCI"
#define DEVICE_ID 1
#define SAMPLE_FREQ 102400.
#define CHANNEL_NUMBER 8
#define IBSIZE 5120


//
//FUNCTION: InitBoard
//Performs Leonardo board initialization and returns a handle to device into an argument
//Return value: 0 if succeeded, error code otherwise.
//
LEONARDO_WRAPPER_API unsigned int __stdcall InitBoard(unsigned int * pOutHandle, unsigned int ibSize)
{
	unsigned int st, deviceHandle;
	URshInitDMA  p = {0};
	st = UniDriverGetDeviceHandle(BOARD_NAME, &deviceHandle);
	if (st != RSH_API_SUCCESS)
        {
			*pOutHandle = -1;
			return st;
        }

    st = UniDriverIsCapable(deviceHandle, RSH_CAPS_SOFT_PGATHERING_IS_AVAILABLE);
    if (st != RSH_API_SUCCESS)
    {
		*pOutHandle = -2;
		return st;
    }

    st = UniDriverConnect(deviceHandle, DEVICE_ID, RSH_CONNECT_MODE_BASE);
	if (st != RSH_API_SUCCESS)
        {
			*pOutHandle = -3;
			return st;
        }

    p.type = rshInitDMA;
	p.startType = URshStartTypeProgram;
	p.dmaMode = URshInitDmaDmaModePersistent;
	p.bufferSize = ibSize;
	p.frequency = SAMPLE_FREQ;
	for(int i=0;i<CHANNEL_NUMBER;++i)
	{
		p.channels[i].control = URshChanControlUsed;
		p.channels[i].gain = 1;
	}

	st = UniDriverInit(deviceHandle, RSH_INIT_MODE_INIT, &p);
	if (st != RSH_API_SUCCESS)
    {
		*pOutHandle = -4;
		return st;
    }

	st = UniDriverStart(deviceHandle);
	if (st != RSH_API_SUCCESS)
	{
		*pOutHandle = -5;
		return st;
    }
	*pOutHandle = deviceHandle;
	return RSH_API_SUCCESS;
}

//FUNCTION: PerformRead
//Reads one data block and returns it into double array
//A double array must be preallocated to (8*ibSize) bytes.
//Return value: 0 if succeeded, error code otherwise.
//
LEONARDO_WRAPPER_API unsigned int __stdcall PerformRead(unsigned int deviceHandle, double *pBuffer, unsigned int ibSize)
{
	unsigned int st;
	unsigned int waitTime = 100000;

	st = UniDriverLVGetUInt(deviceHandle, RSH_GET_WAIT_BUFFER_READY_EVENT, &waitTime );
    if (st != RSH_API_SUCCESS)
	{
		return st;
	}

	unsigned int received = 0;
	st = UniDriverLVGetDataDouble (deviceHandle,RSH_DATA_MODE_NO_FLAGS,CHANNEL_NUMBER*ibSize,&received,pBuffer);
	return st;
}

LEONARDO_WRAPPER_API void __stdcall FreeBoard(unsigned int deviceHandle)
{
	UniDriverStop(deviceHandle);
	UniDriverCloseDeviceHandle(deviceHandle);
}

int _tmain(void)
{
	return 0;
}
