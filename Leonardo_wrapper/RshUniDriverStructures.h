/*!
* \copyright JSC "Rudnev-Shilyaev"
* 
* \file RshUniDriverStructures.h
* \date 28.07.2014
* \version 1.0 [SDK 2.00]
* 
* \~english
* \brief
* Here you can find the structures which are intended for use with RshUniDriver.dll.
* 
* \~russian
* \brief
* В данном файле присутствуют описания структур и констант используемых для работы с RshUniDriver.dll.
* 
*/

#ifndef __RSH_UNIDRIVER_STRUCTURES_H__
#define __RSH_UNIDRIVER_STRUCTURES_H__

#include "Rsh.h"
#include "RshDefChk.h"
#include "RshConsts.h"

#pragma pack(push, 1)	
/////////////////////////////////////////////////////////////////////
// Коды типов данных
//

/////////////////////////////////////////////////////////////////////
// Буфер данных.
// Данная структура используется в функции UniDriverGetData.
//

//! Буфер данных
typedef struct
{
	RshDataTypes	type;  //!< тип данных буфера
	unsigned int	size;  //!< данное поле используется после вызова UniDriverGetData(), чтобы отразить реальное количество скопированных данных в буфер
	unsigned int	psize; //!< количество элементов в буфере
	unsigned int	id;    //!< уникальный идентификатор буфера (поле нельзя трогать, оно предназначено только для служебного использования)
	void*			ptr;   //!< указатель на буфер

} URshBuffer;

/////////////////////////////////////////////////////////////////////
// Данные структуры используютя для передачи данных
// в функции UniDriverGet и некоторых других
//

//! Общий шаблон (тип)
typedef struct
{
	RshDataTypes	type;   //!< тип данных 
	void*			data;   //!< данные 
} URshType;

//! Число с плавающей точкой (8 байт)
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshDouble)
	double			data;   //!< данные 
} URshTypeDoubleStructure;

//! Знаковое целое 1 байт
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshS8)
	char			data;   //!< данные 
} URshTypeS8Structure;

//! Беззнаковое целое 1 байт
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshU8)
	unsigned char	data;   //!< данные 
} URshTypeU8Structure;

//! Знаковое целое 2 байта
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshS16)
	short			data;   //!< данные 
} URshTypeS16Structure;

//! Беззнаковое целое 2 байта
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshU16)
	unsigned short	data;   //!< данные 
} URshTypeU16Structure;

//! Знаковое целое 4 байта
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshS32)
	int				data;	//!< данные 
} URshTypeS32Structure;

//! Беззнаковое целое 4 байта
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshU32)
	unsigned int	data;   //!< данные 
} URshTypeU32Structure;

//! Указатель на беззнаковое целое 2 байта (UTF-16 строка)
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshU16P)
	unsigned short*	data;   //!< данные 
} URshTypeU16PointerStructure;

//! Указатель на знаковое целое 1 байт (ansi строка)
typedef struct
{
	RshDataTypes		type;	//!< тип данных (rshS8P)
	char*			data;   //!< данные 
} URshTypeS8PointerStructure;

struct URshBaseType
{
	unsigned int type;
};

/////////////////////////////////////////////////////////////////////
//Структуры с информацией о каналах и портах
//

//! Параметры аналогового канала устройства
typedef struct   
{
	unsigned int	gain;			//!< коэффициент усиления
	unsigned int	control;		//!< специфические настройки канала        
	double			adjustment;		//!< смещениe (в вольтах)
} URshChannel;

//! Параметры канала синхронизации устройства
typedef struct  
{
	unsigned int	gain;		//!< коэффициент усиления
	unsigned int	control;	//!< специфические настройки канала        
} URshSynchroChannel;

//! Информация о цифровом порте
typedef struct   
{
	unsigned int address;		  //!< регистр отвечающий за порт
	unsigned char bitSize;		  //!< разрядность порта
	char name[RSH_MAX_LIST_SIZE]; //!< название порта
} URshPortInfo;

//! Информация о цифровых портах устройства
typedef struct
{
	unsigned int type;						//код типа данных ( rshBoardPortInfo )
	URshPortInfo confs[RSH_MAX_LIST_SIZE];	//!< порты/регистры настройки
	URshPortInfo ports[RSH_MAX_LIST_SIZE];	//!< порты/регистры данных
	unsigned int totalConfs;
	unsigned int totalPorts;
} URshBoardPortInfo;

//! Запись/чтение данных из регистра.
typedef struct 
{
	unsigned int type; //код типа данных ( rshRegister )
	unsigned int size; //размер слова данных
	unsigned int offset; //адрес регистра (смещение)
	unsigned int value; //значение
}URshRegister;

/////////////////////////////////////////////////////////////////////
//Структуры инициализации
//

//! Структура инициализации для устройств типа "DMA"
typedef struct 
{
	unsigned int	type;			//код типа данных ( rshInitDMA )

	unsigned int	startType;		//!< настройки типа старта платы
	unsigned int	bufferSize;		//!< размер буфера в отсчётах (значение пересчитывается при инициализации в зависимости от сопутствующих настроек)
	double			frequency;		//!< частота дискретизации	

	unsigned int	dmaMode;		//!< режим работы DMA	
	unsigned int	control;		//!< специфические настройки для данного типа плат (например, диф режим)
	double			frequencyFrame;	//!< частота дискретизации	внутри пачки

	URshChannel		channels[RSH_MAX_LIST_SIZE]; //!< параметры каналов
	
	double			threshold;		//!< уровень синхронизации в Вольтах
	unsigned int	controlSynchro;	//!< специфические настройки синхронизации
} URshInitDMA;

//! Структура инициализации для устройств типа "Memory"
typedef struct 
{
	unsigned int	type;			//код типа данных ( rshInitMemory )

	unsigned int	startType;		//!< настройки типа старта платы
	unsigned int	bufferSize;		//!< размер буфера в отсчётах (значение пересчитывается при инициализации в зависимости от сопутствующих настроек)
	double			frequency;		//!< частота дискретизации	

	unsigned int	control;		//!< специфические настройки для данного типа плат (например, диф режим)

	unsigned int	preHistory;		//!< размер предыстории, может принимать значения от 0 до 15
	unsigned int	startDelay;		//!< задержка старта
	unsigned int	hysteresis;		//!< гистеризис
	unsigned int	packetNumber;	//!< количество пакетов размера bufferSize

	double			threshold;		//!< уровень синхронизации в Вольтах
	unsigned int	controlSynchro;	//!< специфические настройки синхронизации

	URshSynchroChannel channelSynchro; //<! настройки канала внешней синхронизации
	URshChannel channels[RSH_MAX_LIST_SIZE]; // параметры каналов
} URshInitMemory;

//! Структура инициализации для управления цифровым портом
typedef struct 
{
	unsigned int	type;		//код типа данных ( rshInitPort )

	unsigned int operationType; //!< Код операции
	unsigned int portAddress;   //!< Идентификатор порта
	unsigned int portValue;     //!< Значение
} URshInitPort;

//! Структура инициализации для управления ЦАПом
typedef struct 
{
	unsigned int	type;	//код типа данных ( rshInitDAC ) 

	unsigned int id;		//!< Идентификатор ЦАПа
	double voltage;			//!< Напряжение, которое нужно выдать на ЦАП
} URshInitDAC;

//! Структура инициализации для управления генераторами сигнала
typedef struct   
{
	unsigned int	    type;		//код типа данных ( rshInitGSPF )

	unsigned int		startType;	//!< тип запуска платы
	double				frequency;	//!< частота 
	unsigned int		attenuator;	//!< код аттенюатора
	unsigned int		control;	//!< настройки платы
} URshInitGSPF;

//! Структура инициализации для управления вольтметрами
typedef struct  
{
	unsigned int	type;			//код типа данных ( rshInitVoltmeter )

	unsigned int		startType;	//!< тип запуска
	unsigned int		bufferSize;	//!< размер буфера в отсчётах (значение пересчитывается при инициализации в зависимости от сопутствующих настроек)
	unsigned int		filter;		//!< использование фильтра
	unsigned int		control;	//!< настройки платы
}  URshInitVoltmeter;

//! Константы для поля control структуры URshChannel
enum URshChanControl
{
	URshChanControlNotUsed		= 0x0,		//!< канал не используется при оцифровке
	URshChanControlNoSynchro	= 0x0,		//!< по данному каналу не осуществляется синхронизация
	URshChanControlResist1MOm	= 0x0,		//!< сопротивление входа 1 МОм
	URshChanControlDC			= 0x0,		//!< состояние входa открытый
	URshChanControlFreqSingle	= 0x0,		//!< обычная частота
	URshChanControlICPPowerOff  = 0x0,		//!< отключить ICP питание канала

	URshChanControlUsed			= 0x1,		//!< канал используется
	URshChanControlSynchro		= 0x2,		//!< синхронизация по данному каналу
	URshChanControlAC			= 0x4,		//!< состояние входa закрытый
	URshChanControlResist50Om	= 0x8,		//!< сопротивление входа 50 Ом
	URshChanControlICPPowerOn   = 0x10,		//!< включить ICP питание канала

	URshChanControlFirstChannel = 0x10000,  //!< для некоторых плат данный флаг задаёт канал, который будет оцифрован первым
};

//! Константы для поля control структуры URshsynchroChannel
enum URshSyncChanControl
{
	URshSyncChanControlFilterOff	= 0x0,	//!< Выключить фильтр для канала внешней синхронизации
	URshSyncChanControlResist1MOm	= 0x0,	//!< сопротивление входа 1 МОм
	URshSyncChanControlDC			= 0x0,	//!< состояние входa открытый

	URshSyncChanControlAC			= 0x4,	//!< состояние входa закрытый
	URshSyncChanControlResist50Om	= 0x8,	//!< сопротивление входа 50 Ом
	URshSyncChanControlFilterLow	= 0x1,	//!< Включить фильтр низких частот для канала внешней синхронизации
	URshSyncChanControlFilterHigh	= 0x3,	//!< Включить фильтр высоких частот для канала внешней синхронизации
};

//! Режимы запуска устройства (поле startType структур инициализации)
enum URshStart
{
	URshStartTypeProgram			= 0x1,	//!< программный запуск
	URshStartTypeTimer				= 0x2,	//!< запуск по таймеру
	URshStartTypeExternal			= 0x4,	//!< использование внешней синхронизации
	URshStartTypeInternal			= 0x8,	//!< использование внутренней синхронизации
	URshStartTypeFrequencyExternal	= 0x10, //!< использование внешней частоты дискретизации
	URshStartTypeMaster				= 0x20	//!< старт от устройства-мастера в системах с несколькими устройствами  
};

//! константы для поля operationType структуры URshInitPort
enum URshPortOperationCode
{
	URshPortRead = 0,
	URshPortWrite = 1,
	URshPortWriteAND = 2,
	URshPortWriteOR = 3
};

//! Константы для поля control структуры URshInitDMA
enum URshInitDmaControl
{
	URshInitDmaControlStandartMode = 0x0,	//!< Дополнительные опции не используются

	URshInitDmaControlDiffMode = 0x1,		//!< Включение дифференциального режима работы 
	URshInitDmaControlFrameMode = 0x2,		//!< Включение кадрового режима сбора
	URshInitDmaControlMulSwitchStart = 0x4	//!< Переключение мультиплексора по старту
};

//! Константы для поля dmaMode структуры URshInitDMA
enum URshDmaMode
{
	URshInitDmaDmaModeSingle = 0x0,		 //!< Одиночный запуск
	URshInitDmaDmaModePersistent = 0x1	 //!< Непрерывный сбор
};

//! Константы для поля control структуры URshInitMemory
enum URshInitMemoryControl
{
	URshInitMemoryControlFreqSingle = 0x0,	//!< Обычный режим
	URshInitMemoryControlAutoStartOff = 0x0, //!<Автозапуск не используется 

	URshInitMemoryControlFreqDouble = 0x1,	//!< Удвоение частоты
	URshInitMemoryControlFreqQuadro = 0x2,	//!< Учетверение частоты
	URshInitMemoryControlAutoStartOn = 0x4  //!< Автоматический перезапуск 
};

//! Константы для поля controlSynchro структур URshInitMemory и URshInitDMA
enum URshInitADCControlSynchro
{
	URshInitADCFrequencySwitchOff = 0x0, //!<Предыстория и история собираются с одной частотой дискретизации
	URshInitADCSlopeFront = 0x0, //!<Синхронизация по фронту
	URshInitADCSlopeDecline = 0x2, //!<Синхронизация по срезу
	URshInitADCFrequencySwitchToMinimum = 0x4, //!<Предыстория и история собираются с разными частотами (переключение на низкую частоту)
	URshInitADCFrequencySwitchToMaximum = 0x8 //!<Предыстория и история собираются с разными частотами (переключение на высокую частоту)
};

//! Константы для поля control структуры URshInitGSPF
enum URshInitGSPFControl
{
	URshInitGSPFControlFilterOff = 0x0,				//!< Выключить фильтр НЧ
	URshInitGSPFControlPlayOnce = 0x0,				//!< Одиночное проигрование
	URshInitGSPFControlSynchroFront = 0x0,			//!< Запуск по фронту
	URshInitGSPFControlSynthesizerOff = 0x0,		//!< Синтезатор частоты не исползуется

	URshInitGSPFControlSynthesizerOn = 0x1,			//!< Использовать синтезатор частоты
	URshInitGSPFControlFilterOn = 0x2,				//!< Включить фильтр НЧ
	URshInitGSPFControlPlayLoop = 0x4,				//!< Циклическое проигрование
	URshInitGSPFControlSynchroDecline = 0x8			//!< Запуск по спаду
};

//! Константы для поля attenuator структуры URshInitGSPF
enum URshInitGSPFAttenuation
{
	URshInitGSPFAttenuationOff = 0x0,		//!< Ослабление не используется
	URshInitGSPFAttenuation6dB = 0x1,		//!< Ослабление 6дБ
	URshInitGSPFAttenuation12db = 0x2,		//!< Ослабление 12дБ
	URshInitGSPFAttenuation18dB = 0x3,		//!< Ослабление 18дБ
	URshInitGSPFAttenuation24dB = 0x4,		//!< Ослабление 24дБ
	URshInitGSPFAttenuation30dB = 0x5,		//!< Ослабление 30дБ
	URshInitGSPFAttenuation36dB = 0x6,		//!< Ослабление 36дБ
	URshInitGSPFAttenuation42dB = 0x7		//!< Ослабление 42дБ	
};

#pragma pack(pop) 

#endif //__RSH_UNIDRIVER_STRUCTURES_H__
