/*!
 * \copyright JSC "Rudnev-Shilyaev"
 * 
 * \file RshDefChk.h
 * \date 03.09.2013
 * \version 1.0 [SDK 2.00]
 * 
 * \~english
 * \brief
 * OS macro definitions.
 * 
 * \~russian
 * \brief
 * ОС-макросы.
 * 
 */

#ifndef __RSH_DEF_CHK_H__
#define __RSH_DEF_CHK_H__

#if defined(_WIN32) || defined(_WIN64)
#define RSH_MSWINDOWS
#else
#define RSH_LINUX
#endif

#endif //__RSH_DEF_CHK_H__
