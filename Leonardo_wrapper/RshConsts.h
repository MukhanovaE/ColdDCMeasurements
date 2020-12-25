/*!
 * \copyright JSC "Rudnev-Shilyaev"
 * 
 * \file RshConsts.h
 * \date 17.09.2015
 * \version 1.0 [SDK 2.00]
 * 
 * \~english
 * \brief
 * This file contains definitions of constants that are common to all RSH SDK code.
 *
 * \~russian
 * \brief
 * В данном файле содержатся определения и константы общие для всего RSH SDK. 
 *  
 */

#ifndef __RSH_CONSTS_H__
#define __RSH_CONSTS_H__


#define _RSH_GROUP_TYPE_DELIMITER(value)   ( 0xadc00000 | ( value << 12 ) )
#define	_RSH_GROUP_TYPE_BASE(value)        ( _RSH_GROUP_TYPE_DELIMITER(0x1) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_POINTER(value)     ( _RSH_GROUP_TYPE_DELIMITER(0x2) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_BUFFER(value)      ( _RSH_GROUP_TYPE_DELIMITER(0x3) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_INIT(value)        ( _RSH_GROUP_TYPE_DELIMITER(0x4) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_STUFF(value)       ( _RSH_GROUP_TYPE_DELIMITER(0x5) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_INTERNAL(value)    ( _RSH_GROUP_TYPE_DELIMITER(0x6) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_DPA(value)         ( _RSH_GROUP_TYPE_DELIMITER(0x7) | ( value & 0xfff ) )
#define	_RSH_GROUP_TYPE_LAB(value)         ( _RSH_GROUP_TYPE_DELIMITER(0x8) | ( value & 0xfff ) )


/*!
* 
* \~english
* \brief
* Data types identifiers.
* 
* Every derived from RshBaseType class has its own unique ID,
* which is used to identify it.
* 
* \~russian
* \brief
* Идентификаторы типов данных.
* 
* Каждый класс, унаследованный от RshBaseType, имеет
* свой уникальный идентификатор, который позволяет
* определить тип данных, когда это необходимо.
*
*/
typedef enum {
	rshTypeUndefined = 0x0,
	rshU8 = _RSH_GROUP_TYPE_BASE(0x1), //0xadc01000
	rshS8 = _RSH_GROUP_TYPE_BASE(0x2),
	rshU16 = _RSH_GROUP_TYPE_BASE(0x3),
	rshS16 = _RSH_GROUP_TYPE_BASE(0x4),
	rshU32 = _RSH_GROUP_TYPE_BASE(0x5),
	rshS32 = _RSH_GROUP_TYPE_BASE(0x6),
	rshU64 = _RSH_GROUP_TYPE_BASE(0x7),
	rshS64 = _RSH_GROUP_TYPE_BASE(0x8),
	rshFloat = _RSH_GROUP_TYPE_BASE(0x9),
	rshDouble = _RSH_GROUP_TYPE_BASE(0xA),
	rshBool  = _RSH_GROUP_TYPE_BASE(0xB),

	rshVoidP = _RSH_GROUP_TYPE_POINTER(0x1), //0xadc02000
	rshU8P = _RSH_GROUP_TYPE_POINTER(0x2),
	rshS8P  = _RSH_GROUP_TYPE_POINTER(0x3),
	rshU16P = _RSH_GROUP_TYPE_POINTER(0x4),
	rshS16P = _RSH_GROUP_TYPE_POINTER(0x5),
	rshU32P = _RSH_GROUP_TYPE_POINTER(0x6),
	rshS32P = _RSH_GROUP_TYPE_POINTER(0x7),
	rshU64P = _RSH_GROUP_TYPE_POINTER(0x8),
	rshS64P = _RSH_GROUP_TYPE_POINTER(0x9),
	rshFloatP = _RSH_GROUP_TYPE_POINTER(0xA),
	rshDoubleP = _RSH_GROUP_TYPE_POINTER(0xB),
	rshBoolP = _RSH_GROUP_TYPE_POINTER(0xC),
	rshU8PP = _RSH_GROUP_TYPE_POINTER(0xD),
	rshS8PP = _RSH_GROUP_TYPE_POINTER(0xE),
	rshU16PP = _RSH_GROUP_TYPE_POINTER(0xF),
	rshS16PP = _RSH_GROUP_TYPE_POINTER(0x10),
	rshU32PP = _RSH_GROUP_TYPE_POINTER(0x11),
	rshS32PP = _RSH_GROUP_TYPE_POINTER(0x12),
	rshU64PP = _RSH_GROUP_TYPE_POINTER(0x13),
	rshS64PP = _RSH_GROUP_TYPE_POINTER(0x14),
	rshFloatPP = _RSH_GROUP_TYPE_POINTER(0x15),
	rshDoublePP = _RSH_GROUP_TYPE_POINTER(0x16),
	rshBoolPP = _RSH_GROUP_TYPE_POINTER(0x17),

	rshBufferTypeU8 = _RSH_GROUP_TYPE_BUFFER(0x1), //0xadc03000
	rshBufferTypeS8 = _RSH_GROUP_TYPE_BUFFER(0x2),
	rshBufferTypeU16 = _RSH_GROUP_TYPE_BUFFER(0x3),
	rshBufferTypeS16 = _RSH_GROUP_TYPE_BUFFER(0x4),
	rshBufferTypeU32 = _RSH_GROUP_TYPE_BUFFER(0x5),
	rshBufferTypeS32 = _RSH_GROUP_TYPE_BUFFER(0x6),
	rshBufferTypeU64 = _RSH_GROUP_TYPE_BUFFER(0x7),
	rshBufferTypeS64 = _RSH_GROUP_TYPE_BUFFER(0x8),
	rshBufferTypeFloat = _RSH_GROUP_TYPE_BUFFER(0x9),
	rshBufferTypeDouble = _RSH_GROUP_TYPE_BUFFER(0xA),
	rshBufferTypeBool = _RSH_GROUP_TYPE_BUFFER(0xB),
	rshBufferTypeChannel = _RSH_GROUP_TYPE_BUFFER(0xC),
	rshBufferTypePortInfo = _RSH_GROUP_TYPE_BUFFER(0xD),
	rshBufferTypeSetting = _RSH_GROUP_TYPE_BUFFER(0xE),
	rshBufferTypeSettingChannel = _RSH_GROUP_TYPE_BUFFER(0xF),
	rshDBufferTypeU8 = _RSH_GROUP_TYPE_BUFFER(0x10),
	rshDBufferTypeS8 = _RSH_GROUP_TYPE_BUFFER(0x11),
	rshDBufferTypeU16 = _RSH_GROUP_TYPE_BUFFER(0x12),
	rshDBufferTypeS16 = _RSH_GROUP_TYPE_BUFFER(0x13),
	rshDBufferTypeU32 = _RSH_GROUP_TYPE_BUFFER(0x14),
	rshDBufferTypeS32 = _RSH_GROUP_TYPE_BUFFER(0x15),
	rshDBufferTypeU64 = _RSH_GROUP_TYPE_BUFFER(0x16),
	rshDBufferTypeS64 = _RSH_GROUP_TYPE_BUFFER(0x17),
	rshDBufferTypeFloat = _RSH_GROUP_TYPE_BUFFER(0x18),
	rshDBufferTypeDouble = _RSH_GROUP_TYPE_BUFFER(0x19),
	rshDBufferTypeBool = _RSH_GROUP_TYPE_BUFFER(0x1A),
	rshBufferTypeU8P = _RSH_GROUP_TYPE_BUFFER(0x1B),
	rshBufferTypeDeviceBaseInfo = _RSH_GROUP_TYPE_BUFFER(0x1C),
	rshBufferTypeDeviceFullInfo = _RSH_GROUP_TYPE_BUFFER(0x1D),
	rshBufferTypeChannelVoltage = _RSH_GROUP_TYPE_BUFFER(0x1E),
	rshBufferTypeCalibrationItem = _RSH_GROUP_TYPE_BUFFER(0x1F), 
	rshBufferTypeCalibrationGroup = _RSH_GROUP_TYPE_BUFFER(0x20), 
	rshBufferTypeBaseP = _RSH_GROUP_TYPE_BUFFER(0x21), 

	rshInitADC = _RSH_GROUP_TYPE_INIT(0x1), //0xadc04000
	rshInitGSPF = _RSH_GROUP_TYPE_INIT(0x2),
	rshInitDMA = _RSH_GROUP_TYPE_INIT(0x3),
	rshInitMemory = _RSH_GROUP_TYPE_INIT(0x4),
	rshInitVoltmeter = _RSH_GROUP_TYPE_INIT(0x5),
	rshInitPort = _RSH_GROUP_TYPE_INIT(0x6),
	rshInitPacket = _RSH_GROUP_TYPE_INIT(0x7),
	rshInitDAC = _RSH_GROUP_TYPE_INIT(0x8),
	rshInitTimer = _RSH_GROUP_TYPE_INIT(0x9),

	rshRegister = _RSH_GROUP_TYPE_STUFF(0x1), //0xadc05000
	rshPort = _RSH_GROUP_TYPE_STUFF(0x2),
	rshGatheringParameters = _RSH_GROUP_TYPE_STUFF(0x3),
	rshDeviceActiveList = _RSH_GROUP_TYPE_STUFF(0x4),
	rshOnboardBaseInfo = _RSH_GROUP_TYPE_STUFF(0x5),
	rshDeviceBaseInfo = _RSH_GROUP_TYPE_STUFF(0x6),
	rshDeviceFullInfo = _RSH_GROUP_TYPE_STUFF(0x7),
	rshDeviceBuffer = _RSH_GROUP_TYPE_STUFF(0x8),
	rshPortInfo = _RSH_GROUP_TYPE_STUFF(0x9),
	rshBoardPortInfo = _RSH_GROUP_TYPE_STUFF(0xA),
	rshIFactory = _RSH_GROUP_TYPE_STUFF(0xB),
	rshIRSHDevice = _RSH_GROUP_TYPE_STUFF(0xC),
	rshChannel = _RSH_GROUP_TYPE_STUFF(0xD),
	rshSynchroChannel = _RSH_GROUP_TYPE_STUFF(0xE),
	rshCalibrationParameters = _RSH_GROUP_TYPE_STUFF(0xF),
	rshCalibrationControl = _RSH_GROUP_TYPE_STUFF(0x10),
	rshIDebug = _RSH_GROUP_TYPE_STUFF(0x11),
	rshChannelVoltage = _RSH_GROUP_TYPE_STUFF(0x12),
	rshDeviceKey = _RSH_GROUP_TYPE_STUFF(0x13),
	rshCalibrationChannelParameter = _RSH_GROUP_TYPE_STUFF(0x14),
	rshCalibrationItemBase = _RSH_GROUP_TYPE_STUFF(0x15),
	rshCalibrationItemEntity = _RSH_GROUP_TYPE_STUFF(0x16),
	rshCalibrationItemRegister = _RSH_GROUP_TYPE_STUFF(0x17),	
	rshCalibrationItemButton = _RSH_GROUP_TYPE_STUFF(0x18),
	rshCalibrationItemFilePath = _RSH_GROUP_TYPE_STUFF(0x19),
	rshCalibrationItemRegOffset = _RSH_GROUP_TYPE_STUFF(0x1A),

	rshBoardInfoDMA = _RSH_GROUP_TYPE_INTERNAL(0x1), //0xadc06000
	rshBoardInfoMemory = _RSH_GROUP_TYPE_INTERNAL(0x2),
	rshBoardInfoDAC = _RSH_GROUP_TYPE_INTERNAL(0x3),
	rshBoardInfoDP = _RSH_GROUP_TYPE_INTERNAL(0x4),
	rshFRDACTune  = _RSH_GROUP_TYPE_INTERNAL(0x5),
	rshTunerDataWrapper = _RSH_GROUP_TYPE_INTERNAL(0x6),
	rshTunerDataWrapperP = _RSH_GROUP_TYPE_INTERNAL(0x7),

	rshDPADataFFTComplex  = _RSH_GROUP_TYPE_DPA(0x1), //0xadc07000
	rshDPADataWindowFunction  = _RSH_GROUP_TYPE_DPA(0x2),
	rshDPADataFindGap = _RSH_GROUP_TYPE_DPA(0x3),
	rshDPADataFindFront  = _RSH_GROUP_TYPE_DPA(0x4),
	rshDPADataGeneratorSignalBase = _RSH_GROUP_TYPE_DPA(0x5),
	rshDPADataFFTPowerSpectrum = _RSH_GROUP_TYPE_DPA(0x6),
	rshDPAStatisticsBase = _RSH_GROUP_TYPE_DPA(0x7),
	rshDPADataStroboscope = _RSH_GROUP_TYPE_DPA(0x8),
	rshDPADataSaveHDF5 = _RSH_GROUP_TYPE_DPA(0x9),
	rshDPADataThermoCouple = _RSH_GROUP_TYPE_DPA(0xA),

	rshLabDataBuffer = _RSH_GROUP_TYPE_LAB(0x1), //0xadc08000
	rshLabDataStatistics = _RSH_GROUP_TYPE_LAB(0x2), 
	rshLabDataFeatures = _RSH_GROUP_TYPE_LAB(0x3),
	rshLabXYData = _RSH_GROUP_TYPE_LAB(0x4), 
	rshLabDataSave = _RSH_GROUP_TYPE_LAB(0x5),

} RshDataTypes;



/*!
 * 
 * \~english
 * \brief
 * Infinite timeout for operations.
 * 
 * Pass this constant to event waiting functions
 * such as IRshDevice::Get() with ::RSH_GET_WAIT_BUFFER_READY_EVENT.
 * Timeout for operation will be set to infinite.
 * 
 * \remarks
 * The only way to exit waiting state is to reset event
 * (you can call IRshDevice::Stop() to do it).
 * 
 * \see
 * IRshDevice | RSH_GET_WAIT_BUFFER_READY_EVENT
 * 
 * \~russian
 * \brief
 * Бесконечное время ожидания для операций.
 * 
 * Используется для передачи в качестве времени ожидания в 
 * функции ожидания событий (например IRshDevice::Get() с
 * параметром ::RSH_GET_WAIT_BUFFER_READY_EVENT).
 * Время ожидания будет бесконечным, т.е. метод не вернет результат
 * до тех пор, пока не произойдет ожидаемое событие или какой-либо сбой.
 * 
 * \remarks
 * Единственный способ прервать ожидание при использовании данной 
 * константы - это сброс события (вызов IRshDevice::Stop() ).
 * 
 * \see
 * IRshDevice | RSH_GET_WAIT_BUFFER_READY_EVENT
 */
#define RSH_INFINITE_WAIT_TIME	0xffffffff

#define _RSH_GROUP_GET_DELIMITER(value)    (  value << 16 )
#define	_RSH_GROUP_GET_BUFFER(value)       ( _RSH_GROUP_GET_DELIMITER(0x1) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_WAIT(value)         ( _RSH_GROUP_GET_DELIMITER(0x2) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_DEVICE(value)       ( _RSH_GROUP_GET_DELIMITER(0x3) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_SDK(value)          ( _RSH_GROUP_GET_DELIMITER(0x4) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_LIBRARY(value)      ( _RSH_GROUP_GET_DELIMITER(0x5) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_CORELIB(value)      ( _RSH_GROUP_GET_DELIMITER(0x6) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_RESET(value)        ( _RSH_GROUP_GET_DELIMITER(0x7) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_DEBUG(value)        ( _RSH_GROUP_GET_DELIMITER(0x8) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_CALIBRATION(value)  ( _RSH_GROUP_GET_DELIMITER(0x9) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_FLASH(value)        ( _RSH_GROUP_GET_DELIMITER(0xA) | ( value & 0xffff ) )
#define	_RSH_GROUP_GET_DPA(value)		   ( _RSH_GROUP_GET_DELIMITER(0xB) | ( value & 0xffff ) )

/*!
 * 
 * \~english
 * \brief
 * Operation codes for IRshDevice::Get() method of IRshDevice (and some other) interface.
 * 
 * \remarks
 * Most of these codes are used to obtain data from device library,
 * but some of them are used to set device parameters. These codes
 * have _SET postfix.
 * 
 * \see
 * IRshDevice::Get().
 * 
 * \~russian
 * \brief
 * Коды операций для метода IRshDevice::Get() интерфейса IRshDevice (и некоторых других).
 * 
 * \remarks
 * Большинство этих кодов используются для получения различной информации
 * из библиотеки устройства, но некоторые из них служат для передачи информации
 * в библиотеку или для управления устройством. Такие коды имеют суффикс _SET.
 * 
 * \see
 * IRshDevice::Get().
 */
typedef enum
{
	/*!
	 * \~english
	 * \brief
	 * Check buffer ready event state.
	 *
	 * <b>Data type</b>: [out] ::RSH_U32\n
	 * Obtained data: 1 - buffer ready event is signaled (data ready),
	 * 0 - buffer ready event is not signaled.
	 * If data acquisition process was started before IRshDevice::Get() call,
	 * one can check if data is ready or not using this code.	 
	 * 
	 * \remarks
	 * This code check only current state of buffer ready event,
	 * if you need create data wait routine better use
	 * ::RSH_GET_WAIT_BUFFER_READY_EVENT code instead.
	 *
	 * \see \link IRshDevice_Get_RSH_GET_BUFFER_READY_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Проверка готовности данных в случае одиночного преобразования.
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Полученные данные: 1 - было получено прерывание по готовности данных,
	 * 0 - прерывание не было получено.
	 * Если перед вызовом метода IRshDevice::Get() с данным кодом был запущен сбор данных,
	 * можно узнать, готова ли уже очередная порция данных.	
	 * 
	 * \remarks
	 * Данный код проверяет текущее (на момент вызова метода IRshDevice::Get()) состояние события,
	 * если нужно организовать цикл ожидания готовности данных, лучше воспользоваться
	 * кодом ::RSH_GET_WAIT_BUFFER_READY_EVENT.
	 *
	 * \see \link IRshDevice_Get_RSH_GET_BUFFER_READY_RU.cpp Пример использования \endlink
	 *
	 */
	RSH_GET_BUFFER_READY = _RSH_GROUP_GET_BUFFER(0x1), // 0x10000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Wait while data acquisition and transfer process will be finished.
	 * 
	 * <b>Data type</b>: [in] ::RSH_U32\n
	 * After starting data acquisition process, one can call IRshDevice::Get()
	 * with this parameter to start waiting data receive event. Second parameter
	 * of IRshDevice::Get() is timeout in ms. One can use ::RSH_INFINITE_WAIT_TIME
	 * for infinite waitng.
	 * 
	 * \remarks
	 * This method is analog of WinAPI WaitForSingleObject call, but
	 * realisation is crossplatform.
	 * 
	 * \warning Calling this method will lock caller thread until event signalled
	 * or timeout! If ::RSH_INFINITE_WAIT_TIME is used, the only way to unlock thread
	 * is call to IRshDevice::Stop() method from other thread.
	 *
	 * \see
	 * \link IRshDevice_Get_RSH_GET_WAIT_BUFFER_READY_EVENT_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Ожидание завершения процесса сбора и передачи данных.
	 * 
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * После запуска процесса сбора данных, можно вызвать метод IRshDevice::Get()
	 * с этим параметром и ожидать события готовности данных. Второй параметр в методе
	 * IRshDevice::Get() задает максимальное время ожидания (таймаут) в мс.
	 * Можно использовать константу ::RSH_INFINITE_WAIT_TIME для бесконечного ожидания.
	 * 
	 * \remarks
	 * По сути, данный метод аналогичен вызову функции WaitForSingleObject
	 * из WinAPI, но его реализация кроссплатформенная.
	 *
	 * \warning Вызов данного метода блокирует вызывающий поток до тех пор,
	 * пока не будет получено событие готовности данных, или таймаут! Если
	 * используется константа ::RSH_INFINITE_WAIT_TIME, единственный способ 
	 * отменить ожидание и разблокировать поток - это вызов метода IRshDevice::Stop().
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_WAIT_BUFFER_READY_EVENT_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_WAIT_BUFFER_READY_EVENT = _RSH_GROUP_GET_WAIT(0x1), // 0x10000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Wait for continious data acquisition process to finish.
	 * 
	 * <b>Data type</b>: [in] ::RSH_U32\n
	 * After calling IRshDevice::Stop() method continious data
	 * acquisition won't stop immidiately. Last data block can be transfered
	 * before process termination. Using this constant one can get sure
	 * that data acquisition process completely stopped before do anything else.\n
	 * Second parameter of IRshDevice::Get() is timeout in ms.
	 * One can use ::RSH_INFINITE_WAIT_TIME for infinite waitng.
	 * 
	 * \remarks
	 * In most cases you can avoid calling this method, but
	 * it can be extremely useful for thread synchronization
	 * in complex applications.
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_WAIT_GATHERING_COMPLETE_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Ожидание завершения процесса непрервыного сбора данных.
	 * 
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * После вызова метода IRshDevice::Stop() при работе в непрерывном режиме
	 * может пройти какое-то время до того момента, когда сбор будет
	 * фактически остановлен. Используя данную константу можно быть уверенным
	 * в том, что процесс сбора данных полностью остановлен, прежде чем
	 * выполнять какие-либо другие действия.\n
	 * Второй параметр в методе IRshDevice::Get() задает максимальное время
	 * ожидания (таймаут) в мс.Можно использовать константу ::RSH_INFINITE_WAIT_TIME
	 * для бесконечного ожидания.
	 * 
	 * \remarks
	 * В большинстве случаев можно обойтись без вызова данного метода, но
	 * он может быть очень полезен для синхронизации потоков в сложных приложениях.
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_WAIT_GATHERING_COMPLETE_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_WAIT_GATHERING_COMPLETE = _RSH_GROUP_GET_WAIT(0x2), // 0x20000
	
	RSH_GET_WAIT_NANO_DELAY = _RSH_GROUP_GET_WAIT(0x3), // 0x20000 //!< <b>Тип данных</b>: [in] ::RSH_U32\n Наносекундная задержка	

	RSH_GET_WAIT_INTERRUPT0 = _RSH_GROUP_GET_WAIT(0x4),  // 0x20000 //!< ожидание срабатывания прерывания iNT0

	RSH_GET_WAIT_INTERRUPT1 = _RSH_GROUP_GET_WAIT(0x5),  // 0x20000 //!< ожидание срабатывания прерывания iNT0

	/*!
	 * 
	 * \~english
	 * \brief
	 * Get product ID of the device.
	 * 
	 * <b>Data type</b>: [out] ::RSH_U32\n
	 * Each peace of hardware connected to PC has
	 * its unique (for device class) vendor ID and 
	 * device ID numbers. Using this numbers operation
	 * system can chose driver to use to work with
	 * this device.\n
	 * Using IRshDevice::Get() method with this constant
	 * one can obtain product id of the device.
	 *
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Получение идентификационного кода устройства.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Каждое устройство расширения, подключаемое к компьютеру,
	 * имеет уникальный (для данной модели устройства) код устройства (product ID или PID)
	 * и код производителя (vendor ID или VID). Операционная система
	 * использует данные коды для идентифиакции устройства и выбора драйвера
	 * для него.\n
	 * Используя метод IRshDevice::Get() с данной константой, можно
	 * получить код оборудования для устройства.	
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_PID = _RSH_GROUP_GET_DEVICE(0x1), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Get vendor ID of the device.
	 * 
	 * <b>Data type</b>: [out] ::RSH_U32\n
	 * Each peace of hardware connected to PC has
	 * its unique (for device class) vendor ID and 
	 * device ID numbers. Using this numbers operation
	 * system can chose driver to use to work with
	 * this device.\n
	 * Using IRshDevice::Get() method with this constant
	 * one can obtain vendor id of the device.
	 *
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Получение идентификационного кода производителя устройства.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Каждое устройство расширения, подключаемое к компьютеру,
	 * имеет уникальный (для данной модели устройства) код устройства (product ID или PID)
	 * и код производителя (vendor ID или VID). Операционная система
	 * использует данные коды для идентифиакции устройства и выбора драйвера
	 * для него.\n
	 * Используя метод IRshDevice::Get() с данной константой, можно
	 * получить код производителя устройства.	
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_VID = _RSH_GROUP_GET_DEVICE(0x2), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Get long name of the abatraction library.
	 * 
	 * <b>Data type</b>: [out] ::RSH_S8P\n
	 * Obtain string constant with library name.
	 * Pointer to internal string constant will be returned,
	 * no need to allocate memory in user application.	
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Получение полного имени библиотеки абстракции.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Получение указателя на строковую константу с именем
	 * библиотеки абстракции. Так как возвращается указатель,
	 * выделять память под строку дополнительно не нужно.
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_INFORMATION_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_NAME_VERBOSE = _RSH_GROUP_GET_DEVICE(0x3), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Unicode version of ::RSH_GET_DEVICE_NAME_VERBOSE.
	 * 
	 * <b>Data type</b>: [out] ::RSH_U16P\n
	 * Obtain string constant with library name in UTF-16 format.
	 *
	 * \~russian
	 * \brief
	 * Аналог ::RSH_GET_DEVICE_NAME_VERBOSE в формате юникод.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Получение строки с названием библиотеки в формате UTF-16.
	 * 
	 */
	RSH_GET_DEVICE_NAME_VERBOSE_UTF16 = _RSH_GROUP_GET_DEVICE(0x4), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Check for device and software feature support.
	 * 
	 * <b>Data type</b>: [in] ::RSH_U32\n
	 * Using this constant one can check if the device
	 * and abstraction library support various hardware
	 * and software features. Feature code must be passed
	 * as second parameter of IRshDevice::Get() method.
	 * 
	 * \remarks
	 * Full list of features one can check with detailed description
	 * can be found \link RSH_CAPS here \endlink.
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_IS_CAPABLE_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Определение возможностей устройства и библиотеки.
	 * 
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Используя данную константу, можно проверить, поддерживает
	 * ли устройство и библиотека различные аппаратные и программные
	 * режимы работы и возможности. Код свойства, поддержку которого 
	 * нужно проверить, должен передаваться в качестве второго параметра
	 * метода IRshDevice::Get().
	 * 
	 * \remarks
	 * Полный список свойств можно посмотреть \link RSH_CAPS здесь\endlink.
	 * 
	 * \see
	 * \link IRshDevice_Get_RSH_GET_DEVICE_IS_CAPABLE_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_IS_CAPABLE = _RSH_GROUP_GET_DEVICE(0x5), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Get base address list.
	 * 
	 * <b>Data type</b>: [out] ::RSH_BUFFER_U32\n
	 * When there are several devices of one type
	 * connected to PC (or boards installed), these
	 * devices are enumerated, and each device have
	 * its unique index (1 based).\n
	 * Using this constant, one can get such a list. 
	 * 
	 * \remarks
	 * Indexes obtained through this IRshDevice::Get()
	 * call can be used in IRshDevice::Connect() method.
	 * 
	 * \see
	 * IRshDevice::Connect() | \link IRshDevice_Get_RSH_GET_DEVICE_BASE_LIST_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Получение списка допустимых базовых адресов.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Если в системе установлено несколько устройств 
	 * одного типа, для выбора конкретного устройства
	 * используется базовый адрес. Базовые адреса выдаются
	 * операционной системой, и зависят от слота (порта)
	 * подключения, а также порядка включения устройств.\n
	 * Используя данную константу, можно получить этот список
	 * в виде массива целых чисел.
	 * 
	 * \remarks
	 * Полученные базовые адреса можно использовать
	 * в методе IRshDevice::Connect().
	 * 
	 * \see
	 * IRshDevice::Connect() | \link IRshDevice_Get_RSH_GET_DEVICE_BASE_LIST_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_BASE_LIST = _RSH_GROUP_GET_DEVICE(0x6), // 0x30000

	/*!
	 * 
	 * \~english
	 * \brief
	 * Get device list with additional information.
	 * 
	 * <b>Data type</b>: [out] ::RSH_BUFFER_DEVICE_BASE_INFO\n
	 * This constant is used for the same purpose as
	 * ::RSH_GET_DEVICE_BASE_LIST. But returned list
	 * is not simple base address array - it is list of RshDeviceBaseInfo
	 * structures. RshDeviceBaseInfo contains extended information about device,
	 * such as PCI slot used, VID and PID, serial number.	
	 * 
	 * \see
	 * RshDeviceBaseInfo | \link IRshDevice_Get_RSH_GET_DEVICE_BASE_LIST_EXT_EN.cpp Usage example \endlink
	 * 
	 * \~russian
	 * \brief
	 * Получение списка устройств с дополнительной информацией.
	 * 
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_DEVICE_BASE_INFO\n
	 * Данная константа используется для тех же целей, что и 
	 * ::RSH_GET_DEVICE_BASE_LIST. Но, в отличие от нее, возвращается
	 * не просто список допустимых базовых адресов, а массив структур
	 * RshDeviceBaseInfo. Структура RshDeviceBaseInfo содержит, помимо
	 * базового адреса, дополнительную информацию о подключенном устройстве -
	 * используемый PCI слот, коды оборудования и производителя, ревизию,
	 * заводской номер.	 
	 * 
	 * \see
	 * RshDeviceBaseInfo | \link IRshDevice_Get_RSH_GET_DEVICE_BASE_LIST_EXT_RU.cpp Пример использования \endlink
	 * 
	 */
	RSH_GET_DEVICE_BASE_LIST_EXT = _RSH_GROUP_GET_DEVICE(0x7), // 0x30000

	/*!
	 * \brief
	 * Минимально возможная частота дискретизации
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Минимально возможная частота, генерируемая таймером
	 */
	RSH_GET_DEVICE_MIN_FREQUENCY = _RSH_GROUP_GET_DEVICE(0x8), // 0x30000 

	/*!
	 * \brief
	 * Максимально возможная частота дискретизации
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Максимально возможная частота, генерируемая таймером
	 */

	RSH_GET_DEVICE_MAX_FREQUENCY = _RSH_GROUP_GET_DEVICE(0x9), // 0x30000

	/*!
	 * \brief
	 * Минимальное значение амплитуды (МЗР)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S32\n
	 * Минимальное значение амплитуды (МЗР)
	 */
	RSH_GET_DEVICE_MIN_AMP_LSB = _RSH_GROUP_GET_DEVICE(0xA), // 0x30000
	
	/*!
	 * \brief
	 * Максимальное значение амплитуды (МЗР)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S32\n
	 * Максимальное значение амплитуды (МЗР) 
	 */
	RSH_GET_DEVICE_MAX_AMP_LSB = _RSH_GROUP_GET_DEVICE(0xB), // 0x30000
	
	/*!
	 * \brief
	 * Таблица допустимых частот квантования
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_DOUBLE\n
	 * Таблица допустимых частот квантования
	 */
	RSH_GET_DEVICE_FREQUENCY_LIST = _RSH_GROUP_GET_DEVICE(0xC), // 0x30000
	
	/*!
	 * \brief
	 * Размер в байтах, необходимый для записи одного значения
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Размер в байтах, необходимый для записи одного значения 
	 */
	RSH_GET_DEVICE_DATA_SIZE_BYTES = _RSH_GROUP_GET_DEVICE(0xD), // 0x30000
	
	/*!
	 * \brief
	 * Разрядность АЦП (или ЦАП) 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Разрядность АЦП (или ЦАП) 
	 */
	RSH_GET_DEVICE_DATA_BITS = _RSH_GROUP_GET_DEVICE(0xE), // 0x30000
	
	/*!
	 * \brief
	 * Количество аналоговых каналов 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Количество аналоговых каналов 
	 */
	RSH_GET_DEVICE_NUMBER_CHANNELS = _RSH_GROUP_GET_DEVICE(0xF), // 0x30000
	
	/*!
	 * \brief
	 * Количество каналов в базовом устройстве 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Количество каналов в базовом устройстве.\n
	 * Актуально для систем и составных устройств (например, многоканальные осциллографы).
	 */
	RSH_GET_DEVICE_NUMBER_CHANNELS_BASE = _RSH_GROUP_GET_DEVICE(0x10), // 0x30000
	
	/*!
	 * \brief
	 * Список допустимых коэффициентов усиления
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых коэффициентов усиления для 
	 * аналоговых каналов.
	 */
	RSH_GET_DEVICE_GAIN_LIST = _RSH_GROUP_GET_DEVICE(0x11), // 0x30000
	
	/*!
	 * \brief
	 * Получение  массива с коэффициентами усиления для входа 50Ом 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Получение  массива с коэффициентами усиления для входа 50Ом 
	 */
	RSH_GET_DEVICE_GAIN_LIST_50_OHM = _RSH_GROUP_GET_DEVICE(0x12), // 0x30000
	
	/*!
	 * \brief
	 * Получение  массива с коэффициентами усиления для входа 1МОм 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Получение  массива с коэффициентами усиления для входа 1МОм 
	 */
	RSH_GET_DEVICE_GAIN_LIST_1_MOHM = _RSH_GROUP_GET_DEVICE(0x13), // 0x30000
	
	/*!
	 * \brief
	 * Размер памяти, установленной на плате (или доступной для сбора)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Размер памяти, установленной на плате (или доступной для сбора) 
	 */
	RSH_GET_DEVICE_MEMORY_SIZE = _RSH_GROUP_GET_DEVICE(0x14), // 0x30000
	
	/*!
	 * \brief
	 * Список допустимых размеров блоков собираемых данных 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых размеров блоков собираемых данных   
	 */
	RSH_GET_DEVICE_SIZE_LIST = _RSH_GROUP_GET_DEVICE(0x15), // 0x30000
	
	/*!
	 * \brief
	 * Список допустимых размеров буфера
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых размеров буфера в простом режиме работы
	 * (без использования удвоения/учетверения частоты)
	 */
	RSH_GET_DEVICE_SIZE_LIST_SINGLE = _RSH_GROUP_GET_DEVICE(0x16), // 0x30000
	
	/*!
	 * \brief
	 * Список допустимых размеров буфера в режиме удвоения  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых размеров буфера в режиме удвоения   
	 */
	RSH_GET_DEVICE_SIZE_LIST_DOUBLE = _RSH_GROUP_GET_DEVICE(0x17), // 0x30000
	
	/*!
	 * \brief
	 * Список допустимых размеров буфера в режиме учетверения  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых размеров буфера в режиме учетверения  
	 */
	RSH_GET_DEVICE_SIZE_LIST_QUADRO = _RSH_GROUP_GET_DEVICE(0x18), // 0x30000
		
	/*!
	 * \brief
	 * Список допустимых размеров пакетов   
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых размеров пакетов   
	 */
	RSH_GET_DEVICE_PACKET_LIST = _RSH_GROUP_GET_DEVICE(0x19), // 0x30000	
		
	/*!
	 * \brief
	 * Входной диапазон в вольтах при коэффициенте усиления 1 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Входной диапазон в вольтах при коэффициенте усиления 1   
	 */
	RSH_GET_DEVICE_INPUT_RANGE_VOLTS = _RSH_GROUP_GET_DEVICE(0x1A), // 0x30000
		
	/*!
	 * \brief
	 * Выходной диапазон в вольтах при коэффициенте усиления 1 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Выходной диапазон в вольтах при коэффициенте усиления 1
	 * (без использования аттенюатора)
	 */
	RSH_GET_DEVICE_OUTPUT_RANGE_VOLTS = _RSH_GROUP_GET_DEVICE(0x1B), // 0x30000	
		
	/*!
	 * \brief
	 * Список допустимых коэффициентов усиления для входа внешней синхронизации 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Список допустимых коэффициентов усиления для входа внешней синхронизации   
	 */
	RSH_GET_DEVICE_EXT_SYNC_GAINLIST = _RSH_GROUP_GET_DEVICE(0x1C), // 0x30000
		
	/*!
	 * \brief
	 * Получение  массива с коэффициентами усиления внешней синхронизации для входа 50Ом  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Получение  массива с коэффициентами усиления внешней синхронизации для входа 50Ом 
	 */
	RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_50_OHM = _RSH_GROUP_GET_DEVICE(0x1D), // 0x30000
		
	/*!
	 * \brief
	 * Получение  массива с коэффициентами усиления внешней синхронизации для входа 1МОм 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_U32\n
	 * Получение  массива с коэффициентами усиления внешней синхронизации для входа 1МОм  
	 */
	RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_1_MOHM = _RSH_GROUP_GET_DEVICE(0x1E), // 0x30000
		
	/*!
	 * \brief
	 * Диапазон входа внешней синхронизации в вольтах при коэффициенте усиления 1
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Диапазон входа внешней синхронизации в вольтах при коэффициенте усиления 1
	 */
	RSH_GET_DEVICE_EXT_SYNC_INPUT_RANGE_VOLTS = _RSH_GROUP_GET_DEVICE(0x1F), // 0x30000
		
	/*!
	 * \brief
	 * Получeние структуры из со служебной информацией о портах
	 *
	 * <b>Тип данных</b>: [out] RshBoardPortInfo\n
	 * Получeние структуры из со служебной информацией о портах
	 */
	RSH_GET_DEVICE_PORT_INFO = _RSH_GROUP_GET_DEVICE(0x20), // 0x30000
		
	/*!
	 * \brief
	 * Получение заводского номера устройства
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение заводского номера устройства  
	 */
	RSH_GET_DEVICE_SERIAL_NUMBER = _RSH_GROUP_GET_DEVICE(0x21), // 0x30000
		
	/*!
	 * \brief
	 * Размер предыстории в отсчетах
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Размер предыстории в отсчетах	 
	 */
	RSH_GET_DEVICE_PREHISTORY_SIZE = _RSH_GROUP_GET_DEVICE(0x22), // 0x30000
		
	/*!
	 * \brief
	 * Количество каналов, выбраных для работы
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Количество каналов, выбраных для работы (доступно после вызова метода IRshDevice::Init() )  
	 */
	RSH_GET_DEVICE_ACTIVE_CHANNELS_NUMBER = _RSH_GROUP_GET_DEVICE(0x23), // 0x30000
		
	/*!
	 * \brief
	 * Проверка статуса подключения для USB устройств
	 *
	 * <b>Тип данных</b>: [in] NULL\n
	 * Проверка статуса подключения для USB устройств. Второй параметр игнорируется.     
	 */
	RSH_GET_DEVICE_PLUG_STATUS = _RSH_GROUP_GET_DEVICE(0x24), // 0x30000
		
	/*!
	 * \brief
	 * Получение списка активных устройств
	 *
	 * <b>Тип данных</b>: [out] ::RSH_BUFFER_DEVICE_FULL_INFO\n
	 * Получение списка устройств ЗАО "Руднев-Шиляев",
	 * подключенных (установленных) в данный момент.\n
	 * Список заполняется на основании данных, получаемых от операционной
	 * системы.
	 *
	 */
	RSH_GET_DEVICE_ACTIVE_LIST = _RSH_GROUP_GET_DEVICE(0x25), // 0x30000
		
	/*!
	 * \brief
	 * Запуск процесса автоматической калибровки
	 *
	 * <b>Тип данных</b>: [in] NULL\n
	 * Производит автоматическую калибровку для тех устройств, которые поддерживают данную возможность	  
	 */
	RSH_GET_DEVICE_AUTO_CALIBRATION_SET = _RSH_GROUP_GET_DEVICE(0x26), // 0x30000 
		
	/*!
	 * \brief
	 * Управление ICP-питанием аналоговых каналов
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Управление ICP-питанием. Соответствующий каналу бит = 0 - нет питания, = 1 - есть питание  
	 * \todo Возможно, требуется доработка (данная опция только у Леонардо 2)
	 */
	RSH_GET_DEVICE_ICP_POWER_SET = _RSH_GROUP_GET_DEVICE(0x27), // 0x30000
		
	/*!
	 * \brief
	 * RSH_GET_DEVICE_AVR_MODE_SET
	 *
	 * НЕ РЕАЛИЗОВАНО в текущей версии
	 * \todo  RSH_GET_DEVICE_AVR_MODE_SET 
	 */
	RSH_GET_DEVICE_AVR_MODE_SET = _RSH_GROUP_GET_DEVICE(0x28), // 0x30000
		
	/*!
	 * \brief
	 * Чтение из регистра устройства 
	 *
	 * <b>Тип данных</b>: [out] RshRegister\n
	 * Чтение из регистра устройства  
	 */
	RSH_GET_DEVICE_REGISTER_BOARD = _RSH_GROUP_GET_DEVICE(0x29), // 0x30000
		
	/*!
	 * \brief
	 * Запись в регистр устройства
	 *
	 * <b>Тип данных</b>: [in] RshRegister\n
	 * Запись в регистр устройства   
	 */
	RSH_GET_DEVICE_REGISTER_BOARD_SET = _RSH_GROUP_GET_DEVICE(0x2A), // 0x30000
		
	/*!
	 * \brief
	 * Чтение из регистра устройства plx9050 (диапазон памяти 1)
	 *
	 * <b>Тип данных</b>: [out] RshRegister\n
	 * Чтение из регистра устройства plx9050 (диапазон памяти 1)
	 */
	RSH_GET_DEVICE_REGISTER_BOARD_SPACE1 = _RSH_GROUP_GET_DEVICE(0x2B), // 0x30000
		
	/*!
	 * \brief
	 * Запись в регистр устройства plx9050 (диапазон памяти 1)
	 *
	 * <b>Тип данных</b>: [in] RshRegister\n
	 * Запись в регистр устройства plx9050 (диапазон памяти 1)
	 */
	RSH_GET_DEVICE_REGISTER_BOARD_SPACE1_SET = _RSH_GROUP_GET_DEVICE(0x2C), // 0x30000
		
	/*!
	 * \brief
	 * Чтение из регистра устройства plx9050 (диапазон памяти 2)
	 *
	 * <b>Тип данных</b>: [out] RshRegister\n
	 * Чтение из регистра устройства plx9050 (диапазон памяти 2)
	 */
	RSH_GET_DEVICE_REGISTER_BOARD_SPACE2 = _RSH_GROUP_GET_DEVICE(0x2D), // 0x30000
		
	/*!
	 * \brief
	 * Запись в регистр устройства plx9050 (диапазон памяти 2)
	 *
	 * <b>Тип данных</b>: [in] RshRegister\n
	 * Запись в регистр устройства plx9050 (диапазон памяти 2)
	 */
	RSH_GET_DEVICE_REGISTER_BOARD_SPACE2_SET = _RSH_GROUP_GET_DEVICE(0x2E), // 0x30000
		
	/*!
	 * \brief
	 * Минимальное количество отсчетов (размер буфера) на канал
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Минимальное количество отсчетов (размер буфера) на канал  
	 */
	RSH_GET_DEVICE_MIN_SAMPLES_PER_CHANNEL = _RSH_GROUP_GET_DEVICE(0x2F), // 0x30000
		
	/*!
	 * \brief
	 * Максимальное количество отсчетов (размер буфера) на канал
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Максимальное количество отсчетов (размер буфера) на канал
	 */
	RSH_GET_DEVICE_MAX_SAMPLES_PER_CHANNEL = _RSH_GROUP_GET_DEVICE(0x30), // 0x30000
		
	/*!
	 * \brief
	 * Сброс устройства, освобождение захваченных устройством ресурсов
	 *
	 * <b>Тип данных</b>: [in] NULL\n
	 * Сброс устройства, освобождение захваченных устройством ресурсов
	 */
	RSH_GET_DEVICE_RESET = _RSH_GROUP_GET_DEVICE(0x31), // 0x30000
	
	/*!
	 * \brief
	 * Состояние питания устройства
	 *
	 * <b>Тип данных</b>: [in] NULL\n
	 * Проверка статуса питания (для устройств с внешним питанием). Второй параметр игнорируется.     
	 */
	RSH_GET_DEVICE_POWER_STATUS  = _RSH_GROUP_GET_DEVICE(0x32),// 0x30000

	/*
	 * \brief
	 * Получение списка активных устройств (расширенная информация)
	 *
	 * Получение списка активных устройств (расширенная информация)
	 * \warning В текущей версии не реализовано!
	 * \todo Возможно, следует удалить данный код
	 * 	
	RSH_GET_DEVICE_ACTIVE_LIST_EXT = _RSH_GROUP_GET_DEVICE(0x33), // 0x30000
	 */

	/*!
	 * \brief
	 * Получение данных GPS
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Формат строки зависит от устройства (чипа GPS).
	 * Как правило, данные представляют собой строку вида:\n
	 * <b>GGA,123519,4807.038,N,01131.324,E,1,08,0.9,545.4,M,46.9,M, , *42<\b>\n
	 * (пример для NMEA-0183). Подробное описание формата можно найти
	 * в руководстве пользователя для устройства.
	 *
	 */
	RSH_GET_DEVICE_GPS_DATA = _RSH_GROUP_GET_DEVICE(0x34), // 0x30000

	
	/*!
	 * \brief
	 * Получение данных GPS (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Аналог ::RSH_GET_DEVICE_GPS_DATA но в формате UTF-16.
	 */
	RSH_GET_DEVICE_GPS_DATA_UTF16 = _RSH_GROUP_GET_DEVICE(0x35), // 0x30000

	/*!
	 * \brief
	 * Установка интервала автозапуска
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Используется для задания интервала автоматического запуска сбора
	 * данных, для тех устройств, которые поддерживают данную возможность.
	 *
	 * \see
	 * RSH_CAPS_DEVICE_AUTO_START_MODE
	 */
	RSH_GET_DEVICE_AUTO_START_INTERVAL_SET = _RSH_GROUP_GET_DEVICE(0x36), // 0x30000

	/*!
	 * \brief
	 * Получение текущего значения напряжения питания
	 *
	 * <b>Тип данных</b>: [out] ::RSH_DOUBLE\n
	 * Получение текущего значения напряжения питания в вольтах.\n 
	 * Как правило, применияется для устройств с автономным питанием.
	 */
	RSH_GET_DEVICE_POWER_SOURCE_VOLTAGE = _RSH_GROUP_GET_DEVICE(0x37), // 0x30000

		
	/*!
	 * \brief
	 * Версия SDK major  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Версия SDK major  
	 */
	RSH_GET_SDK_VERSION_MAJOR = _RSH_GROUP_GET_SDK(0x1), // 0x40000
		
	/*!
	 * \brief
	 * Версия SDK minor  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Версия SDK minor 
	 */
	RSH_GET_SDK_VERSION_MINOR =  _RSH_GROUP_GET_SDK(0x2), // 0x40000
		
	/*!
	 * \brief
	 * Строковая константа с версией SDK
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа с версией SDK
	 */
	RSH_GET_SDK_VERSION_STRING =  _RSH_GROUP_GET_SDK(0x3), // 0x40000
		
	/*!
	 * \brief
	 * Строковая константа - название организации
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - название организации
	 */
	RSH_GET_SDK_COPYRIGHT_STRING =  _RSH_GROUP_GET_SDK(0x4), // 0x40000
		
	/*!
	 * \brief
	 * Строковая константа с версией SDK (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа с версией SDK (Unicode)
	 */
	RSH_GET_SDK_COPYRIGHT_STRING_UTF16 =  _RSH_GROUP_GET_SDK(0x5), // 0x40000
		
	/*!
	 * \brief
	 * Строковая константа - название организации (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - название организации (Unicode)
	 */
	RSH_GET_SDK_VERSION_STRING_UTF16 =  _RSH_GROUP_GET_SDK(0x6), // 0x40000
		
	/*!
	 * \brief
	 * Получение версии библиотеки - major.
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии библиотеки - major.  
	 */
	RSH_GET_LIBRARY_VERSION_MAJOR =  _RSH_GROUP_GET_LIBRARY(0x1), // 0x50000
		
	/*!
	 * \brief
	 * Получение версии библиотеки - minor.
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии библиотеки - minor.  
	 */
	RSH_GET_LIBRARY_VERSION_MINOR =  _RSH_GROUP_GET_LIBRARY(0x2), // 0x50000
		
	/*!
	 * \brief
	 * Получение версии библиотеки - build.
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии библиотеки - build.
	 */
	RSH_GET_LIBRARY_VERSION_BUILD =  _RSH_GROUP_GET_LIBRARY(0x3), // 0x50000
		
	/*!
	 * \brief
	 * Получение версии библиотеки - date.
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии библиотеки - date.
	 */
	RSH_GET_LIBRARY_VERSION_DATE =  _RSH_GROUP_GET_LIBRARY(0x4), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя интерфейса
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя интерфейса 
	 */
	RSH_GET_LIBRARY_INTERFACE_NAME =  _RSH_GROUP_GET_LIBRARY(0x5), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя интерфейса (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя интерфейса (Unicode)  
	 */
	RSH_GET_LIBRARY_INTERFACE_NAME_UTF16 =  _RSH_GROUP_GET_LIBRARY(0x6), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя модуля 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя модуля 
	 */
	RSH_GET_LIBRARY_MODULE_NAME =  _RSH_GROUP_GET_LIBRARY(0x7), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя модуля (Unicode) 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя модуля (Unicode)  
	 */
	RSH_GET_LIBRARY_MODULE_NAME_UTF16 =  _RSH_GROUP_GET_LIBRARY(0x8), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - путь размещения файла библиотеки 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - путь размещения файла библиотеки 
	 */
	RSH_GET_LIBRARY_PATH =  _RSH_GROUP_GET_LIBRARY(0x9), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - путь размещения файла библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - путь размещения файла библиотеки (Unicode)   
	 */
	RSH_GET_LIBRARY_PATH_UTF16 =  _RSH_GROUP_GET_LIBRARY(0xA), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя файла библиотеки абстракции
	 *
     * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя файла библиотеки абстракции
	 */
	RSH_GET_LIBRARY_FILENAME =  _RSH_GROUP_GET_LIBRARY(0xB), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - имя файла библиотеки абстракции (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя файла библиотеки абстракции (Unicode) 
	 */
	RSH_GET_LIBRARY_FILENAME_UTF16 =  _RSH_GROUP_GET_LIBRARY(0xC), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - версия библиотеки абстракции 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - версия библиотеки абстракции  
	 */
	RSH_GET_LIBRARY_VERSION_STR =  _RSH_GROUP_GET_LIBRARY(0xD), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - версия библиотеки абстракции (Unicode) 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - версия библиотеки абстракции (Unicode)  
	 */
	RSH_GET_LIBRARY_VERSION_STR_UTF16 =  _RSH_GROUP_GET_LIBRARY(0xE), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - описание библиотеки (как в свойствах файла)  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - описание библиотеки (как в свойствах файла)  
	 */
	RSH_GET_LIBRARY_DESCRIPTION =  _RSH_GROUP_GET_LIBRARY(0xF), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - описание библиотеки (Unicode)  
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - описание библиотеки (Unicode)  
	 */
	RSH_GET_LIBRARY_DESCRIPTION_UTF16 =  _RSH_GROUP_GET_LIBRARY(0x10), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - внутреннее имя библиотеки (как в свойствах файла) 
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - внутреннее имя библиотеки (как в свойствах файла)  
	 */
	RSH_GET_LIBRARY_PRODUCT_NAME =  _RSH_GROUP_GET_LIBRARY(0x11), // 0x50000
		
	/*!
	 * \brief
	 * Строковая константа - внутреннее имя библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - внутреннее имя библиотеки (Unicode)  
	 */
	RSH_GET_LIBRARY_PRODUCT_NAME_UTF16 =  _RSH_GROUP_GET_LIBRARY(0x12), // 0x50000
		
	/*!
	 * \brief
	 * Получение версии базовой библиотеки - major
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии базовой библиотеки - major  
	 */
	RSH_GET_CORELIB_VERSION_MAJOR = _RSH_GROUP_GET_CORELIB(0x1), // 0x60000
		
	/*!
	 * \brief
	 * Получение версии базововй библиотеки - minor
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии базововй библиотеки - minor
	 */
	RSH_GET_CORELIB_VERSION_MINOR = _RSH_GROUP_GET_CORELIB(0x2), // 0x60000
		
	/*!
	 * \brief
	 * Получение версии базововй библиотеки - build
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии базововй библиотеки - build  
	 */
	RSH_GET_CORELIB_VERSION_BUILD = _RSH_GROUP_GET_CORELIB(0x3), // 0x60000
		
	/*!
	 * \brief
	 * Получение версии базововй библиотеки - date
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Получение версии базововй библиотеки - date  
	 */
	RSH_GET_CORELIB_VERSION_DATE = _RSH_GROUP_GET_CORELIB(0x4), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя интерфейса базовой библиотеки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя интерфейса базовой библиотеки  
	 */
	RSH_GET_CORELIB_INTERFACE_NAME = _RSH_GROUP_GET_CORELIB(0x5), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя интерфейса базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя интерфейса базовой библиотеки (Unicode) 
	 */
	RSH_GET_CORELIB_INTERFACE_NAME_UTF16 = _RSH_GROUP_GET_CORELIB(0x6), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя модуля базовой библиотеки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя модуля базовой библиотеки  
	 */
	RSH_GET_CORELIB_MODULE_NAME = _RSH_GROUP_GET_CORELIB(0x7), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя модуля базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя модуля базовой библиотеки (Unicode) 
	 */
	RSH_GET_CORELIB_MODULE_NAME_UTF16 = _RSH_GROUP_GET_CORELIB(0x8), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - путь размещения файла базовой библиотеки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - путь размещения файла базовой библиотеки
	 */
	RSH_GET_CORELIB_PATH = _RSH_GROUP_GET_CORELIB(0x9), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - путь размещения файла базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - путь размещения файла базовой библиотеки (Unicode)   
	 */
	RSH_GET_CORELIB_PATH_UTF16 = _RSH_GROUP_GET_CORELIB(0xA), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя файла базовой библиотеки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - имя файла базовой библиотеки 
	 */
	RSH_GET_CORELIB_FILENAME = _RSH_GROUP_GET_CORELIB(0xB), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - имя файла базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - имя файла базовой библиотеки (Unicode)  
	 */
	RSH_GET_CORELIB_FILENAME_UTF16 = _RSH_GROUP_GET_CORELIB(0xC), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - версия базовой библиотеки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - версия базовой библиотеки   
	 */
	RSH_GET_CORELIB_VERSION_STR = _RSH_GROUP_GET_CORELIB(0xD), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - версия базовой библиотеки Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - версия базовой библиотеки Unicode)  
	 */
	RSH_GET_CORELIB_VERSION_STR_UTF16 = _RSH_GROUP_GET_CORELIB(0xE), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - описание базовой библиотеки (как в свойствах файла)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - описание базовой библиотеки (как в свойствах файла)  
	 */
	RSH_GET_CORELIB_DESCRIPTION = _RSH_GROUP_GET_CORELIB(0xF), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - описание базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - описание базовой библиотеки (Unicode)  
	 */
	RSH_GET_CORELIB_DESCRIPTION_UTF16 =  _RSH_GROUP_GET_CORELIB(0x10), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - внутреннее имя  базовой библиотеки (как в свойствах файла)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Строковая константа - внутреннее имя  базовой библиотеки (как в свойствах файла)
	 */
	RSH_GET_CORELIB_PRODUCT_NAME = _RSH_GROUP_GET_CORELIB(0x11), // 0x60000
		
	/*!
	 * \brief
	 * Строковая константа - внутреннее имя базовой библиотеки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Строковая константа - внутреннее имя базовой библиотеки (Unicode)
	 */
	RSH_GET_CORELIB_PRODUCT_NAME_UTF16= _RSH_GROUP_GET_CORELIB(0x12), // 0x60000
		
	/*!
	 * \brief
	 * Версия API драйвера (актуально для PLX устройств)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U32\n
	 * Версия API драйвера (актуально для PLX устройств)
	 */
	RSH_GET_CORELIB_VERSION_INTERNAL_API = _RSH_GROUP_GET_CORELIB(0x13), // 0x60000
		
	/*!
	 * \brief
	 * Версия  API драйвера в виде строки
	 *
	 * <b>Тип данных</b>: [out] ::RSH_S8P\n
	 * Версия  API драйвера в виде строки
	 */
	RSH_GET_CORELIB_VERSION_INTERNAL_API_STR = _RSH_GROUP_GET_CORELIB(0x14), // 0x60000
		
	/*!
	 * \brief
	 * Версия  API драйвера в виде строки (Unicode)
	 *
	 * <b>Тип данных</b>: [out] ::RSH_U16P\n
	 * Версия  API драйвера в виде строки (Unicode)
	 */
	RSH_GET_CORELIB_VERSION_INTERNAL_API_STR_UTF16 = _RSH_GROUP_GET_CORELIB(0x15), // 0x60000

	
	RSH_GET_RESET_WAIT_INTERRUPT0 = _RSH_GROUP_GET_RESET(0x1), // 0x70000
	RSH_GET_RESET_WAIT_INTERRUPT1 = _RSH_GROUP_GET_RESET(0x2), // 0x70000


	//////////////////////////////////////////
	//Get codes for DPA modules
	

	//DPA_FFT

	/*!
	 * \brief
	 * Установка плана БПФ ESTIMATE_FORWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ ESTIMATE_FORWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_ESTIMATE_FORWARD_SET = _RSH_GROUP_GET_DPA(0x1),

	/*!
	 * \brief
	 * Установка плана БПФ ESTIMATE_BACKWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ ESTIMATE_BACKWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_ESTIMATE_BACKWARD_SET = _RSH_GROUP_GET_DPA(0x2),

	/*!
	 * \brief
	 * Установка плана БПФ MEASURE_FORWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ MEASURE_FORWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_MEASURE_FORWARD_SET = _RSH_GROUP_GET_DPA(0x3),

	/*!
	 * \brief
	 * Установка плана БПФ MEASURE_BACKWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ MEASURE_BACKWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_MEASURE_BACKWARD_SET = _RSH_GROUP_GET_DPA(0x4),

	/*!
	 * \brief
	 * Установка плана БПФ PATIENT_FORWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ PATIENT_FORWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_PATIENT_FORWARD_SET = _RSH_GROUP_GET_DPA(0x5),

	/*!
	 * \brief
	 * Установка плана БПФ PATIENT_BACKWARD
	 *
	 * <b>Тип данных</b>: [in] ::RSH_U32\n
	 * Модуль DPA_FFT, установка плана БПФ PATIENT_BACKWARD.
	 * В качестве данных - желаемый размер буфера.
	 */
	RSH_GET_DPA_FFT_NEW_FFT_PLAN_PATIENT_BACKWARD_SET = _RSH_GROUP_GET_DPA(0x6),

	/*!
	 * \brief
	 * Сброс накопления данных
	 *
	 * <b>Тип данных</b>: [in] NULL\n
	 * Сброс накопления данных в алгоритме стробоскопирования.
	 * После вызова Get() c данным параметром внутренний буфер модуля обнуляется,
	 * и накопление данных начинается заново.
	 * Второй параметр игнорируется.     
	 */
	RSH_GET_DPA_STROBOSCOPE_RESET = _RSH_GROUP_GET_DPA(0x7),

	//DPA_GeneratorSignal


}RSH_GET;


 /*!
  * 
  * \~english
  * \brief
  * List of device and software capabilities (features).
  * 
  * You can check what device is capable of using 
  * IRshDevice::Get() method with parameter ::RSH_GET_DEVICE_IS_CAPABLE.\n
  * 
  * \see
  * IRshDevice::Get() | \link IRshDevice_Get_RSH_GET_DEVICE_IS_CAPABLE_EN.cpp Usage example \endlink
  * 
  * \~russian
  * \brief
  * Список возможностей устройства и программного обеспечения
  * 
  * Позволяет узнать, какие возможности поддерживаются устройством
  * и библиотекой абстракции, используя метод IRshDevice::Get()
  * с параметром ::RSH_GET_DEVICE_IS_CAPABLE.\n
  *
  * \see
  * IRshDevice::Get() | \link IRshDevice_Get_RSH_GET_DEVICE_IS_CAPABLE_RU.cpp Пример использования \endlink
  *
  */
 typedef enum {
	 
	 /*!
	  * \~english
	  * \brief
	  * Device has PCI interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом PCI.
	  */
	 RSH_CAPS_DEVICE_PCI = 0,

	 /*!
	  * \~english
	  * \brief
	  * Device has PCI Express interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом PCI Express.
	  */
	 RSH_CAPS_DEVICE_PCI_EXPRESS = 1,

	 /*!
	  * \~english
	  * \brief
	  * Device has USB 1.1 interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом USB 1.1.
	  */
	 RSH_CAPS_DEVICE_USB1_1 = 2,

	 /*!
	  * \~english
	  * \brief
	  * Device has USB 2.0 interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом USB 2.0.
	  */
	 RSH_CAPS_DEVICE_USB2_0 = 3,

	 /*!
	  * \~english
	  * \brief
	  * Device has USB 3.0 interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом USB 3.0.
	  */
	 RSH_CAPS_DEVICE_USB3_0 = 4,

	 /*!
	  * \~english
	  * \brief
	  * Device has Ethernet interface.
	  * \~russian
	  * \brief
	  * Устройство с интерфейсом Ethernet.
	  */
	 RSH_CAPS_DEVICE_ETHERNET = 5,

	
	 /*!
	  * \~english
	  * \brief
	  * Device has frequency synthesizer installed.
	  *
	  * Frequency synthesizer allows to vary sampling rate smoothly,
	  * opposite to standart devices with frequency divider,
	  * where you have maximum frequency Fmax and dirived frequencies
	  * such as Fmax/2, Fmax/4 etc.
	  *
	  * \remarks
	  * Some devices with frequency synthesizer DO NOT SUPPORT free frequency select
	  * and have a list of the predefined frequencies anyway.
	  * Check it using ::RSH_CAPS_DEVICE_FREQUENCY_LIST.
	  *
	  * \see RSH_CAPS_DEVICE_FREQUENCY_LIST | RSH_GET_DEVICE_FREQUENCY_LIST
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет синтезатор частоты.
	  *
	  * Синтезатор частоты позволяет плавно изменять
	  * частоту дискретизации, в отличие от устройств с делителем
	  * частоты, у которых есть некая максимальная частота дискретизации Fmax
	  * и кратные ей частоты Fmax/2, Fmax/4 и т.д.
	  *
	  * \remarks 
	  * Некоторые устройства с установленным синтезатором частоты НЕ ПОДДЕРЖИВАЮТ
	  * возможность произвольного выбора частоты дискретизации.
	  * Проверить наличие предопределенного списка поддерживаемых частот можно с 
	  * помощью ::RSH_CAPS_DEVICE_FREQUENCY_LIST.
	  *
	  * \see RSH_CAPS_DEVICE_FREQUENCY_LIST | RSH_GET_DEVICE_FREQUENCY_LIST
	  *
	  */
	 RSH_CAPS_DEVICE_FREQUENCY_SYNTHESIZER = 15,

	 /*!
	  * \~english
	  * \brief
	  * Device has 3 channel Intel 8254 PIT chip installed.
	  *
	  * Using RshInitTimer sturcture one can set some tricky
	  * data acquisition mode for device.	 
	  *
	  * \see  RshInitTimer
	  *
	  * \~russian
	  * \brief
	  * В устройстве установлен программируемый счетчик-таймер Intel 8254.
	  *
	  * Используя структуру инициализации RshInitTimer 
	  * можно задать нестандартный режим сбора данных.	
	  *
	  * \see  RshInitTimer
	  */
	 RSH_CAPS_DEVICE_TIMER_8254 = 16,	

	 /*!
	  * \~english
	  * \brief
	  * Device supports selection of individual block size for each analog channel.
	  * \~russian
	  * \brief
	  * Устройство поддерживает возможность задать произвольный размер блока для каждого измерительного канала.
	  */
	 RSH_CAPS_DEVICE_MEMORY_PER_CHANNEL = 17,

	 /*!
	  * \~english
	  * \brief
	  * Device has predefined sampling rates list.
	  *
	  * Frequency list can be obtained using IRshDevice::Get() method
	  * with parameter ::RSH_GET_DEVICE_FREQUENCY_LIST.\n
	  *
	  * \remarks
	  * If device don't have frequency list,
	  * one can obtaind minimum and maximum sampling rates for device
	  * using IRshDevice::Get() method with parameters ::RSH_GET_DEVICE_MIN_FREQUENCY
	  * and ::RSH_GET_DEVICE_MAX_FREQUENCY accordingly.
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет таблицу фиксированных частот квантования.
	  *
	  * Список частот дискретизации может быть получен с помощью метода IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_FREQUENCY_LIST.\n
	  *
	  * \remarks
	  * Если у устройства нет таблицы частот,
	  * можно получить минимальную и максимальную возможные частоты квантования,
	  * используя метод IRshDevice::Get() с параметрами ::RSH_GET_DEVICE_MIN_FREQUENCY
	  * и ::RSH_GET_DEVICE_MAX_FREQUENCY соответственно.
	  *
	  */
	 RSH_CAPS_DEVICE_FREQUENCY_LIST = 18,

	  /*!
	  * \~english
	  * \brief
	  * Device has predefined buffer size list.
	  *
	  * Buffer size list can be obtained using IRshDevice::Get() method
	  * with parameter ::RSH_GET_DEVICE_SIZE_LIST.\n
	  *
	  * \remarks 
	  * All sizes in list are related to single channel, so
	  * if you use 2 channels (for example), you must pass 2 times larger buffer
	  * in IRshDevice::GetData() than size you set in RshInitADC::bufferSize initialization parameter.
	  *
	  * If device don't have size list,
	  * one can obtaind minimum and maximum sample size for device
	  * using IRshDevice::Get() method with parameters ::RSH_GET_DEVICE_MIN_SAMPLES_PER_CHANNEL
	  * and ::RSH_GET_DEVICE_MAX_SAMPLES_PER_CHANNEL accordingly.
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет таблицу фиксированных размеров.
	  *
	  * Список частот дискретизации может быть получен с помощью метода IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_SIZE_LIST.\n
	  *
	  * \remarks
	  * Все размеры в таблице размеров приведены на канал, т.е. если используется
	  * 2 канала (например), в метод IRshDevice::GetData() нужно передать буфер
	  * в два раза большего размера, чем заданное значение параметра инициализации RshInitADC::bufferSize.
	  *
	  * Если у устройства нет таблицы размеров,
	  * можно получить минимальный и максимальный допустимый размер в отсчетах на канал,
	  * используя метод IRshDevice::Get() с параметрами ::RSH_GET_DEVICE_MIN_SAMPLES_PER_CHANNEL
	  * и ::RSH_GET_DEVICE_MAX_SAMPLES_PER_CHANNEL соответственно.
	  *
	  */
	 RSH_CAPS_DEVICE_SIZE_LIST = 19,

	 /*!
	  * \~english
	  * \brief
	  * Device has TTL lines for input (output).
	  *
	  * One can obtain additinal information about digital ports installed
	  * using IRshDevice::Get() with ::RSH_GET_DEVICE_PORT_INFO parameter.
	  * Obtained RshBoardPortInfo structure contains all information
	  * you need to control digital input/output.
	  *
	  * \see
	  * RshBoardPortInfo | RshInitPort
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет цифровые линии для ввода (вывода) данных
	  *
	  * Дополнительную информацию о цифровых портах устройства можно получить,
	  * используя метод IRshDevice::Get() с параметром ::RSH_GET_DEVICE_PORT_INFO.
	  * Полученная  структура RshBoardPortInfo содержит все необходимые данные
	  * для организации управления цифровыми вводом/выводом.
	  *
	  * \see
	  * RshBoardPortInfo | RshInitPort
	  *
	  */
	 RSH_CAPS_DEVICE_HAS_DIGITAL_PORT = 20,

	 /*!
	  * \~english
	  * \brief
	  * Device has predefined list of gain coefficients.
	  *	
	  * One can get this list using IRshDevice::Get() method
	  * with ::RSH_GET_DEVICE_GAIN_LIST parameter.\n Input (or output)
	  * range of the device is divided by coefficients from list.
	  * For example, if device has input range 10V and we set gain equal 2,
	  * device will have input range 5V for the same bit range, so dynamic range
	  * will improve.
	  *
	  * \see
	  * RSH_GET_DEVICE_GAIN_LIST | RSH_GET_DEVICE_INPUT_RANGE_VOLTS | RshLsbToVoltCoef
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет таблицу коэффициентов усиления.
	  *
	  *	Получить список коэффициентов усиления можно с помощью метода
	  * IRshDevice::Get() с параметром ::RSH_GET_DEVICE_GAIN_LIST. \n
	  * При использовании коэффициента усиления отличного от 1.0,
	  * входной (или выходной) диапазон устройства делится на этот коэффициент
	  * усиления, позволяя более полно задействовать динамический диапазон АЦП
	  * при работе со слабыми сигналами.\n Например, если устройство имеет входной диапазон
	  * 10В и 12 бит, вся шкала от 0 до 4096МЗР соотвествует напряжению от -10 до +10В.
	  * Использование коэффициента усиления равного 2 ставит в соответствие тому же диапазону
	  * (от 0 до 4096МЗР) напряжение от -5 до +5В, таким образом цена одного МЗР становится в два
	  * раза меньше. Правильно выбрав коэффициент усиления, можно более точно измерить слабый сигнал.
	  *
	  * \see
	  * RSH_GET_DEVICE_GAIN_LIST | RSH_GET_DEVICE_INPUT_RANGE_VOLTS | RshLsbToVoltCoef
	  *
	  */
	 RSH_CAPS_DEVICE_GAIN_LIST = 21,

	 /*!
	  * \~english
	  * \brief
	  * Gain coefficients can be set separately for each analog channel.
	  *
	  * Gain coefficients can be obtained using IRshDevice::Get() method
	  * with ::RSH_GET_DEVICE_GAIN_LIST parameter. \n
	  * Gain coefficients can be set using RshInitADC::channels list.
	  *
	  * \remarks
	  * Most of the rsh devices have this feature.
	  *
	  * \see 
	  * RshChannel | RshInitADC | RSH_GET_DEVICE_GAIN_LIST
	  *
	  * \~russian
	  * \brief
	  * Поддерживается установка коэффициента усиления индивидуально для каждого канала.
	  *
	  * Список коэффициентов усиления может быть получен с помощью метода IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_GAIN_LIST. \n
	  * Устанавливаются коэффиценты усиления в списке RshInitADC::channels структуры инициализации.
	  *
	  * \remarks
	  * Большинство устройств поддерживают эту возможность.
	  *
	  * \see 
	  * RshChannel | RshInitADC | RSH_GET_DEVICE_GAIN_LIST
	  *
	  */
	 RSH_CAPS_DEVICE_GAINS_PER_CHANNEL = 22,

	 /*!
	  * \~english
	  * \brief
	  * Prehistory data writing is availible.
	  *
	  * Using RshInitMemory::preHistory field one can choose, what part
	  * of databuffer will be used for saving "prehistory" data
	  * (before synchronization event occurred) and "history" data
	  * (after synchronization event occurred).
	  *
	  * \remarks
	  * Prehistory parameter is only used when working with synchronization.
	  *
	  * \see
	  * RshInitMemory | RSH_GET_DEVICE_PREHISTORY_SIZE | \link page_Synchronization Synchronization\endlink
	  * 
	  * \~russian
	  * \brief
	  * Доступна возможность записи предыстории измерения.
	  *
	  * Используя поле RshInitMemory::preHistory структуры инициализации,
	  * можно задать, какая часть буфера данных будет использована для 
	  * записи данных "предыстории" (до события синхронизации) и 
	  * "истории" (после события синхронизации).	
	  *
	  * \remarks
	  * Параметр "предыстория" актуален только при работе в режиме синхронизации.
	  *
	  * \see
	  * RshInitMemory | RSH_GET_DEVICE_PREHISTORY_SIZE | \link page_Synchronization Синхронизация\endlink
	  */
	 RSH_CAPS_DEVICE_PREHISTORY = 23,

	 /*!
	  * \~english
	  * \brief
	  * Device supports double frequency data acquisition mode.
	  * 
	  * Some of high sampling rate devices with on board memory installed
	  * can operate in so called <b>double frequency</b> mode.
	  * For such devices, each analog channel usualy has its own ADC chip
	  * and when device is operated in normal mode, all ADC work in parralles,
	  * converting data from analog inputs.\n
	  * When double frequency mode is activated, 2 ADC start work with only one analog input
	  * (for most devices it is first channel, but for some you can chose what channel use
	  * for double frequency - see ::RSH_CAPS_DEVICE_FREE_CHANNEL_SELECT_IN_EXT_MODE).\n
	  * The result of this is that sampling rate (and buffer size) is doubled for selected channel,
	  * so if device has maximum sampling frequency 1GHz for example, in double frequency mode 
	  * it will have ONLY one channel active, but with 2GHz sampling rate.\n
	  * Example: \include IRshDevice_DoubleFreqMode_EN.cpp
	  *
	  * \remarks
	  * For block devices like oscillosopes, when 2 or more ADC board are combined in one 
	  * multychannel device, total number of channels in double frequency mode is half
	  * its channels in normal mode.
	  *
	  * \see
	  * RshInitMemory | RSH_CAPS_DEVICE_FREE_CHANNEL_SELECT_IN_EXT_MODE
	  *
	  * \~russian
	  * \brief
	  * Устройство поддерживает режим сбора данных с удвоенной частотой дискретизации.
	  *
	  * Некоторые из высокочастотных устройств с собственной памятью
	  * могут работать в так называемом режиме <b>удвоения частоты</b>.
	  * Как правило, на таких устройствах установлено отдельное АЦП для оцифровки каждого
	  * канала. Когда устройство работает в обычном режиме, все АЦП работают параллельно,
	  * каждое цифрует данные со своего аналогового канала.\n
	  * В режиме удвоения частоты, 2 АЦП работают с данными \a одного аналогового канала
	  * (для большинства устройств это первый канал, для некоторых устройств можно задать 
	  * канал, который будет использоваться для удвоения - см. ::RSH_CAPS_DEVICE_FREE_CHANNEL_SELECT_IN_EXT_MODE).\n
	  * В результате этого, частота дискретизации (и размер буфера) для этого канала удваивается,
	  * и если, к примеру, максимальная частота дискретизации для устройства 1ГГц, в режиме удвоения
	  * будет активен ТОЛЬКО один из двух каналов, но с частотой дискретизации 2ГГц. \n
	  * Пример: \include IRshDevice_DoubleFreqMode_RU.cpp
	  *
	  *
	  * \remarks
	  * Для составных устройств (многоканальных осциллографов), в которых используются 2 или
	  * более устройства в качестве базовых модулей, число каналов в режиме удвоения будет
	  * в два раза меньше, чеи общее число каналов осциллографа.
	  *
	  * \see
	  * RshInitMemory | RSH_CAPS_DEVICE_FREE_CHANNEL_SELECT_IN_EXT_MODE
	  *
	  */
	 RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE = 24,

	 /*!
	  * \~english
	  * \brief
	  * Device supports quadro frequency data acquisition mode.
	  *
	  * This mode is similar to double frequency mode (::RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE)
	  * only exception is that frequency is multiplied by 4 and not 2. Channel number
	  * is divided by 4, accordingly.
	  *
	  * \see 
	  * RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE
	  *
	  * \~russian
	  * \brief
	  * Устройство поддерживает режим режим сбора данных с учетверенной частотой дискретизации.
	  *
	  * Данный режим аналогичен удвоению частоты (::RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE),
	  * единственное отличие - частота умножается на 4, а не на 2. Число каналов, соответственно,
	  * тоже делится на 4.
	  *
	  * \see 
	  * RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE
	  *
	  */
	 RSH_CAPS_DEVICE_QUADRO_FREQUENCY_MODE = 25,

	 /*!
	  * \~english
	  * \brief
	  * Device supports autocalibration.
	  *
	  * Automatic internal calibration. Calibration procedure
	  * is device specific. For example, Leonardo II board
	  * adjust zero level for analog channels when one call
	  * IRshDevice::Get() with RSH_GET_DEVICE_AUTO_CALIBRATION_SET parameter.
	  *
	  * \remarks
	  * ::RSH_CAPS_SOFT_CALIBRATION_IS_AVAILABLE is not connected to this one!
	  * ::RSH_CAPS_SOFT_CALIBRATION_IS_AVAILABLE is active for device libraries
	  * that have imbeded calibration algorithms, used during device setup
	  * with external signal generation and measurement devices.
	  *
	  * \see
	  * RSH_GET_DEVICE_AUTO_CALIBRATION_SET
	  *
	  * \~russian
	  * \brief
	  * Устройство поддерживает режим автокалибровки.
	  *
	  * Автоматическая внутренняя калибровка. Процедура
	  * калибровки индивидуальна для каждого устройства.
	  * Например, плата Леонардо II настраивает уровни смещения нуля
	  * при вызове метода IRshDevice::Get() с параметром
	  * RSH_GET_DEVICE_AUTO_CALIBRATION_SET. 
	  *
	  * \remarks
	  * Флаг ::RSH_CAPS_SOFT_CALIBRATION_IS_AVAILABLE не связан с этим флагом!
	  * Наличие ::RSH_CAPS_SOFT_CALIBRATION_IS_AVAILABLE говорит о том, что
	  * в библиотеке устройства присуствуют алгоритмы калибровки, нужные
	  * при настройке (предпродажной или ремонтной) устройства. 
	  *
	  * \see
	  * RSH_GET_DEVICE_AUTO_CALIBRATION_SET
	  *
	  */
	 RSH_CAPS_DEVICE_AUTO_CALIBRATION = 26,

	 /*!
	  * \~english
	  * \brief
	  * Analog input of the device can be used as trigger source.
	  *
	  * Using RshInitMemory initialization structure one can
	  * set treshold and select one of the input analog channels as
	  * trigger source. Synchronization slope and some other parameters
	  * are also programmable. After starting data acquisition using 
	  * IRshDevice::Start() method, synchronization event will be 
	  * raised when signal on selected input will correspond to selected trigger settings.
	  *
	  * \see
	  * RshInitMemory | RshChannel
	  *
	  * \~russian
	  * \brief
	  * Аналоговые каналы устройства могут быть использованы в качестве источника синхронизации.
	  *
	  * Используя структуру инициализации RshInitMemory можно задать порог срабатывания,
	  * условие перехода (фронт или спад), а также некоторые другие параметры и выбрать один
	  * из аналоговых входных каналов устройства в качестве источника синхронизации.
	  * После запуска процесса сбора данных с помощью метода IRshDevice::Start(), устройство
	  * будет ожидать прихода события синхронизации в соотвествии с заданными параметрами.
	  *
	  * \see
	  * RshInitMemory | RshChannel 
	  *
	  */
	 RSH_CAPS_DEVICE_SYNCHRO_INTERNAL = 27,

	 /*!
	  * \~english
	  * \brief
	  * Device has additional input that can be used as trigger source.
	  *
	  * Syncrhonization parameters (such as threshold, slope, filter use etc.)
	  * can be selected using RshInitMemory structure.  After starting data acquisition using 
	  * IRshDevice::Start() method, synchronization event will be 
	  * raised when signal on external sync input will correspond to selected trigger settings.
	  *
	  * \remarks
	  * Usually external input differs from analog inputs - it can have its own
	  * input range, gain coefficients list, input resist switch, programmable filters, etc.
	  * All this parameters can be obtained using IRshDevice::Get() method. All external
	  * synchronization specific parameters have <b>RSH_GET_DEVICE_EXT_SYNC</b> prefix,
	  * for example ::RSH_GET_DEVICE_EXT_SYNC_GAINLIST.
	  *
	  * \see
	  * RshInitMemory | RshSynchroChannel
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет дополнительный вход, который может быть использован в качестве источника синхронизации.
	  *
	  * Параметры синхронизации (порог, условие перехода, использование фильтра и др.)
	  * могут быть заданы в структуре RshInitMemory. После запуска сбора данных с помощью
	  * метода IRshDevice::Start(), устройство будет ожидать прихода события синхронизаци
	  * в соотвествии с заданными параметрами.
	  *
	  * \remarks
	  * Вход внешней синхронизации обычно отличается от аналоговых входов по своим параметрам.
	  * Он может иметь собственный входной диапазон, список коэффициентов усиления, переключение
	  * сопротивления входа, программируемые фильтры и т.д. 
	  * Все эти параметры могут быть получены с помощью метода IRshDevice::Get(). Параметры,
	  * относящиеся к внешней синхронизации, имеют префикс <b>RSH_GET_DEVICE_EXT_SYNC</b>,
	  * например ::RSH_GET_DEVICE_EXT_SYNC_GAINLIST.
	  *
	  * \see
	  * RshInitMemory | RshSynchroChannel
	  */
	 RSH_CAPS_DEVICE_SYNCHRO_EXTERNAL = 28,
	 	
	 /*!
	  * \~english
	  * \brief
	  * Device has digital trigger.
	  *
	  * Data acquisition process can be triggered using TTL signal.
	  * Information about signal connection, levels and condition to trigger
	  * can be found in device documentation or user manual.
	  *
	  * \remarks
	  * External start and external synchronization are not the same thing!
	  *
	  * \~russian	  
	  * \brief
	  * Устройство поддерживает возможность внешнего запуска преобразования.
	  *
	  * Процесс сбора данных может быть запущен подачей TTL сигнала на определенный
	  * цифровой вход устройства.
	  * Информация о подключении, уровне сигнала и условиях срабатывания содержится
	  * в руководстве пользователя для конкретного устройства.
	  *
	  * \remarks
	  * Внешний запуск преобразования и внешняя синхронизация - не одно и то же!
	  *
	  */
	 RSH_CAPS_DEVICE_EXTERNAL_START = 29,

	 /*!
	  * \~english
	  * \brief
	  * Device has programmable hysteresis for synchronization.
	  *
	  * Some devices with hardware digital synchronization have
	  * programmable hysteresis level feature.\n
	  * For more details about this option see RshInitMemory::hysteresis.
	  *
	  * \see
	  * RshInitMemory::hysteresis | IRshDevice::Init() | \link page_Synchronization Synchronization\endlink
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет возможность задания уровня гистерезиса для синхронизации.
	  *
	  * Некоторые устройства с аппаратной цифровой синхронизацией имеют
	  * возможность программно задавать уровень гистерезиса. \n
	  * Более подробно об этой фозможности смотрите тут: RshInitMemory::hysteresis.
	  *
	  * \see
	  * RshInitMemory::hysteresis | IRshDevice::Init() | \link page_Synchronization Синхронизация\endlink
	  *
	  */
	 RSH_CAPS_DEVICE_HYSTERESIS = 30,

	 /*!
	  * \~english
	  * \brief
	  * Device have separate gain coefficients list for externl input.
	  *
	  * External syncrhonization input often have its own gain list.
	  * You can get that list using IRshDevice::Get() method with
	  * ::RSH_GET_DEVICE_EXT_SYNC_GAINLIST parameter.
	  *
	  * \remarks
	  * If external synchronization input supports resist switch,
	  * you can get different lists for 50Ohm and 1MOhm modes
	  * using ::RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_50_OHM and
	  * ::RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_1_MOHM constans accordingly.
	  *
	  * \see
	  * IRshDevice::Get() | RSH_GET_DEVICE_EXT_SYNC_GAINLIST
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет отдельный список коэффициентов усиления для входа внешней синхронизации.
	  *
	  * Вход внешней синхронизации часто отличается от обычных аналоговых входов,
	  * и может иметь свой собственный список коэффициентов усиления.
	  * Получить этот список можно используя метод IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_EXT_SYNC_GAINLIST.
	  *
	  * \remarks
	  * Если вход внешней синхронизации поддерживает переключение
	  * входного сопротивления, можно получить два различных списка
	  * коэффициентов усиления для 50Ом и 1МОм режима, используя
	  * метод IRshDevice::Get() с константами ::RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_50_OHM
	  * и ::RSH_GET_DEVICE_EXT_SYNC_GAIN_LIST_1_MOHM соответственно.
	  *
	  * \see
	  * IRshDevice::Get() | RSH_GET_DEVICE_EXT_SYNC_GAINLIST
	  *
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_GAIN_LIST = 31,

	 /*!
	  * \~english
	  * \brief
	  * High pass filter can be set on external syncrhonization input.
	  *
	  * Filter pass band and other details are device specific, see
	  * user manual for more information.\n
	  * RshInitMemory::channelSynchro field  of RshInitMemory is used for external
	  * synchronization channel control.
	  * RshSynchroChannel::FilterLow bit must be set in RshSynchroChannel::control field
	  * to turn filter on.
	  *
	  * \see RshInitMemory | RshSynchroChannel | \link RshInitMemroySynchroChannel_EN.cpp Example of external synchronization input setup\endlink
	  *
	  * \~russian
	  * \brief
	  * Фильтр низких частот может быть включен для входа внешней синхронизации.
	  *
	  * Полоса пропускания, подавление и другие характеристики фильтра зависят от
	  * типа устройства, более подробная информация содержится в руководстве пользователя.\n
	  * Для управления каналом внешней синхронизации используется поле
	  * RshInitMemory::channelSynchro структуры RshInitMemory.
	  * Для того, чтобы задействовать ФНЧ, нужно выставить бит 
	  * RshSynchroChannel::FilterLow в поле RshSynchroChannel::control.
	  *
	  * \see RshInitMemory | RshSynchroChannel | \link RshInitMemroySynchroChannel_RU.cpp Пример настройки параметров входа внешней синхронизации\endlink
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_FILTER_LOW = 32,

	  /*!
	  * \~english
	  * \brief
	  * Low pass filter can be set on external syncrhonization input.
	  *
	  * Filter pass band and other details are device specific, see
	  * user manual for more information.\n
	  * RshInitMemory::channelSynchro field  of RshInitMemory is used for external
	  * synchronization channel control.
	  * RshSynchroChannel::FilterHigh bit must be set in RshSynchroChannel::control field
	  * to turn filter on.
	  *
	  * \see RshInitMemory | RshSynchroChannel | \link RshInitMemroySynchroChannel_EN.cpp Example of external synchronization input setup\endlink
	  *
	  * \~russian
	  * \brief
	  * Фильтр высоких частот может быть включен для входа внешней синхронизации.
	  *
	  * Полоса пропускания, подавление и другие характеристики фильтра зависят от
	  * типа устройства, более подробная информация содержится в руководстве пользователя.\n
	  * Для управления каналом внешней синхронизации используется поле
	  * RshInitMemory::channelSynchro структуры RshInitMemory.
	  * Для того, чтобы задействовать ФВЧ, нужно выставить бит 
	  * RshSynchroChannel::FilterHigh в поле RshSynchroChannel::control.
	  *
	  * \see RshInitMemory | RshSynchroChannel | \link RshInitMemroySynchroChannel_RU.cpp Пример настройки параметров входа внешней синхронизации\endlink
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_FILTER_HIGH = 33,

	 /*!
	  * \~english
	  * \brief
	  * External synchronization input of the device has 50 Ohm resist mode.
	  *
	  * If RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_1_MOHM is also available,
	  * one can switch between resist modes using RshInitMemory::channelSynchro
	  * field of RshInitMemory structure. \n 
	  * If 50Ohm is the only option, or neither of resist CAPS available,
	  * using this setting will take no effect.
	  *
	  * \remarks
	  * When switching resist mode dont forget that modes have different gain lists
	  * and some features (as coupling) are available only for 1MOhm input mode.
	  *
	  * \see RSH_CAPS_DEVICE_EXT_SYNC_COUPLING_AC_DC | RshSynchroChannel | \link RshInitMemroySynchroChannel_EN.cpp Example of external synchronization input setup\endlink
	  *
	  * \~russian
	  * \brief
	  * Доступен режим входного сопротивления 50Ом для входа внешней синхронизации.
	  *
	  * Если, кроме того, активен режим RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_1_MOHM,
	  * можно программно переключать входное сопротивление входа, используя поле
	  * RshInitMemory::channelSynchro структуры RshInitMemory.\n	  
	  * Если 50Ом единственная доступная опция, или вообще ни одна из опций неактивна,
	  * использование данной настройки не будет иметь эффекта, и вход внешней синхронизации
	  * всегда будет в единственном доступном состоянии.
	  *
	  * \remarks
	  * При переключении сопротивления входа нужно помнить, что списки коэффициентов
	  * усиления различаются для разных входных сопротивлений. Кроме того, некоторые
	  * опции (например, возможность использования открытого/закрытого входа) доступны
	  * только в режиме 1МОм входа.
	  *
	  * \see RSH_CAPS_DEVICE_EXT_SYNC_COUPLING_AC_DC | RshSynchroChannel | \link RshInitMemroySynchroChannel_RU.cpp Пример настройки параметров входа внешней синхронизации\endlink 
	  *
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_50_OHM = 34,

	  /*!
	  * \~english
	  * \brief
	  * External synchronization input of the device has 1 MOhm resist mode.
	  *
	  * If RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_50_OHM is also available,
	  * one can switch between resist modes using RshInitMemory::channelSynchro
	  * field of RshInitMemory structure. \n 
	  * If 1MOhm is the only option, or neither of resist CAPS available,
	  * using this setting will take no effect.
	  *
	  * \remarks
	  * When switching resist mode dont forget that modes have different gain lists
	  * and some features (as coupling) are available only for 1MOhm input mode.
	  *
	  * \see RSH_CAPS_DEVICE_EXT_SYNC_COUPLING_AC_DC | RshSynchroChannel | \link RshInitMemroySynchroChannel_EN.cpp Example of external synchronization input setup\endlink
	  *
	  * \~russian
	  * \brief
	  * Доступен режим входного сопротивления 1МОм для входа внешней синхронизации.
	  *
	  * Если, кроме того, активен режим RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_50_OHM,
	  * можно программно переключать входное сопротивление входа, используя поле
	  * RshInitMemory::channelSynchro структуры RshInitMemory.\n	  
	  * Если 1МОм единственная доступная опция, или вообще ни одна из опций неактивна,
	  * использование данной настройки не будет иметь эффекта, и вход внешней синхронизации
	  * всегда будет в единственном доступном состоянии.
	  *
	  * \remarks
	  * При переключении сопротивления входа нужно помнить, что списки коэффициентов
	  * усиления различаются для разных входных сопротивлений. Кроме того, некоторые
	  * опции (например, возможность использования открытого/закрытого входа) доступны
	  * только в режиме 1МОм входа.
	  *
	  * \see RSH_CAPS_DEVICE_EXT_SYNC_COUPLING_AC_DC | RshSynchroChannel | \link RshInitMemroySynchroChannel_RU.cpp Пример настройки параметров входа внешней синхронизации\endlink 
	  *
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_INPUT_RESIST_1_MOHM = 35,

	 /*!
	  * \~english
	  * \brief
	  * AC/DC coupling of the external synchronization input can be changed.
	  *
	  * In 1MOhm input mode one can switch between AC and DC mode of external
	  * synchronization channel using RshInitMemory::channelSynchro
	  * field of RshInitMemory structure. \n  
	  *
	  * \see  RshSynchroChannel | \link RshInitMemroySynchroChannel_EN.cpp Example of external synchronization input setup\endlink 
	  * 
	  * \~russian
	  * \brief
	  * Доступна возможность переключения состояния входа внешней синхронизации "Открытый"/"Закрытый".
	  *
	  * Если синхровход работает в режиме входного сопротивления 1МОм, есть возможность
	  * задать состояние входа: открытый (постоянная составляющая сигнала учитывается) или
	  * закрытый (постоянная составляющая сигнала отбрасывается). Для установки параметра
	  * используется  поле RshInitMemory::channelSynchro структуры RshInitMemory.
	  *
	  * \see  RshSynchroChannel | \link RshInitMemroySynchroChannel_RU.cpp Пример настройки параметров входа внешней синхронизации\endlink 
	  * 
	  */
	 RSH_CAPS_DEVICE_EXT_SYNC_COUPLING_AC_DC = 36,

	 /*!
	  * \~english
	  * \brief
	  * Device have one or more DAC modules installed.
	  *
	  * One can get access to DACs using IRshDevice::Init() method
	  * with RshInitDAC initialization structure.
	  *
	  * \remarks
	  * Do not confuse this feature with RSH_CAPS_SOFT_GENERATION_IS_AVAILABLE.
	  * Second one is for devices which main feature is signal generation,
	  * such as GSPF. GSPF have internal buffer for data, attenuator and can play
	  * signals from buffer with different sampling frequencies.\n
	  * DAC installed on ADC board is quite simple, and can only
	  * set some voltage level on output node.
	  * 
	  * \see RSH_CAPS_SOFT_INIT_DAC | RshInitDAC | \link RshInitDAC_EN.cpp DAC control example\endlink
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет один или несколько ЦАПов.
	  *
	  * Управлять ЦАПами можно с помощью метода IRshDevice::Init(),
	  * используя структуру инициализации RshInitDAC.
	  *
	  * \remarks
	  * Не путайте данную возможность с RSH_CAPS_SOFT_GENERATION_IS_AVAILABLE.
	  * Для устройств, которые поддерживают RSH_CAPS_SOFT_GENERATION_IS_AVAILABLE,
	  * генерация сигнала является основным предназначением.\n
	  * Например, устройства серии GSPF имеют внутренний буфер для данных, аттенюатор,
	  * возможность выдачи сигнала из внутреннего буфера с различной частотой дискретизации
	  * и в разных режимах - одиночный, с повторением, по внешнему триггеру.\n
	  * Флаг RSH_CAPS_SOFT_INIT_DAC говорит о том, что устройство может, помимо основной
	  * своей задачи (сбор и оцифровка данных), выдать сигнал на ЦАП, причем
	  * никаких других действий кроме установки заданного уровня сигнала на выходе
	  * произвести нельзя.
	  * 
	  * \see RSH_CAPS_SOFT_INIT_DAC | RshInitDAC | \link RshInitDAC_RU.cpp пример управления ЦАПом\endlink
	  *
	  */
	 RSH_CAPS_DEVICE_HAS_DAC_INSTALLED = 37,

	 /*!
	  * \~english
	  * \brief
	  * Device's analog channels have programmable hardware input level adjustment.
	  *
	  * Usually, voltage range of this adjustment is equal to input voltage range.
	  * One can get access to this feature, using RshInitADC::channels list,
	  * via RshChannel::adjustment field.\n
	  * For example, device have input range ±25V, and we have sinus signal
	  * with mean value 20V and amplitude 10V. Without signal adjustment, we 
	  * cant't see full signal (it will be cut off becouse maximum value will be
	  * 20+10 = 30 V). Setting RshChannel::adjustment parameter for this channel
	  * to -15V we will have signal on ADC input in range from 35-15=20V to 10-15=-5V,
	  * which is in range of our ADC and can be converted without losing anything.
	  *
	  * \remarks You can acheive similar result using RshChannel::AC mode
	  * if ::RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC flag is available.
	  *
	  * \see RshChannel | RshInitADC
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет возможность подстройки уровня входного напряжения аналоговых каналов.
	  *
	  * Обычно, диапазон подстройки уровня входного напряжения совпадает со входным
	  * диапазоном канала.
	  * Управлять этим параметром можно отдельно для каждого канала в списке RshInitADC::channels,
	  * используя поле RshChannel::adjustment.\n
	  * Допустим, канал имеет входной диапазон ±25В, а на входе синусоидальный сигнал
	  * со средним значениме 20В и амплитудой 10В. Без коррекции входного напряжения
	  * на входе АЦП будет сигнал от 35В до 10В, и оцифровать его без потерь
	  * не получится. Установив же параметр RshChannel::adjustment равным, к примеру,
	  * -15В, мы получим на входе АЦП сигнал в диапазоне от 35-15=20В до 10-15=-5В,
	  * который может быть оцифрован без потерь.
	  *
	  * \remarks Добиться похожего результата можно, используя режим RshChannel::AC,
	  * если флаг ::RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC доступен для устройства.
	  *
	  * \see RshChannel | RshInitADC
	  */
	 RSH_CAPS_DEVICE_INPUT_LEVEL_ADJUSTMENT = 38,

	 /*!
	  * \~english
	  * \brief
	  * AC/DC coupling of the analog inputs can be changed.
	  *
	  * In 1MOhm input mode one can switch between AC and DC mode of analog
	  * input channels setting one of the flags (RshChannel::AC or RshChannel::DC)
	  * in RshChannel::control field for selected channel in RshInitMemory::channels list
	  * in RshInitMemory structure.
	  *
	  * \see  RshChannel | RshInitMemory | \link RshChannelSetup_EN.cpp Channels setup example\endlink
	  *
	  * \~russian
	  * \brief
	  * Доступна возможность переключения состояния аналоговых входов "открытый/закрытый".
	  *
	  * Если аналоговый канал поддерживает входное сопротивление 1МОм,
	  * в этом режиме можно переключать состояние канала между "открытый вход"
	  * и "закрытый вход", устанавливая один из флагов (RshChannel::AC или RshChannel::DC)
	  * в поле RshChannel::control для выбранного канала в списке RshInitMemory::channels
	  * в структуре инициализации RshInitMemory.
	  *
	  * \see  RshChannel | RshInitMemory | \link RshChannelSetup_RU.cpp Пример настройки каналов\endlink
	  *
	  */
	 RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC = 39,

	 /*!
	  * \~english
	  * \brief
	  * Analog input channels of the device has 50 Ohm resist mode.
	  *
	  * If RSH_CAPS_DEVICE_INPUT_RESIST_1_MOHM is also available,
	  * one can switch between resist modes using RshChannel::control field
	  * for selected channel in RshInitMemory::channels list of RshInitMemory structure.\n 
	  * If 50Ohm is the only option, or neither of resist CAPS available,
	  * using this setting will take no effect.
	  *
	  * \remarks
	  * When switching resist mode dont forget that modes have different gain lists
	  * and some features (as coupling) are available only for 1MOhm input mode.
	  *
	  * \see RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC | RshChannel | \link RshChannelSetup_EN.cpp Channels setup example\endlink
	  *
	  * \~russian
	  * \brief
	  * Доступен режим входного сопротивления 50Ом для аналоговых каналов.
	  *
	  * Если, кроме того, активен режим RSH_CAPS_DEVICE_INPUT_RESIST_1_MOHM,
	  * можно программно переключать входное сопротивление входа, используя поле
	  * RshChannel::control для выбранного канала в списке RshInitMemory::channels структуры RshInitMemory.\n	  
	  * Если 50Ом единственная доступная опция, или вообще ни одна из опций неактивна,
	  * использование данной настройки не будет иметь эффекта, и вход
	  * всегда будет в единственном доступном состоянии.
	  *
	  * \remarks
	  * При переключении сопротивления входа нужно помнить, что списки коэффициентов
	  * усиления различаются для разных входных сопротивлений. Кроме того, некоторые
	  * опции (например, возможность использования открытого/закрытого входа) доступны
	  * только в режиме 1МОм входа.
	  *
	  * \see RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC | RshChannel | \link RshChannelSetup_RU.cpp Пример настройки каналов\endlink
	  *
	  */
	 RSH_CAPS_DEVICE_INPUT_RESIST_50_OHM = 40,

	 /*!
	  * \~english
	  * \brief
	  * Analog input channels of the device has 1 MOhm resist mode.
	  *
	  * If RSH_CAPS_DEVICE_INPUT_RESIST_50_OHM is also available,
	  * one can switch between resist modes using RshChannel::control field
	  * for selected channel in RshInitMemory::channels list of RshInitMemory structure.\n 
	  * If 1MOhm is the only option, or neither of resist CAPS available,
	  * using this setting will take no effect.
	  *
	  * \remarks
	  * When switching resist mode dont forget that modes have different gain lists
	  * and some features (as coupling) are available only for 1MOhm input mode.
	  *
	  * \see RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC | RshChannel | \link RshChannelSetup_EN.cpp Channels setup example\endlink
	  *
	  * \~russian
	  * \brief
	  * Доступен режим входного сопротивления 1МОм для аналоговых каналов.
	  *
	  * Если, кроме того, активен режим RSH_CAPS_DEVICE_INPUT_RESIST_50_OHM,
	  * можно программно переключать входное сопротивление входа, используя поле
	  * RshChannel::control для выбранного канала в списке RshInitMemory::channels структуры RshInitMemory.\n	  
	  * Если 1МОм единственная доступная опция, или вообще ни одна из опций неактивна,
	  * использование данной настройки не будет иметь эффекта, и вход
	  * всегда будет в единственном доступном состоянии.
	  *
	  * \remarks
	  * При переключении сопротивления входа нужно помнить, что списки коэффициентов
	  * усиления различаются для разных входных сопротивлений. Кроме того, некоторые
	  * опции (например, возможность использования открытого/закрытого входа) доступны
	  * только в режиме 1МОм входа.
	  *
	  * \see RSH_CAPS_DEVICE_INPUT_COUPLING_AC_DC | RshChannel | \link RshChannelSetup_RU.cpp Пример настройки каналов\endlink
	  *
	  */
	 RSH_CAPS_DEVICE_INPUT_RESIST_1_MOHM = 41,
	 
	 /* dont sure we need this, commented	  
	 RSH_CAPS_DEVICE_ADC_MODE_SWITCH = 42,
	 */

	 /*!
	  * \~english
	  * \brief
	  * Device supports frame frequency mode.
	  *
	  * In this mode one defines two frequencies:\n
	  * one used inside frame (determing time between channels) and the other outside
	  * (determing time between frames).\n
	  * This mode is useful when one need to acqure data with low sampling rate from
	  * several channels and use ADC with non-synchronious (multyplexed) channels.
	  * Without this mode, gaps between channels will be very large because of low
	  * frequency. But with frame frequency used, interval between channel can be small,
	  * when interval between frames can be large.
	  *
	  * \see RshInitDMA | \link page_FrameFreqMode Frame frequency data acquisition mode\endlink
	  * 
	  * \~russian
	  * \brief
	  * Устройство поддерживает режим кадрового сбора.
	  * 
	  * В этом режиме задаются две частоты:\n
	  * одна определяет частоту внутри кадра (интервал между данными с разных каналов),
	  * а другая - частоту кадров (интервал между блоками данных, в каждом блоке - по
	  * одному отсчету с каждого выбранного для измерения канала).\n
	  * Этот режим полезен при использовании устройства АЦП, каналы
	  * которого мультиплексируются (не являются синхронными), с низкой частотой дискретизации.
	  * Без включения кадрового режима при использовании низкой частоты дискретизации интервал
	  * между каналами будет очень большим. Но если включить данный режим, можно одновнременно
	  * получить низкую частоту дискретизации и маленький интервал между измерениями с разных
	  * каналов.
	  *
	  * \see RshInitDMA | \link page_FrameFreqMode Кадровый режим сбора данных\endlink
	  */
	 RSH_CAPS_DEVICE_FRAME_FREQUENCY_MODE = 43,

	 /*!
	  * \~english
	  * \brief
	  * Device supports packet mode of data acquisition.
	  *
	  * This mode is used for devices with internal memory installed.
	  * Such devices first acquire data to internal buffer (that can be
	  * several Mb long), and then transfer data using USB/PCI interface
	  * to PC. Second process is quite long, so if required data size is small,
	  * it will be waste of time on data transfer. \n
	  * Thus, packet mode is quite useful: one setup data block size using RshInitMemory::bufferSize and
	  * number of blocks using  RshInitMemory::packetNumber
	  * (obviously, \b bufferSize*packetNumber must be less then \b MaximumMemory, which one can obtain
	  * using IRshDevice::Get() method with parameter ::RSH_GET_DEVICE_MEMORY_SIZE). \n
	  * When data acquistion process will be started with IRshDevice::Start() method,
	  * device will start acquistion (using all parameters such
	  * as trigger source etc.) multiple times until it got all RshInitMemory::packetNumber
	  * blocks and only after that will start transfer data to PC.
	  *
	  * \see RshInitMemory
	  *
	  * \~russian
	  * \brief
	  * Устройство поддерживает пакетный режим сбора данных.
	  *
	  * Этот режим используется для устройств сбора данных с установленной собственной памятью.
	  * Такие устройства собирают данные во внутренний буфер (размер которого может
	  * составлять несколько мегабайт), а затем передают эти данные в компьютер по относительном
	  * медленным интерфейсам (USB, PCI). Если задан небольшой размер буфера для сбора,
	  * основное время уходит не на сбор данных, а на инициализацию сбора и передачу их
	  * в компьютер.\n
	  *
	  * Пакетный режим, таким образом, может быть очень полезен: в этом режиме можно задать
	  * размер блока данных( поле RshInitMemory::bufferSize) и количество этих блоков
	  * (поле RshInitMemory::packetNumber). Очевидно, что итоговый размер, равный
	  * \b bufferSize*packetNumber, должен быть меньше, чем максимальный объем доступной
	  * внутренней памяти \b MaximumMemory (его можно узнать с помощью метода IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_MEMORY_SIZE).\n
	  * Когда будет запущен процесс сбора данных с помощью метода IRshDevice::Start(),
	  * устройство будет собирать данные (используя все заданные параметры сбора, настройки синхронизации
	  * и т.д.) до тех пор, пока не соберет RshInitMemory::packetNumber блоков данных. Только после
	  * этого начнется передача данных в компьютер. \n
	  * Таким образом, можно, например, записать без пропусков несколько быстрых процессов,
	  * идущих с небольшим интервалом, что было бы невозможно в обычном режиме.
	  *
	  * \see RshInitMemory
	  *
	  */
	 RSH_CAPS_DEVICE_PACKET_MODE = 44,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Data acquisition process can be delayed (from trigger event).
	  * 
	  * When device work in syncrhonization mode, one can set
	  * time interval (RshInitMemory::startDelay field), and
	  * when synchronization event will be triggered, data writing
	  * will start not immediately, but after \b startDelay time elapsed.\n
	  * This setting is opposite to using RshInitMemory::preHistory.
	  * 
	  * \see
	  * RshInitMemory | \link page_Synchronization Synchronization\endlink
	  * 
	  * \~russian
	  * \brief
	  * Сбор данных может быть начат с задержкой (относительно события синхронизации)
	  * 
	  * Если устройство работает в режиме ожидания события синхронизации, можно задать
	  * интервал времени (поле RshInitMemory::startDelay), определяющий задержку старта.
	  * Когда будет получено событие синхронизации, запись данных в буфер начнется не
	  * мгновенно, а через заданное в поле \b startDelay время. \n
	  * Эта опция, по сути, "предыстория наоборот"
	  * (предыстория задается в поле RshInitMemory::preHistory).	
	  * 
	  * \see
	  * RshInitMemory | \link page_Synchronization Синхронизация\endlink
	  */
	 RSH_CAPS_DEVICE_START_DELAY = 45,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Data acquisition can be started from master device.
	  * 
	  * Using RshInitADC::Master as RshInitADC::startType,
	  * one can run device as slave. After call to IRshDevice::Start()
	  * method device will be in waitng state (like synchronization),
	  * but wait for signal from master device.
	  * 
	  * \remarks
	  * This feature is mostly used in systems where several identical
	  * devices are used for syncrhonious data acquisition. Special link
	  * between devices is required for this feature to work.
	  * 
	  * \~russian
	  * \brief
	  * Сбор данных может быть запущен от ведущего устройства.
	  * 
	  * Задав RshInitADC::Master в качестве источника запуска в поле RshInitADC::startType,
	  * можно сделать устройство "ведомым" (slave). После вызова метода IRshDevice::Start(),
	  * устройство будет находиться в режиме ожидания (как при использовании синхронизации),
	  * и сбор данных начнется только при получении специального сигнала от ведущего (Master)
	  * устройства
	  * 
	  * \remarks
	  * Даная возможность чаще всего применяется в составных системах, где несколько 
	  * одинаковых устройств используются для синхронного сбора данных. Необходимо
	  * соединять ведущее и ведомое (или ведомые) устройства специальным кабелем,
	  * чтобы система заработала в таком режиме.
	  *
	  */
	 RSH_CAPS_DEVICE_SLAVE_MASTER_SWITCH = 46,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Device's channels are synchronous.
	  * 
	  * If this flag is active, the device have separate ADC for each
	  * of analog channels, all ADCs are started by common clock signal
	  * and data from all channels acquired simultaniously.\n
	  * If opposite is true, device only have one ADC and channels are multyplexed.
	  * All samples have intervals equal to 1/F between them, where F is sampling
	  * frequency.
	  * 
	  * \remarks
	  * If device dont support this feature, its maximum frequency is always divided
	  * by number of channels used. For example, if device have maximum sampling rate equal
	  * to 500kHz, when using 2 channels one can only set RshInitADC::frequency field
	  * to 250kHz.
	  * 
	  * \see
	  * RshInitADC
	  * 
	  * \~russian
	  * \brief
	  * Аналоговые каналы устройства - синхронные.
	  * 
	  * Если данный флаг активен, устройство имеет свой собственный АЦП 
	  * на каждом из аналоговых каналов, все эти АЦП тактируются из одного
	  * источника, и данные со всех каналов собираются синхронно.\n
	  * Если же верно обратное, устройство имеет только один АЦП и аналоговые
	  * каналы оцифровываются по очереди (мультиплексируются). При этом
	  * все отсчеты отделены друг от друга по времени на величину 1/F,
	  * где F - частота дискретизации.
	  * 
	  * \remarks
	  * Если устройство не поддерживает данную опцию (каналы не синхронны),
	  * максимальная частота дискретизации всегда делится на количество активных
	  * (участвующих в сборе данных) каналов. Например, если максимальная частота
	  * дискретизации устройства составляет 500кГц, при использовании двух каналов
	  * максимально возможное значение частоты в поле RshInitADC::frequency 
	  * будет равно 250кГц.
	  * 
	  * \see
	  * RshInitADC
	  */
	 RSH_CAPS_DEVICE_SYNCHRO_CHANNELS = 47,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * ADC can be sampled by external signal source.
	  * 
	  * To turn on this feature use RshInitADC::FrequencyExternal bit
	  * in RshInitADC::startType field of initialization structure.
	  * One can combine this flag
	  * (using OR state) with some other startType flags, like 
	  * RshInitADC::Timer or RshInitADC::Internal.\n
	  * Parameters of signal to use as sampling source can be find
	  * in device's user manual.
	  * 
	  * \remarks
	  * When using this feature, RshInitADC::frequency field is still
	  * used (in most devices) to determine what frequency divider will
	  * be used.\n
	  * For example, if maximum sampling rate for device is 500kHz,
	  * and 150кHz external sampling source is used, when RshInitADC::frequency is
	  * set to 250kHz, then divider = 500/250 = 2 will be applyed to external frequency 
	  * signal, producing 150/2 = 75kHz sample rate.
	  * 
	  * \~russian
	  * \brief
	  * АЦП может тактироваться из внешнего источника.
	  * 
	  * Чтобы включить эту возможность, нужно установить бит RshInitADC::FrequencyExternal
	  * в поле RshInitADC::startType структуры инициализации. Можно комбинировать
	  * этот режим (используя логическое ИЛИ) с другими флагами, например RshInitADC::Timer,
	  * RshInitADC::Internal.\n
	  * Требования к сигналу (амплитуда, скважность, полярность и пр.) описаны
	  * в руководстве пользователя для каждого конкретного устройства.
	  * 
	  * \remarks
	  * При использовании данной возможности, поле RshInitADC::frequency структуры 
	  * инициализации все еще актуально (по крайней мере, для большинства устройств),
	  * т.к. заданная в нем частота используется для вычисления значения делителя частоты.\n
	  * Например, если максимальная частота дискретизации устройства составляет 500кГц,
	  * в качестве внешней тактовой частоты используется сигнал с частотой 150кГц, 
	  * а в поле RshInitADC::frequency задана частота 250кГц, при оцифровке будет использовано
	  * значение делителя частоты равное 500/250 = 2. Таким образом, получим, что реальная частота
	  * дискретизации будет равна 150/2 = 75кГц.
	  * 
	  */
	 RSH_CAPS_DEVICE_EXTERNAL_FREQUENCY = 48,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Sampling rate can be changed after trigger event.
	  * 
	  * If this feature is available, one can use two
	  * different sampling rates for "prehistory" and "data"
	  * parts of the buffer. History sampling rate has two fixed values F1 = Fmax
	 * and F2 = Fmax/8. See device documentation for more details.	  
	  * One can turn this feature on using RshInitMemory::FrequencySwitchToMaximum 
	  * or RshInitMemory::FrequencySwitchToMinimum flag
	  * in RshInitMemory::controlSynchro field of initialization structure. 
	  * 
	  * \see
	  * RSH_CAPS_DEVICE_PREHISTORY | \link page_Synchronization Synchronization\endlink
	  * 
	  * \~russian
	  * \brief
	  * Доступна возможность переключения частоты дискретизации после получения события синхронизации.
	  * 
	  * Если доступна данная возможность, можно использовать две разные частоты
	  * для "предыстории" и "истории" данных в буфере. Частота предыстории задается как обычно 
	  * (поле <b>frequency</b> структуры инициализации), а частота истории может быть переключена либо
	  * на максимальную для данного устройства частоту (Fmax), либо на частоту Fmax/8.\n
	  * Включить этот режим работы можно, используя флаги RshInitMemory::FrequencySwitchToMinimum
	  * и RshInitMemory::FrequencySwitchToMaximum в поле RshInitMemory::controlSynchro
	  * структуры инициализации RshInitMemory.
	  * 	
	  * \see
	  *  RSH_CAPS_DEVICE_PREHISTORY | \link page_Synchronization Синхронизация\endlink
	  */
	 RSH_CAPS_DEVICE_FREQUENCY_SWITCH_PREHISTORY = 49,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * One can select what channel (channels) will be used in double (quadro) frequency mode.
	  * 
	  * If this feature is available, one can specify which channel (or channels) will be used
	  * when double frequency mode is activated. If not, zero channel (or even channels if there
	  * are more than two of them) will always selected for double frequency mode.
	  * Channel selection is performed using standart RshChannel::Used flag in
	  * RshInitMemory::channels list.
	  * 
	  * \remarks
	  * This feature is relevant for quadro frequency too, one (obvious) except is that
	  * one can select only one channel from every four.
	  * 
	  * \see
	  * RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE | \link IRshDevice_DoubleFreqMode_EN.cpp Init parameters example\endlink
	  * 
	  * \~russian
	  * \brief
	  * Можно выбрать канал (каналы), который будут использоваться в режиме удвоения (учетверения) частоты.
	  * 
	  * Если доступна данная возможность, можно указать, какой канал (или каналы) будет использоваться
	  * в режиме удвоения частоты. По умолчанию, всегда используется нулевой канал (или четные каналы,
	  * если их количество больше двух). Выбор каналов осуществляется с помощью стандартного флага
	  * RshChannel::Used в списке RshInitMemory::channels структуры инициализации.
	  * 
	  * \remarks
	  * Данная возможность также актуальна и для режима учетверения, за исключением того, что можно
	  * выбрать один канал из каждых четырех, а не два, как в режиме удвоения.
	  * 
	  * \see
	  * RSH_CAPS_DEVICE_DOUBLE_FREQUENCY_MODE | \link IRshDevice_DoubleFreqMode_RU.cpp Пример задания параметров\endlink
	  */
	 RSH_CAPS_DEVICE_FREE_CHANNEL_SELECT_IN_EXT_MODE = 50,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Device can be programmably configure to acquire data in unipolar/ bipolar mode.
	  * 
	  * Devices work in unipolar mode by default.
	  * One need set RshInitDMA::DiffMode flag of RshInitDMA::control field to set
	  * device in bipolar mode.
	  * 
	  * \remarks
	  * Channels number will be divided by 2, and input lines for analog channels
	  * must be connected according user manual.
	  * 
	  * \see
	  * RshInitDMA
	  * 
	  * \~russian
	  * \brief
	  * Доступна возможность программно переключаться между однополюсным/дифференциальным режимом.
	  * 
	  * По умолчанию, устроства работают в однополюсном режиме. Чтобы задействовать 
	  * дифференциальный режим работы, нужно установить флаг RshInitDMA::DiffMode
	  * в поле RshInitDMA::control структуры инициализации.
	  * 
	  * \remarks
	  * При включении дифференциального режима количество каналов становится меньше в два раза,
	  * так как оцифровывается разностное напряжение двух входов.
	  * Кроме того, требуется выполнить подключение сигналов в соответствии со схемой
	  * подключения дифференциальных входов согласно руководству пользователя.
	  * 
	  * \see
	  * RshInitDMA
	  */
	 RSH_CAPS_DEVICE_DIFFERENTIAL_INPUT_MODE = 51,	


	 /*! 	  
	  * 
	  * \~english
	  * \brief
	  * There is a flash memory unit onboard for device information.
	  * 
	  * This flag indicates that device has onboard flash memory which is used 
	  * for additional information such as serial number. 
	  *
	  * \~russian
	  * \brief
	  * Устройство имеет энергонезависимую память (флэш), которая содержит дополнительную информацию.
	  * 
	  * Наличие данного флага означает, что устройство располагает дополнительной памятью, в которую
	  * может быть записан заводской номер платы, различные настроечные коэффициенты и другая 
	  * информация. Как правило, информация записывается на этапе настройки и в процессе эксплуатации
	  * доступна только для чтения.
	  *
	  */
 	 RSH_CAPS_DEVICE_FLASH_INFO_ONBOARD = 52,


	 /*!
	  * 
	  * \~english
	  * \brief
	  * Device have GPS module
	  * 
	  * One can obtain GPS data using IRshDevice::Get() method
	  * with ::RSH_GET_DEVICE_GPS_DATA or ::RSH_GET_DEVICE_GPS_DATA_UTF16 constants.
	  * 
	  * \remarks
	  * Format of GPS sentance string is device (and module) dependend,
	  * see device manual for details.
	  * 
	  * \~russian
	  * \brief
	  * Устройство имеет GPS-модуль
	  * 
	  * Получить данные GPS можно, вызвав метод IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_GPS_DATA или ::RSH_GET_DEVICE_GPS_DATA_UTF16.
	  * 
	  * \remarks
	  * Формат строки с данными зависит от устройства и используемого 
	  * модуля, все подробности приведены в описании устройства.
	  * 
	  */
	 RSH_CAPS_DEVICE_GPS_MODULE_INSTALLED = 53,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Device supports automatic restart
	  * 
	  * Device can be proggrammed in such a way that it
	  * will automatically restart data acquisition using
	  * internal timing interval. This interval can 
	  * be set using IRshDevice::Get() method with
	  * ::RSH_GET_DEVICE_AUTO_START_INTERVAL_SET parameter.\n
	  * 
	  * \remarks
	  * This mode is not continuous mode. Data buffers obtained
	  * are not continuous. The only difference from "Start-Stop"
	  * mode is that one do not have to start data acquisition for
	  * each buffer - device hardware will do it.\n
	  * From programming point of view, however, work process look 
	  * much like work in continuous mode - one have to init device,
	  * start it, and then wait to interrupt events (one for each bufer)
	  * infinitely, until IRshDevice::Stop() method is called.
	  * 
	  * \~russian
	  * \brief
	  * Устройство поддерживает режим автоматического запуска
	  * 
	  * Устройство может быть запрограммировано таким образом, что
	  * сбор данных будет запускаться автоматически, с заданным интервалом.
	  * Интервал запуска можно задать, используя метод IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_AUTO_START_INTERVAL_SET.
	  * 
	  * \remarks
	  * Данный режим работы - это \b НЕ непрерывный режим. Каждый блок данных, 
	  * получаемый от устройства, независим и не связан с предыдущим.
	  * Единственное отличие от стандартного режима "Старт-Стоп" в том, что
	  * не нужно запускать сбор каждый раз - устройство будет делать это 
	  * автоматически.\n
	  * С программной точки зрения, однако, процесс работы с устройством
	  * выглядит очень похожим на работу в непрерывном режиме - нужно
	  * задать параметры сбора данных (в том числе и интервал опроса), запустить
	  * сбор и затем получать данные длительное время, ожидая событие готовности
	  * для каждого собранного буфера. Процесс сбора данных может быть остановлен
	  * вызовом метода IRshDevice::Stop().
	  *
	  * 
	  */
	 RSH_CAPS_DEVICE_AUTO_START_MODE = 54,


	 /*!
	  * 
	  * \~english
	  * \brief
	  * Digital line data can be contained within analog data.
	  * 
	  * Device digital lines data (input digital port for ADC devices) can
	  * be placed in last significant bits of analog data.
	  * 
	  * \remarks
	  * Use special IRshDevice::GetData() flag ( ::RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT)
	  * to transfer digital port data with analog data (for ADC devices) or to output
	  * digital lines (for GSPF devices). See ::RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT for details.
	  * 
	  * \see
	  * RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT
	  * 
	  * \~russian
	  * \brief
	  * Цифровые данные могут передаваться вместе с аналоговыми.
	  * 
	  * Устройство имеет возможность получать данные со своего цифрового порта или
	  * входных цифровых линий вместе с аналоговыми данными. Цифровые данные помещаются
	  * в несколько младших битов каждого слова данных.
	  * 
	  * \remarks
	  * Используется специальный флаг  ( ::RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT) при вызове
	  * метода IRshDevice::GetData() для того, чтобы цифровые данные не были отмаскированы.
	  * См. ::RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT для более подробного описания.
	  * 
	  * \see
	  * RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT
	  * 
	  */
	 RSH_CAPS_DEVICE_DIGITAL_PORT_DATA_WITH_ANALOG_DATA = 55,

	 /*! 	  
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow automatic calibration perform.
	  * 
	  * This flag indicates that device can be calibrated programmably,
	  * with use of external signal generation and measurement devices.\n
	  * Do not confuse with ::RSH_CAPS_DEVICE_AUTO_CALIBRATION (automatic
	  * calibration of device during runtime). This flag is for preproduction
	  * process only.
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для проведения автоматической настройки и калибровки устройства.
	  * 
	  * Наличие данного флага означает, что устройство может быть откалибровано (настройка внутренних
	  * коэффициентов) программно, с использованием внешнего источника сигнала
	  * и эталонного измерительного прибора.\n
	  * Данная возможность не связана с наличием флага ::RSH_CAPS_DEVICE_AUTO_CALIBRATION
	  * (автоматическая подстройка нуля в процессе работы). Режим автоматической 
	  * калибровки используется только при производстве и ремонте устройств.
	  * 
	  */
	 RSH_CAPS_SOFT_CALIBRATION_IS_AVAILABLE = 512,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow data acquisition in "start-stop" mode.
	  * 
	  * Device can be programmed to acquire data in "Start-Stop"
	  * mode. In this mode only one data block of predefined size
	  * will be acquired and transfered to user. This is most 
	  * common scenario of work.
	  * 
	  * \see
	  * RshInitDMA | RshInitMemory
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для осуществления сбора данных в режиме "старт-стоп".
	  * 
	  * Устройство может быть запрограммировано для сбора данных
	  * в режиме "Старт-Стоп". В этом режиме происходит одиночный
	  * запуск устройства, сбор одного блока данных с заданными 
	  * параметрами (частота дискретизации, размер и т.д.) и остановка
	  * устройства. Этот сценарий работы является наибоелее распространенным.
	  * 
	  * \see
	  * RshInitDMA | RshInitMemory
	  *
	  */
	 RSH_CAPS_SOFT_GATHERING_IS_AVAILABLE = 513,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow continious data acquisition.
	  * 
	  * In this mode device's ADC is started once, and then acquire
	  * data continiously, generating interrupt each time
	  * data block is ready. This process can be active long
	  * time, and stops only when IRshDevice::Stop() method is called.
	  * 
	  * \remarks
	  * Due to brandwidth limitation for computer interfaces,
	  * this mode only available for low frequency (10MHz maximum) devices
	  * 
	  * \see
	  * RshInitDMA
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для осуществления сбора данных в непрерывном режиме
	  * 
	  * В этом режиме АЦП запускается один раз, и затем оцифровывает
	  * входные сигналы непрерывно, генерируя прерывание каждый раз, 
	  * когда готова очередная порция данных. Этот процесс может продолжаться
	  * долгое время (теоретически, бесконечно) и будет остановлен только
	  * при вызове метода IRshDevice::Stop().
	  * 
	  * \remarks
	  * Из-за аппаратных ограничений по пропускной способности различных
	  * интерфейсов, этот режим доступен только для относительно
	  * низкочастотных устройств (до 10МГц).
	  * 
	  * \see
	  * RshInitDMA
	  *
	  */
	 RSH_CAPS_SOFT_PGATHERING_IS_AVAILABLE = 514,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow control of digital port.
	  * 
	  * Using IRshDevice::Init() method and RshInitPort structure
	  * one can write and read data from digital port.
	  * Information about digital port can be obtained using
	  * IRshDevice::Get() method with ::RSH_GET_DEVICE_PORT_INFO parameter.	
	  * 
	  * \see
	  * RshInitPort | RshInitPort | RshPortInfo
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для управления цифровым портом.
	  * 
	  * Используя метод IRshDevice::Init() и структуру инициализации
	  * RshInitPort можно читать и записывать данные в цифровой порт устройства.
	  * Получить информацию о цифровом порте можно, используя метод IRshDevice::Get()
	  * с параметром ::RSH_GET_DEVICE_PORT_INFO.
	  * 
	  * \see
	  * RshInitPort | RshInitPort | RshPortInfo
	  *
	  */
	 RSH_CAPS_SOFT_DIGITAL_PORT_IS_AVAILABLE = 515,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow signal generation.
	  * 
	  * Using RshInitGSPF stucture one can set generation parameters,
	  * and then send data buffer to device using IRshDevice::GetData() method.
	  * 
	  * \see
	  * RshInitGSPF
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для генерации сигнала.
	  * 
	  * Используя структуру инициализации RshInitGSPF можно задать параметры
	  * генерации сигнала, и затем отправить сформированный буфер данных
	  * с сигналом в устройство, используя метод IRshDevice::GetData().
	  * 
	  * \see
	  * RshInitGSPF
	  *
	  */
	 RSH_CAPS_SOFT_GENERATION_IS_AVAILABLE = 516,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitMemory initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is usually used for high frequency devices with internal memory installed.
	  *
	  * \see
	  * RshInitMemory | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitMemory поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура обычно используется для высокочастотных устройств сбора
	  * данных с установленной собственной памятью.
	  *
	  * \see
	  * RshInitMemory | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_MEMORY = 517,

	  /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitDMA initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is usually used for low frequency devices.
	  *
	  * \see
	  * RshInitDMA | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitDMA поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  * 
	  * \remarks
	  * Данная структура обычно используется для низкочастотных устройств сбора
	  * данных. Используя эту структуру, можно организовать сбор данных в непрерывном режиме.
	  * 
	  * \see
	  * RshInitDMA | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_DMA = 518,

	  /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitGSPF initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is used for programming GSPF family devices.
	  *
	  * \see
	  * RshInitGSPF | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitGSPF поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура используется для программирования устройств
	  * серии ГСПФ.
	  *
	  * \see
	  * RshInitGSPF | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_GSPF = 519,
	 
	  /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitVoltmeter initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is used for programming VISA-based digital voltmeters.
	  *
	  * \see
	  * RshInitVoltmeter | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitVoltmeter поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура используется для программирования цифровых
	  * вольтметров с интерфейсом VISA.
	  *
	  * \see
	  * RshInitVoltmeter | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_VOLTMETER = 520,

	  /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitTimer initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is used for direct control of counter timer.
	  *
	  * \see
	  * RshInitTimer | IRshDevice::Init() | RSH_CAPS_DEVICE_TIMER_8254
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitTimer поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура используется для прямого управления
	  * программируемым счетчиком-таймером устройства.
	  *
	  * \see
	  * RshInitTimer | IRshDevice::Init() | RSH_CAPS_DEVICE_TIMER_8254
	  */
	 RSH_CAPS_SOFT_INIT_TIMER = 521,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Abstraction library contains methods that allow use of software stoboscope.
	  * 
	  * Stroboscope only work with synchronization and periodic signals.
	  * Obtaining information about precise time of synchronization event
	  * and interpolate several signal realisation to one output signal
	  * with better resolution in time domain.	 
	  * 
	  * \~russian
	  * \brief
	  * Библиотека абстракции содержит методы для реализация программного стробоскопа.
	  * 
	  * Стробоскопирование работает только для периодических сигналов, 
	  * и при включенной синхронизации. Получая информацию о точном моменте срабатывания
	  * синхронизации, можно из нескольких реализации периодического сигнала
	  * построить одну, но с более высоким временным разрешением.
	  *	 
	  */
	 RSH_CAPS_SOFT_STROBOSCOPE = 522,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitDAC initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is used for DAC control
	  *
	  * \see
	  * RshInitDAC | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitDAC поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура используется для управления ЦАПами.
	  *
	  * \see
	  * RshInitDAC | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_DAC = 523,

	  /*!
	  * 
	  * \~english
	  * \brief
	  * RshInitPort initialization structure is supported by abstraction library.
	  * 
	  * One can use this structure as parameter for IRshDevice::Init() method.	 
	  * 
	  * \remarks
	  * This structure is used for digital port access
	  *
	  * \see
	  * RshInitPort | IRshDevice::Init()
	  * 
	  * \~russian
	  * \brief
	  * Структура инициализации RshInitPort поддерживается библиотекой абстракции.
	  * 
	  * Использовать эту структуру для передачи параметров можно
	  * в методе IRshDevice::Init().
	  *
	  * \remarks
	  * Данная структура используется для управления цифровым портом.
	  *
	  * \see
	  * RshInitPort | IRshDevice::Init()
	  */
	 RSH_CAPS_SOFT_INIT_PORT = 524,

	 /*!
	  * 
	  * \~english
	  * \brief
	  * Internal device parameters can be tuned using this abstraction library.
	  * 
	  * Special private set of methods and structures is used to change internal device
	  * parameters.
	  * Tuner is used only for initial device configuration and pre-sale preparation.
	  * 
	  * 
	  * \~russian
	  * \brief
	  * Внутренние настройки устройства могут быть изменены с использованием данной библиотеки абстракции.
	  * 
	  * Для изменения значений внутренних настроечных коэффициентов устройства используется
	  * специальный набор методов и структур, которые являются закрытыми.
	  * Тюнер используется только при первоначальной настройке и предпродажной подготовке устройства.
	  *
	  */
	 RSH_CAPS_SOFT_TUNER_MODE_IS_AVAILABLE = 525,


	 /*!
	  * \~english
	  * \brief
	  * Maximum number of values in RSH_CAPS enum.
	  * \~russian
	  * \brief
	  * Максимальное количество значений в перечислении RSH_CAPS.
	  */
	 RSH_CAPS_MAX = 1024
 } RSH_CAPS;



 /*!
 * 
 * \~english
 * \brief
 * Connect modes.
 *
 * \see
 * IRshDevice::Connect().
 * 
 * \~russian
 * \brief
 * Варианты подключения к устройству.
 * 
 * \see
 * IRshDevice::Connect().
 */
typedef enum
{
	/*!
	 * \~english
	 * \brief
	 * Connect to device by device index.
	 *
	 * If IRshDevice::Connect() is used with this code,
	 * method will use device index which was assigned to selected device
	 * by the driver.
	 *
	 * \~russian
	 * \brief
	 * Подключение к устройству по его индексу.
	 *
	 * Если метод IRshDevice::Connect() вызывается с использованием
	 * этого параметра, то подключение к устройству происходит в соответствии с построенной 
	 * драйвером таблицей устройств. Нумерация устройств ведется последовательно начиная с 1.
	 */
	RSH_CONNECT_MODE_BASE  = 0,

	/*!
	 * \~english
	 * \brief
	 * Connect to device by device serial number.
	 *
	 * If IRshDevice::Connect() is used with this code,
	 * method will use specified device serial number to connect to device.
	 *
	 * \~russian
	 * \brief
	 * Подключение к устройству по его заводскому номеру.
	 *
	 * Если метод IRshDevice::Connect() вызывается с использованием
	 * этого параметра, то подключение производится к устройству с указанным 
	 * заводским номером.
	 *
	 */
	RSH_CONNECT_MODE_SERIAL_NUMBER  = 1,

	/*!
	 * \~english
	 * \brief
	 * Connect via IP
	 *
	 * This mode is used by some ethernet devices. 
	 * One can specify ip adress and port in 
	 * string, for example "192.168.0.5:2034".
	 *
	 * \~russian
	 * \brief
	 * Подключение к устройству по IP адресу
	 *
	 * Подключение к устройству по IP-адресу.
	 * Данный режим используется некоторыми устройствами
	 * с сетевым интерфейсом.\n
	 * IP-адрес и порт  можно задать в виде строки - например
	 * "192.168.0.5:2034" .
	 *
	 */
	RSH_CONNECT_MODE_IP_ADDRESS = 2,

	/*!
	 * \~english
	 * \brief
	 * Connect to PLX device
	 *
	 * This mode is used to connect to specific PLX device\n
	 * Connection string format: №device;PlxChipType (RshDeviceKey::S8*)\n
	 * example:  RshDeviceKey( "0;9054" ) - connects to the first device in the system with a Plx 9054 chip. 
	 *
	 * \~russian
	 * \brief
	 * Подключение к PLX устройству по типу чипа
	 *
	 * Данный режим используется для подключения к любым чипам PLX напрямую.\n
	 * Формат строки подключения: №устройства;типчипа (RshDeviceKey::S8*)
	 * пример:  RshDeviceKey( "0;9054" ) - подключается к первому найденному устройству в системе с чипом Plx 9054.
	 *
	 */
	RSH_CONNECT_MODE_PLXCHIP_TYPE = 16
	
} RSH_CONNECT_MODES;


/*!
 * 
 * \~english
 * \brief
 * Initialization modes.
 *
 * \see
 * IRshDevice::Init().
 * 
 * \~russian
 * \brief
 * Варианты инициализации.
 * 
 * \see
 * IRshDevice::Init().
 */
typedef enum
{
	/*!
	 * \~english
	 * \brief
	 * Check initialization structure and return.
	 *
	 * If IRshDevice::Init() is used with this code,
	 * method will only check (and correct) parameters in
	 * initialization structure.
	 *
	 * \~russian
	 * \brief
	 * Только проверка параметров инициализации в структуре.
	 *
	 * Если метод IRshDevice::Init() вызывается с использованием
	 * этого параметра, то результатом его работы будет только
	 * проверка и корректировка параметров в структуре инициализации.
	 */
	RSH_INIT_MODE_CHECK  = 0,

	/*!
	 * \~english
	 * \brief
	 * Correct structure parameters and do hardware initialization.
	 * If IRshDevice::Init() is used with this code,
	 * method will check (and correct) parameters in
	 * initialization structure and then send those parameters
	 * to device.
	 * \~russian
	 * \brief
	  * \brief
	 * Проверка параметров в структуре и фактическая инициализация.
	 *
	 * Если метод IRshDevice::Init() вызывается с использованием
	 * этого параметра, то параметры инициализации в структуре
	 * будут откорректированы, и после этого отправлены в устройство.
	 *
	 */
	RSH_INIT_MODE_INIT  = 1,

	RSH_INIT_MODE_REINIT = 2
} RSH_INIT_MODES;


/*!
 * 
 * \~english
 * \brief
 * Additional data transfer flags for IRshDevice::GetData() method.
 * 
 * Flags from this enum can be combined using OR statement,
 * and are used to control data conversation process.
 * 
 * 
 * \see
 * IRshDevice::GetData()
 * 
 * \~russian
 * \brief
 * Дополнительные флаги преобразования данных для метода IRshDevice::GetData().
 * 
 * Флаги из этого списка можно комбинировать по ИЛИ.
 * Для некоторых устройств, данные флаги позволяются получить
 * (или отправить) дополнительню информацию вместе с данными,
 * или изменить параметры процесса преобразования данных.
 * 
 * \see
 * IRshDevice::GetData()
 * 
 */
typedef enum
{
	/*!
	 * 
	 * \~english
	 * \brief
	 * No additional flags are used.
	 * 
	 * You can omit this flag, because its default value of 
	 * IRshDevice::GetData() \b flags parameter.
	 * 
	 * \~russian
	 * \brief
	 * Дополнительные флаги не используются.
	 * 
	 * Можно не прописывать данный флаг, поскольку он ставится
	 * по умолчанию в качестве параметра \b flags метода IRshDevice::GetData().
	 * 
	 */
	RSH_DATA_MODE_NO_FLAGS = 0x0,

	/*!
	 * 
	 * \~english
	 * \brief
	 * State of digital input lines is transfered within data.
	 * 
	 * Some devices have possibility to write ditial port bits
	 * in data word with analog data input.\n
	 * For example, if we have device with 12 bit ADC, which use
	 * 16 bit bus for data transfer, 4 last sagnificant bits can be
	 * used for 4 digital lines data.\n
	 * 
	 * \remarks
	 * When using floating point buffer (::RSH_BUFFER_DOUBLE) in
	 * IRshDevice::GetData() method, this flag will be ignored,
	 * becuase analog input is converted to volts.
	 *
	 * \see RSH_CAPS_DEVICE_DIGITAL_PORT_DATA_WITH_ANALOG_DATA | \link IRshDevice_GetData_DigitalInput_EN.cpp Use example\endlink
	 * 
	 * \~russian
	 * \brief
	 * Передача состояния входных линий цифрового порта вместе с данными.
	 * 
	 * У некоторых устройств есть возможность записи данных цифровых портов
	 * в слово данных аналоговых каналов. \n
	 * Например, если устройство имеет разрядность 12 бит и использует внутреннюю
	 * шину 16 бит для передачи данных, 4 младших бита могут быть использованы
	 * для записи состояния четырех входных линий цифрового порта.\n	
	 * 
	 * \remarks
	 * При использовании в методе IRshDevice::GetData()  буфера из чисел с плавающей точкой
	 * (::RSH_BUFFER_DOUBLE), данный флаг будет проигнорирован, т.к.
	 * аналоговые данные преобразуются в вольты.	
	 *
	 * \see RSH_CAPS_DEVICE_DIGITAL_PORT_DATA_WITH_ANALOG_DATA | \link IRshDevice_GetData_DigitalInput_RU.cpp Пример использования \endlink 
	 * 
	 */
	RSH_DATA_MODE_CONTAIN_DIGITAL_INPUT = 0x00001,

	/*!
	 * 
	 * \~english
	 * \brief
	 * Output TTL signal on digital lines simulteniously with analog output.
	 * 
	 * Two last sagnificant bits of each data sample sended
	 * to GSPF device using IRshDevice::GetData() method
	 * will be used as state of two ditial TTL lines.\n
	 * Signal on that lines will be changed at the same time
	 * as next sample is converted by DAC. So, time parameters
	 * of generated TTL-signal will depend on used sampling rate
	 * and buffer size.
	 * 
	 * \~russian
	 * \brief
	 * Вывод TTL-совместимого сигнала на цифровые выходы одновременно с выводом аналоговых данных.
	 * 
	 * Два младших бита каждого отсчета (слова) данных, отправленных
	 * на устройство ГСПФ с помощью метода IRshDevice::GetData()
	 * будут использоваться для вывода на две TTL-совместимых цифровых линии.\n
	 * Состояние линий будет обновляться одновременно с выдачей очередного
	 * значения из буфера на ЦАП, т.е. временные характеристики выдаваемого
	 * TTL сигнала будут определяться установленной частотой дискретизации
	 * и размером буфера.
	 *
	 */
	RSH_DATA_MODE_GSPF_TTL = 0x10000

} RSH_DATA_MODES;

/*!
 * 
 * \~english
 * \brief
 * Languages list.
 *
 * \~russian
 * \brief
 * Список языков.
 *
 */
typedef enum
{
	/*!
	 * 
	 * \~english
	 * \brief
	 * English.
	 *
	 * \~russian
	 * \brief
	 * Английский.
	 *
	 */
    RSH_LANGUAGE_ENGLISH = 0,

	/*!
	 * 
	 * \~english
	 * \brief
	 * Russian.
	 *
	 * \~russian
	 * \brief
	 * Русский.
	 *
	 */
    RSH_LANGUAGE_RUSSIAN = 1

} RSH_LANGUAGE;

#endif //__RSH_CONSTS_H__