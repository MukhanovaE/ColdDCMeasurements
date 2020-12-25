/*!
 * \copyright JSC "Rudnev-Shilyaev"
 *
 * \file RshUniDriverFunctions.h
 * \date 02.07.2014
 * \version 1.0 [SDK 2.00]
 *
 * \~english
 * \brief
 * Here you can find prototypes of the functions exported from RshUniDriver.dll.
 *
 * \~russian
 * \brief
 * В данном файле описаны прототипы функций экспортируемых из RshUniDriver.dll.
 *
 */

#ifndef __RSH_UNIDRIVER_FUNCTIONS_H__
#define __RSH_UNIDRIVER_FUNCTIONS_H__
#include "RshUniDriverStructures.h"

#ifdef __cplusplus
extern "C"
{
#endif

 /*!
  * \brief
  * Получение строки с названием зарегистрированной библиотеки устройства
  *
  * \param[in] index
  * Индекс записи в реестре.
  *
  * \param[in,out] value
  * Структура, в которую будет помещена строка с описанием ошибки.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция позволяет получить строку с названием зарегистрированной библиотеки устройства.\n
  * В зависимости от выбранного типа структуры (URshTypeU16PointerStructure или
  * URshTypeS8PointerStructure) можно получить строку в UTF-16 либо в ANSI формате
  * соответственно.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverGetRegisteredDeviceName(unsigned int index, URshType* value);

 /*!
  * \brief
  * Получение строки с описанием ошибки
  *
  * \param[in] error
  * Код ошибки, полученный в результате вызова одной из функций RshUniDriver
  *
  * \param[in,out] value
  * Структура, в которую будет помещена строка с описанием ошибки.
  *
  * \param[in] language
  * Язык описания (одна из констант - ::RSH_LANGUAGE_ENGLISH или ::RSH_LANGUAGE_RUSSIAN)
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция позволяет получить строку с описанием ошибки по ее коду.\n
  * В зависимости от выбранного типа структуры (URshTypeU16PointerStructure или
  * URshTypeS8PointerStructure) можно получить строку в UTF-16 либо в ANSI формате
  * соответственно.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverGetError(unsigned int error, URshType* value, int language);

 /*!
  * \brief
  * Создание буфера для данных
  *
  * \param[in,out] uRshBuffer
  * Указатель на структуру URshBuffer
  *
  * \param[in] desiredBufferSize
  * Желаемый размер буфера
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция используется для создания буферов данных, которые
  * затем используются в функции UniDriverGetData для передачи данных.\n
  * Перед вызовом функции необходимо установить код данных (одна из констант
  * списка URshTypes) в поле type структуры URshBuffer. После успешного вызова
  * функции в переданной структуре будут содержаться данные о размере буфера, а
  * также указатель на данные. Память выделяется внутри RshUniDriver.dll
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverAllocateBuffer(void* uRshBuffer, unsigned int desiredBufferSize);

 /*!
  * \brief
  * Удаление буфера данных
  *
  * \param[in,out] uRshBuffer
  * Указатель на структуру URshBuffer
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * С помощью данной функции можно освободить память, выделенную при
  * вызове функции UniDriverAllocateBuffer().\n
  * При выгрузке библиотеки RshUniDriver.dll вся выделенная память
  * освобождается автоматически.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverFreeBuffer(void* uRshBuffer);

 /*!
  * \brief
  * Получение идентификатора драйвера
  *
  * \param[in] deviceName
  * Строка с названием устройства (имя ветки в реестре).
  *
  * \param[in, out] deviceHandle
  * Указатель на переменную, в которую будет помещен идентификатор драйвера.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная фукнция используется для получения идентификатора драйвера, который
  * в дальнейшем используется для управления устройством. Все остальные функции
  * библиотеки RshUniDriver (такие как UniDriverConnect(), UniDriverStart(), UniDriverGetData()
  * и т.д.) требуют идентификатор драйвера в качестве параметра.\n
  * При вызове данной функции внутри библиотеки RshUniDriver.dll происходит загрузка
  * объекта с интерфейсом устройства IRshDevice из соответствующей библиотеки абстракции
  * (например, LA20USB.dll). Полученный объект хранится в памяти до выгрузки библиотеки
  * RshUniDriver или до вызова функции UniDriverCloseDeviceHandle(), а его идентификатор
  * возвращается в переменной deviceHandle.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverGetDeviceHandle(char* deviceName,unsigned int* deviceHandle);

 /*!
  * \brief
  * Освобождение драйвера устройства
  *
  * \param[in, out] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция используется для освобождения ресурсов, связанных с загруженной
  * библиотекой абстракции устройства. Как правило, данную функцию нужно вызывать
  * при выходе из программы, либо когда загруженный драйвер устройства больше не нужен.\n
  * Обратите внимание, что после успешного вызова данной функции значение идентификатора
  * deviceHandle уже не действительно, т.к. объект, на который он ссылается, будет удален.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverCloseDeviceHandle(unsigned int deviceHandle);

 /*!
  * \brief
  * Проверка возможностей устройства и библиотеки
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] capsCode
  * Одна из констант перечисления ::RSH_CAPS
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * С помощью данной функции можно проверить поддержку устройством различных аппаратных
  * и программных возможностей, режимов работы и прочего. Подробности - в описании
  * ::RSH_CAPS.\n
  * Если функция возвращает код ::RSH_API_SUCCESS - значит запрашиваемая возможность
  * поддерживается устройством.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverIsCapable(unsigned int deviceHandle, unsigned int capsCode);

 /*!
  * \brief
  * Подключение к устройству
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] deviceIndex
  * Идентификатор устройства (базовый адрес либо заводской номер).
  *
  * \param[in] mode
  * Режим подключения\n
  * Допустимые варианты: RSH_CONNECT_MODE_BASE или RSH_CONNECT_MODE_SERIAL_NUMBER.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * С помощью данной функции можно подключиться к выбранному устройству.\n
  * В зависимости от параметра mode, идентификатор устройства может быть либо
  * базовым адресом (индексация устройств в системе начинается с 1), либо заводским
  * номером устройства (данный вариант возможен не для всех устройств).\n
  * После успешного вызова данной функции будет осуществлено физическое подключение
  * к заданному устройству. По сути, до вызова данной функции все операции выполняются
  * только с программными объектами (библиотекам).
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverConnect(unsigned int deviceHandle, unsigned int deviceIndex, unsigned int mode);

 /*!
  * \brief
  * Подключение к устройству
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] key
  * Строка-идентификатор устройства.
  *
  * \param[in] mode
  * Режим подключения\n
  * Допустимые варианты: RSH_CONNECT_MODE_CONNECTION_STRING
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * С помощью данной функции можно подключиться к выбранному устройству.\n
  * Данная функция - аналог UniDriverConnect, используется в некоторых случаях -
  * например, для подключения к Ethernet устройствам по ip адресу и т.п.\n
  * Для большинства устройств данный режим не реализован
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverConnectViaStringKey(unsigned int deviceHandle, char* key, unsigned int mode);

 /*!
  * \brief
  * Инициализация параметров устройства
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] initializationMode
  * Режим инициализации (варианты: RSH_INIT_MODE_CHECK или RSH_INIT_MODE_INIT)
  *
  * \param[in,out] initializationStructure
  * Режим подключения\n
  * Указатель на заполненную структуру инициализации.
  * Можно передать следующие структуры:\n
  * URshInitDMA, URshInitMemory, URshInitPort,
  * URshInitDAC, URshInitGSPF, URshInitVoltmeter.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * С помощью данной функции можно задать необходимые параметры сбора данных
  * (или генерации сигнала), а также осуществлять управление цифровым портом
  * или ЦАПом устройства.\n
  * После успешного вызова функции параметры в структуре будут отредактированы,
  * если они выходят за допустимые пределы.
  */
__declspec(dllimport) unsigned __stdcall UniDriverInit(unsigned int deviceHandle, unsigned int initializationMode, void* initializationStructure);

 /*!
  * \brief
  * Запуск сбора данных (генерации сигнала)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Вызов данной функции запускает сбор данных, либо генерацию сигнала
  * в случае генераторов.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverStart(unsigned int deviceHandle);

 /*!
  * \brief
  * Остановка сбора данных (генерации сигнала)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Вызов данной функции останавливает сбор данных, либо генерацию сигнала
  * в случае генераторов.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverStop(unsigned int deviceHandle);

 /*!
  * \brief
  * Получение (передача) буфера с данными
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] getDataMode
  * Дополнительные параметры (одна из констант перечисления ::RSH_DATA_MODES).
  * Используйте ::RSH_DATA_MODE_NO_FLAGS если не требуется выполнять каких-либо
  * дополнительных действий с данными в буфере.
  *
  * \param[in] uRshBuffer
  * Указатель на структуру URshBuffer. Перед получением данных
  * структура должна быть проинициализирована вызовом функции
  * UniDriverAllocateBuffer().
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Получение буфера данных, либо передача буфера (в случаее генераторов).
  * После успешного вызова данной функции в буфере будут находиться собранные
  * данные.\n
  * Если используется буфер чисел с плавающей точкой (double), отсчеты АЦП
  * будут преобразованы в вольты.\n
  * Как правило, библиотеки абстракции поддерживают передачу данных
  * в буфере типа double, а также один из вариантов - char, short или int,
  * в зависимости от разрядности АЦП.
  *
  * \remarks
  * Существуют аналоги данной функции (UniDriverLVGetDataShort(), UniDriverLVGetDataDouble() и т.д.),
  * в которыx не используется структура URshBuffer - вместо нее передается указатель на обычный массив
  * нужного типа. В отличие от данной функции, память под массив должна быть выделена заранее,
  * в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverGetData(unsigned int deviceHandle, unsigned int getDataMode, void* uRshBuffer);

 /*!
  * \brief
  * Получение информации об устройстве и библиотеке
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на структуру с данными. В зависимости от того, какую информацию
  * нужно получить (выбранный Get код), отличается тип данных в структуре.\n
  * Возможные варианты структур и их соответcвие с типами RSH API:\n
  * <ul>
  * <li>URshType</li>
  * <li>URshTypeDoubleStructure - тип <b>double</b> (тип RSH_DOUBLE в описании ::RSH_GET)</li>
  * <li>URshTypeS8Structure - тип <b>char</b> (тип RSH_S8 в описании ::RSH_GET)</li>
  * <li>URshTypeU8Structure - тип <b>unsigned char</b> (тип RSH_U8 в описании ::RSH_GET)</li>
  * <li>URshTypeS16Structure - тип <b>short</b> (тип RSH_S16 в описании ::RSH_GET)</li>
  * <li>URshTypeU16Structure - тип <b>unsigned short</b> (тип RSH_U16 в описании ::RSH_GET)</li>
  * <li>URshTypeS32Structure - тип <b>int</b> (тип RSH_S32 в описании ::RSH_GET)</li>
  * <li>URshTypeU32Structure - тип <b>unsigned int</b> (тип RSH_U32 в описании ::RSH_GET)</li>
  * <li>URshTypeU16PointerStructure - тип <b>unsigned short*</b>(тип RSH_U16P в описании ::RSH_GET)</li>
  * <li>URshTypeS8PointerStructure - тип <b>char*</b>(тип RSH_S8P в описании ::RSH_GET)</li>
  * </ul>
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция используется для получения различной информации об устройстве. Заданный
  * в качестве параметра getMode код определяет, какие именно данные и в каком виде будут получены.\n
  * Например, если нужно получить количество аналоговых каналов устройства, код будет выглядеть примерно так
  * \code
  * ...
  * //результат выполнения операции
  * unsigned res;
  * //структура для передачи данных (целое 32 бит без знака)
  * URshTypeU32Structure str;
  * //ставим нужный тип (это приходится делать вручную, т.к. нет конструктора)
  * str.type = rshU32;
  * //инициализируем поле данных
  * str.data = 0;
  *
  * //Вызов функции UniDriverGet() (предполагается, что получение идентификатора и подключение уже выполнены ранее)
  * res = UniDriverGet(deviceHandle,RSH_GET_DEVICE_NUMBER_CHANNELS,&str);
  * if (res == RSH_API_SUCCESS)
  * {
  *		//в поле data - количество каналов
  *		printf("Number of channels: %d\n", str.data);
  * }
  * else
  * {
  *		//обработка ошибки
  * }
  *
  * \endcode
  *
  * \remarks
  * Иногда данная функция может использоваться не только для получения данных, но и для
  * задания параметров. Подробности - в описании ::RSH_GET.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverGet(unsigned int deviceHandle, unsigned int mode, void* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (char).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_S8</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetChar(unsigned int deviceHandle, unsigned int mode, char* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned char).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_U8</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetUChar(unsigned int deviceHandle, unsigned int mode,unsigned char* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (short).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_S16</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetShort(unsigned int deviceHandle, unsigned int mode, short* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned short).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_U16</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetUShort(unsigned int deviceHandle, unsigned int mode,unsigned short* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (int).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_S32</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetInt(unsigned int deviceHandle, unsigned int mode, int* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned int).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_U32</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetUInt(unsigned int deviceHandle, unsigned int mode, unsigned int* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (double).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на переменную, в которую будут помещены данные.
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_DOUBLE</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetDouble(unsigned int deviceHandle, unsigned int mode, double* value);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (char* - строка).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in,out] value
  * Указатель на массив, в который будут помещены данные.
  *
  * \param[in] maxLength
  * Максимальный размер строки (должен быть равен размеру выделенной памяти в буфере \b value).
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на переменную
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_S8P</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetCstr(unsigned int handle, unsigned int mode, char* value, unsigned int maxLength);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (int* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_S32</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayInt(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, int* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned int* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_U32</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayUInt(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, unsigned int* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (short* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_S16</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayShort(unsigned int deviceHandle, unsigned int mode,unsigned int size, unsigned int* received, short* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned short* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_U16</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayUShort(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, unsigned short* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (char* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_S8</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayChar(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, char* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (unsigned char* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_U8</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayUChar(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, unsigned char* data);

 /*!
  * \brief
  * Получение информации об устройстве или библиотеке (double* - массив).
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] mode
  * Одна из констант перечисления ::RSH_GET
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре data.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] data
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGet(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  * Тип данных, указанный в описании Get-кода, который подходит для данной функции: <b>RSH_BUFFER_DOUBLE</b> \n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetArrayDouble(unsigned int deviceHandle, unsigned int mode, unsigned int size, unsigned int* received, double* data);

 /*!
  * \brief
  * Получение (передача) буфера с данными (массив char*)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] getDataMode
  * Дополнительные параметры (одна из констант перечисления ::RSH_DATA_MODES).
  * Используйте ::RSH_DATA_MODE_NO_FLAGS если не требуется выполнять каких-либо
  * дополнительных действий с данными в буфере.
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре buffer.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] buffer
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGetData(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetDataChar(unsigned int deviceHandle, unsigned int getDataMode,unsigned int size, unsigned int* received, char* buffer);

/*!
  * \brief
  * Получение (передача) буфера с данными (массив short*)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] getDataMode
  * Дополнительные параметры (одна из констант перечисления ::RSH_DATA_MODES).
  * Используйте ::RSH_DATA_MODE_NO_FLAGS если не требуется выполнять каких-либо
  * дополнительных действий с данными в буфере.
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре buffer.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] buffer
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGetData(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetDataShort(unsigned int deviceHandle, unsigned int getDataMode,unsigned int size, unsigned int* received, short* buffer);

/*!
  * \brief
  * Получение (передача) буфера с данными (массив int*)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] getDataMode
  * Дополнительные параметры (одна из констант перечисления ::RSH_DATA_MODES).
  * Используйте ::RSH_DATA_MODE_NO_FLAGS если не требуется выполнять каких-либо
  * дополнительных действий с данными в буфере.
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре buffer.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] buffer
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGetData(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetDataInt(unsigned int deviceHandle, unsigned int getDataMode,unsigned int size, unsigned int* received, int* buffer);

/*!
  * \brief
  * Получение (передача) буфера с данными (массив double*)
  *
  * \param[in] deviceHandle
  * Идентификатор драйвера устройства, полученный в результате вызова функции UniDriverGetDeviceHandle()
  *
  * \param[in] getDataMode
  * Дополнительные параметры (одна из констант перечисления ::RSH_DATA_MODES).
  * Используйте ::RSH_DATA_MODE_NO_FLAGS если не требуется выполнять каких-либо
  * дополнительных действий с данными в буфере.
  *
  * \param[in] size
  * Размер массива - максимальное количество элементов, которые можно скопировать
  * в массив, указатель на который передается в параметре buffer.
  *
  * \param[in,out] received
  * После успешного выполнения функции в даннной переменной будет возвращено
  * количество фактически скопированных элементов.
  *
  * \param[in,out] buffer
  * Указатель на массив, в который будут скопированы данные
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция - аналог функции UniDriverGetData(). Отличие в том, что для передачи данных
  * не используется специальная структура данных - можно просто передать указатель на массив
  * нужного типа.\n
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetDataDouble(unsigned int deviceHandle, unsigned int getDataMode,unsigned int size, unsigned int* received, double* buffer);

 /*!
  * \brief
  * Получение строки с описанием ошибки
  *
  * \param[in] error
  * Код ошибки, полученный в результате вызова одной из функций RshUniDriver
  *
  * \param[in,out] description
  * Указатель на массив (строку) типа char*, в который будут скопированы данные
  * (строка с описанием ошибки).
  *
  * \param[in] maxLength
  * Максимальный размер строки (должен быть равен размеру выделенной памяти в буфере \b description).
  *
  * \param[in] language
  * Язык описания (одна из констант - ::RSH_LANGUAGE_ENGLISH или ::RSH_LANGUAGE_RUSSIAN)
  *
  * \returns
  * ::RSH_API_SUCCESS или код ошибки.
  *
  * Данная функция позволяет получить строку с описанием ошибки по ее коду.\n
  * Эта функция - аналог функции UniDriverGetError(), но для передачи строки
  * не используется специальная структура.\n
  * Пример использования:
  * \code
  * char errorDesc[1024];
  * UniDriverLVGetError(code, errorDesc,1024,RSH_LANGUAGE_ENGLISH);
  * printf("Function failed with error:\n[0x%08X] - %s", code,  errorDesc);
  * \endcode
  *
  * \warning
  * Память под данные должна быть выделена заранее, в программе пользователя. Внутри библиотеки UniDriver
  * происходит только копирование в переданный буфер.
  *
  */
__declspec(dllimport) unsigned __stdcall UniDriverLVGetError(unsigned int error, char* description, unsigned int maxLength, int language);

#ifdef __cplusplus
}
#endif

#endif //__RSH_UNIDRIVER_FUNCTIONS_H__
