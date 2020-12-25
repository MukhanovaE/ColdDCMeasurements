#ifdef LEONARDO_WRAPPER_EXPORTS
#define LEONARDO_WRAPPER_API __declspec(dllexport)
#else
#define LEONARDO_WRAPPER_API __declspec(dllimport)
#endif

LEONARDO_WRAPPER_API unsigned int __stdcall InitBoard(unsigned int * pOutHandle, unsigned int ibSize);
LEONARDO_WRAPPER_API unsigned int __stdcall PerformRead(unsigned int deviceHandle, double *pBuffer, unsigned int ibSize);
LEONARDO_WRAPPER_API void __stdcall FreeBoard(unsigned int deviceHandle);

