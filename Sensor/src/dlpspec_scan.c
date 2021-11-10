/*****************************************************************************
**
**  Copyright (c) 2015 Texas Instruments Incorporated.
**
******************************************************************************
**
**  DLP Spectrum Library
**
*****************************************************************************/

#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>
#include "dlpspec_scan.h"
#include "dlpspec_scan_col.h"
#include "dlpspec_scan_had.h"
#include "dlpspec_types.h"
#include "dlpspec_helper.h"
#include "dlpspec_util.h"
#include "dlpspec_calib.h"

/**
 * @addtogroup group_scan
 *
 * @{
 */

static patDefHad patDefH;

static int32_t dlpspec_scan_slew_genPatterns(const slewScanConfig *pCfg,
		const calibCoeffs *pCoeffs, const FrameBufferDescriptor *pFB)
{
    int32_t numPatterns=0;
    patDefCol patDefC;
	int i;
	scanConfig cfg;
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	uint32_t start_pattern = 0;

	cfg.scanConfigIndex = pCfg->head.scanConfigIndex;
	strcpy(cfg.ScanConfig_serial_number, pCfg->head.ScanConfig_serial_number);
	strcpy(cfg.config_name, pCfg->head.config_name);
	cfg.num_repeats = pCfg->head.num_repeats;
	
	for(i=0; i < pCfg->head.num_sections; i++)
	{
		cfg.scan_type = pCfg->section[i].section_scan_type;
		cfg.wavelength_start_nm = pCfg->section[i].wavelength_start_nm;
		cfg.wavelength_end_nm = pCfg->section[i].wavelength_end_nm;
		cfg.width_px =  pCfg->section[i].width_px;
		cfg.num_patterns = pCfg->section[i].num_patterns;
		switch (cfg.scan_type)
		{
			case COLUMN_TYPE:
				ret_val = dlpspec_scan_col_genPatDef(&cfg, pCoeffs, &patDefC);
				if (ret_val == DLPSPEC_PASS)
					numPatterns = dlpspec_scan_col_genPatterns(&patDefC, pFB, 
							start_pattern);
				break;
			case HADAMARD_TYPE:
				ret_val = dlpspec_scan_had_genPatDef(&cfg, pCoeffs, &patDefH);
				if (ret_val == DLPSPEC_PASS)
					numPatterns = dlpspec_scan_had_genPatterns(&patDefH, pFB, 
							start_pattern);
				break;
			default:
				return ERR_DLPSPEC_INVALID_INPUT;
		}
		start_pattern += numPatterns;
	}

    if (ret_val < 0)
    {
        return ret_val;
    }
    else
    {
        return start_pattern;
    }
}

int32_t dlpspec_scan_genPatterns(const uScanConfig* pCfg, 
		const calibCoeffs *pCoeffs, const FrameBufferDescriptor *pFB)
/**
 * @brief Function to generate patterns for a scan.
 *
 * This is a wrapper function for the pattern generation functions of the 
 * supported scan modules (Column and Hadamard). In this way, any supported 
 * scan configuration can have patterns generated by calling this function
 *
 * @param[in]   pCfg        Pointer to scan config
 * @param[in]   pCoeffs     Pointer to calibration coefficients of the target 
 *							optical engine
 * @param[in]	pFB         Pointer to frame buffer descriptor where the 
 *							patterns will be stored
 *
 * @return  >0  Number of binary patterns generated from scan config
 * @return  ≤0  Error code as #DLPSPEC_ERR_CODE
 */
{
    int32_t numPatterns=0;
    patDefCol patDefC;
    
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);

    switch (pCfg->scanCfg.scan_type)
    {
        case COLUMN_TYPE:
            ret_val = dlpspec_scan_col_genPatDef(&pCfg->scanCfg, pCoeffs, 
					&patDefC);
            if (ret_val == DLPSPEC_PASS)
                numPatterns = dlpspec_scan_col_genPatterns(&patDefC, pFB, 0);
            break;
        case HADAMARD_TYPE:
            ret_val = dlpspec_scan_had_genPatDef(&pCfg->scanCfg, pCoeffs, 
					&patDefH);
            if (ret_val == DLPSPEC_PASS)
                numPatterns = dlpspec_scan_had_genPatterns(&patDefH, pFB, 0);
            break;
        case SLEW_TYPE:
                numPatterns = dlpspec_scan_slew_genPatterns(&pCfg->slewScanCfg, 
						pCoeffs, pFB);
            break;
		default:
			return ERR_DLPSPEC_INVALID_INPUT;
    }

    if (ret_val < 0)
    {
        return ret_val;
    }
    else
    {
        return numPatterns;
    }
}

DLPSPEC_ERR_CODE dlpspec_scan_bendPatterns(const FrameBufferDescriptor *pFB , 
		const calibCoeffs* calCoeff, const int32_t numPatterns)
/**
 * Function to bend existing patterns to correct for optical distortion
 *
 * @param[in,out]   pFB             Pointer to frame buffer descriptor where the patterns will be stored
 * @param[in]       calCoeff        Pointer to calibration coefficients of the target optical engine
 * @param[out]      numPatterns     Number of binary patterns stored in frame buffer
 *
 * @return          Error code
 *
 */
{
    uint32_t line;
    int buffer;
    uint8_t *pLine;
    uint8_t *pOrigLine;
    int8_t* shiftVector = NULL;
    int numBuffers;
    uint8_t *pBuffer;
    int lineWidthInBytes;
    int frameBufferSz;
    int offset;
    
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);

    if ((pFB == NULL) || (calCoeff == NULL))
        return (ERR_DLPSPEC_NULL_POINTER);

    if ((numPatterns < 0))
        return (ERR_DLPSPEC_INVALID_INPUT);

    numBuffers = (numPatterns + (pFB->bpp-1))/pFB->bpp;
    pBuffer = (uint8_t *)pFB->frameBuffer;
    lineWidthInBytes = pFB->width * (pFB->bpp/8);
    frameBufferSz = (lineWidthInBytes * pFB->height);
    offset = lineWidthInBytes/2;

    shiftVector = (int8_t*)(malloc(sizeof(uint8_t)*pFB->height));
    //Copy line to a larger buffer with zeroes filled on both ends
    pOrigLine = (uint8_t*)(malloc(lineWidthInBytes * 2));

    if( (NULL == shiftVector) || (pOrigLine == NULL))
    {
		ret_val = ERR_DLPSPEC_INSUFFICIENT_MEM;
		goto cleanup_and_exit;
    }

    /* Calculate the shift vector */
    ret_val = dlpspec_calib_genShiftVector(calCoeff->ShiftVectorCoeffs, 
			pFB->height, shiftVector);
    if (ret_val < 0)
    {
        goto cleanup_and_exit;
    }

    for(buffer = 0; buffer < numBuffers; buffer++)
    {
    	memset(pOrigLine, 0, lineWidthInBytes*2);
        memcpy(pOrigLine+offset, pBuffer, lineWidthInBytes);

        for(line=0 ; line< pFB->height; line++ )
        {
            pLine = pBuffer + (line * lineWidthInBytes);
            memcpy(pLine, pOrigLine+offset-(shiftVector[line] * (pFB->bpp/8)), lineWidthInBytes);
        }/*end of line loop*/
        pBuffer += frameBufferSz;
    } /*end of buffer loop*/


cleanup_and_exit:
    if(shiftVector != NULL)
        free(shiftVector);
    if(pOrigLine != NULL)
        free(pOrigLine);

    return ret_val;
}

DLPSPEC_ERR_CODE dlpspec_get_scan_config_dump_size(const uScanConfig *pCfg, 
		size_t *pBufSize)
/**
 * Function that retuns buffer size required to store given scan config structure
 * after serialization. This should be called to determine the size of array to 
 * be passed to dlpspec_scan_write_configuration().
 *
 * @param[in]       pCfg        Pointer to scan config
 * @param[out]      pBufSize     buffer size required in bytes retuned in this
 *
 * @return          Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	size_t size;

    if (pCfg == NULL)
		return (ERR_DLPSPEC_NULL_POINTER);

	if(pCfg->scanCfg.scan_type != SLEW_TYPE)
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, pBufSize, CFG_TYPE);
	}
	else
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, &size, SLEW_CFG_HEAD_TYPE);

		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		*pBufSize = size;
        ret_val = dlpspec_get_serialize_dump_size(&pCfg->slewScanCfg.section[0],
			   			&size, SLEW_CFG_SECT_TYPE);

		*pBufSize += size;
	}

    return ret_val;

}

DLPSPEC_ERR_CODE dlpspec_scan_write_configuration(const uScanConfig *pCfg, 
		void *pBuf, const size_t bufSize)
/**
 * Function to write scan configuration to serialized format
 *
 * @param[in]       pCfg        Pointer to scan config
 * @param[in,out]   pBuf        Pointer to buffer in which to store the serialized config
 * @param[in]       bufSize     buffer size, in bytes
 *
 * @return          Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	void *pHeadBuf;
	void *pSectBuf;
	size_t size;
	size_t size1;

    if ((pCfg == NULL) || (pBuf == NULL))
		return (ERR_DLPSPEC_NULL_POINTER);

	if(pCfg->scanCfg.scan_type != SLEW_TYPE)
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, &size, CFG_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		if(bufSize < size) //if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}
		ret_val = dlpspec_serialize(pCfg, pBuf, bufSize, CFG_TYPE);
	}
	else
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, &size, SLEW_CFG_HEAD_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
        ret_val = dlpspec_get_serialize_dump_size(&pCfg->slewScanCfg.section[0],
			   			&size1, SLEW_CFG_SECT_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		if(bufSize < size+size1) //if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}

		pHeadBuf = pBuf;
		ret_val = dlpspec_serialize(pCfg, pHeadBuf, size, SLEW_CFG_HEAD_TYPE);

		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		pSectBuf = (void *)((uintptr_t)pHeadBuf + size);
		ret_val = dlpspec_serialize(&pCfg->slewScanCfg.section[0], pSectBuf, 
				size1, SLEW_CFG_SECT_TYPE);
	}

    return ret_val;

}

DLPSPEC_ERR_CODE dlpspec_scan_read_configuration(void *pBuf, const size_t bufSize)
/**
 * Function to read scan configuration from a serialized format by deserializing in place
 *
 * @param[in,out]   pBuf        Pointer to the serialized scan config buffer
 * @param[in]       bufSize     buffer size, in bytes
 *
 * @return          Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	void *pHeadBuf;
	void *pSectBuf;
	uScanConfig *pCfg = (uScanConfig *)pBuf;
	size_t size;
	size_t size1;
    
    if (pBuf == NULL)
        return (ERR_DLPSPEC_NULL_POINTER);

	if(dlpspec_is_slewcfgtype(pBuf, bufSize) == false)
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, &size, CFG_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		if(bufSize < size) //if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}
		ret_val = dlpspec_deserialize(pBuf, bufSize, CFG_TYPE);
	}
	else
	{
		ret_val = dlpspec_get_serialize_dump_size(pCfg, &size, SLEW_CFG_HEAD_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
        ret_val = dlpspec_get_serialize_dump_size(&pCfg->slewScanCfg.section[0],
			   			&size1, SLEW_CFG_SECT_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		if(bufSize < size+size1) //if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}

		pHeadBuf = pBuf;
		ret_val = dlpspec_deserialize(pHeadBuf, size, SLEW_CFG_HEAD_TYPE);

		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		pSectBuf = (void *)((uintptr_t)pHeadBuf + size);
		ret_val = dlpspec_deserialize(pSectBuf, size1, SLEW_CFG_SECT_TYPE);

		memcpy(&pCfg->slewScanCfg.section[0], pSectBuf, 
				sizeof(slewScanSection)*SLEW_SCAN_MAX_SECTIONS);
	}

    return ret_val;
}

static DLPSPEC_ERR_CODE dlpspec_get_scan_data_dump_sizes(
		const slewScanData *pData, size_t *pSizeDataHead, size_t *pSizeCfgHead,
	   	size_t *pSizeSect, size_t *pSizeADCData)
{
	DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);

	if (pData == NULL)
		return (ERR_DLPSPEC_NULL_POINTER);

	ret_val = dlpspec_get_serialize_dump_size(pData, pSizeDataHead,
			SLEW_DATA_HEAD_TYPE);
	if(ret_val != DLPSPEC_PASS)
		return ret_val;
	ret_val = dlpspec_get_serialize_dump_size(&pData->slewCfg, 
			pSizeCfgHead, SLEW_CFG_HEAD_TYPE);
	if(ret_val != DLPSPEC_PASS)
		return ret_val;
	ret_val = dlpspec_get_serialize_dump_size(&pData->slewCfg.section[0],
			pSizeSect, SLEW_CFG_SECT_TYPE);
	if(ret_val != DLPSPEC_PASS)
		return ret_val;
	ret_val = dlpspec_get_serialize_dump_size(&pData->adc_data[0],
			pSizeADCData, SLEW_DATA_ADC_TYPE);

	return ret_val;

}

DLPSPEC_ERR_CODE dlpspec_get_scan_data_dump_size(const uScanData *pData, 
		size_t *pBufSize)
/**
 * Function that retuns buffer size required to store given scan data structure
 * after serialization. This should be called to determine the size of array to 
 * be passed to dlpspec_scan_write_data().
 *
 * @param[in]       pData        Pointer to scan data
 * @param[out]      pBufSize     buffer size required in bytes retuned in this
 *
 * @return          Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	size_t size_data_head;
	size_t size_cfg_head;
	size_t size_sect;
	size_t size_adc_data;

    if (pData == NULL)
		return (ERR_DLPSPEC_NULL_POINTER);

	if(pData->data.scan_type != SLEW_TYPE)
	{
		ret_val = dlpspec_get_serialize_dump_size(pData, pBufSize, SCAN_DATA_TYPE);
	}
	else
	{
		ret_val =  dlpspec_get_scan_data_dump_sizes(&pData->slew_data, 
				&size_data_head, &size_cfg_head, &size_sect, &size_adc_data);

		*pBufSize = size_data_head+size_cfg_head+size_sect+size_adc_data;
	}

    return ret_val;

}

DLPSPEC_ERR_CODE dlpspec_scan_write_data(const uScanData *pData, void *pBuf, 
		const size_t bufSize)
/**
 * Function to write scan data to serialized format
 *
 * @param[in]       pData       Pointer to scan data
 * @param[in,out]   pBuf        Pointer to buffer in which to store the 
 *								serialized scan data
 * @param[in]       bufSize     buffer size, in bytes
 *
 * @return          Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	size_t size;
	size_t size_data_head;
	size_t size_cfg_head;
	size_t size_sect;
	size_t size_adc_data;
	void *pHeadBuf;
	void *pSectBuf;
	void *pADCdataBuf;
    int type;
    
    if ((pData == NULL) || (pBuf == NULL))
        return (ERR_DLPSPEC_NULL_POINTER);

    type = dlpspec_scan_data_get_type(pData);

    if(type != SLEW_TYPE)
	{
		ret_val = dlpspec_get_serialize_dump_size(pData, &size, SCAN_DATA_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		if(bufSize < size) //if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}
		ret_val = dlpspec_serialize(pData, pBuf, bufSize, SCAN_DATA_TYPE);
	}
    else
	{
		ret_val =  dlpspec_get_scan_data_dump_sizes(&pData->slew_data, 
				&size_data_head, &size_cfg_head, &size_sect, &size_adc_data);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		if(bufSize < size_data_head+size_cfg_head+size_sect+size_adc_data)
		//if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}

		ret_val = dlpspec_serialize(pData, pBuf, size_data_head, 
				SLEW_DATA_HEAD_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		pHeadBuf = (void *)((uintptr_t)pBuf + size_data_head);
		ret_val = dlpspec_serialize(&pData->slew_data.slewCfg, pHeadBuf, 
				size_cfg_head, SLEW_CFG_HEAD_TYPE);

		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		pSectBuf = (void *)((uintptr_t)pHeadBuf + size_cfg_head);
		ret_val = dlpspec_serialize(&pData->slew_data.slewCfg.section[0], 
				pSectBuf, size_sect, SLEW_CFG_SECT_TYPE);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;
		pADCdataBuf = (void *)((uintptr_t)pSectBuf + size_sect);
		ret_val = dlpspec_serialize(&pData->slew_data.adc_data[0], pADCdataBuf,
				size_adc_data, SLEW_DATA_ADC_TYPE);
	}
	
    return ret_val;
}

DLPSPEC_ERR_CODE dlpspec_scan_read_data(void *pBuf, const size_t bufSize)
/**
 * Function to deserialize a serialized scan data blob. The deserialized data
 * is placed at the same buffer (pBuf).
 *
 * @param[in]   pBuf        Pointer to serialized scan data blob; where output
 *							deserialized data is also returned.
 * @param[in]   bufSize     buffer size, in bytes
 *
 * @return      Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	void *pHeadBuf;
	void *pSectBuf;
	void *pADCdataBuf;
	size_t size_data_head;
	size_t size_cfg_head;
	size_t size_sect;
	size_t size_adc_data;
	uScanData *pData = (uScanData *)pBuf;
    
    if (pBuf == NULL)
        return (ERR_DLPSPEC_NULL_POINTER);

	if(dlpspec_is_slewdatatype(pBuf, bufSize) == false)
	{
		ret_val = dlpspec_deserialize(pBuf, bufSize, SCAN_DATA_TYPE);
	}
	else
	{
		ret_val =  dlpspec_get_scan_data_dump_sizes(&pData->slew_data, 
				&size_data_head, &size_cfg_head, &size_sect, &size_adc_data);
		if(ret_val != DLPSPEC_PASS)
			return ret_val;

		if(bufSize < size_data_head+size_cfg_head+size_sect+size_adc_data)
		//if allocated size less than required size
		{
			return ERR_DLPSPEC_INSUFFICIENT_MEM;
		}

		ret_val = dlpspec_deserialize(pBuf, size_data_head,	SLEW_DATA_HEAD_TYPE);
		
		pHeadBuf = (void *)((uintptr_t)pBuf + size_data_head);
		ret_val = dlpspec_deserialize(pHeadBuf, size_cfg_head, SLEW_CFG_HEAD_TYPE);

		if(ret_val != DLPSPEC_PASS)
			return ret_val;

        memcpy(&pData->slew_data.slewCfg.head, pHeadBuf, sizeof(struct slewScanConfigHead));

		pSectBuf = (void *)((uintptr_t)pHeadBuf + size_cfg_head);
		ret_val = dlpspec_deserialize(pSectBuf, size_sect, SLEW_CFG_SECT_TYPE);

		memcpy(&pData->slew_data.slewCfg.section[0], pSectBuf, 
				sizeof(slewScanSection)*SLEW_SCAN_MAX_SECTIONS);

		pADCdataBuf = (void *)((uintptr_t)pSectBuf + size_sect);
		ret_val = dlpspec_deserialize(pADCdataBuf, size_adc_data, 
				SLEW_DATA_ADC_TYPE);
		memcpy(pData->slew_data.adc_data, pADCdataBuf, sizeof(uint32_t)*ADC_DATA_LEN);
		
	}

    return ret_val;
}

static DLPSPEC_ERR_CODE dlpspec_scan_slew_interpret(uScanData *pData,
		scanResults *pRefResults)
{
    scanResults tempScanResults;
    uScanData thisScanData;
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
    int i;
    int num_data;

    dlpspec_subtract_dc_level(&pData->slew_data);

    for(i=0; i < pData->slew_data.slewCfg.head.num_sections; i++)
    {
        dlpspec_get_scanData_from_slewScanData(&pData->slew_data, &thisScanData.data, i);
        if(pData->slew_data.slewCfg.section[i].section_scan_type == COLUMN_TYPE)
            ret_val = dlpspec_scan_col_interpret(&thisScanData, &tempScanResults);
        else if(pData->slew_data.slewCfg.section[i].section_scan_type == HADAMARD_TYPE)
            ret_val = dlpspec_scan_had_interpret(&thisScanData, &tempScanResults);
        else
            return ERR_DLPSPEC_ILLEGAL_SCAN_TYPE;

        if(ret_val != DLPSPEC_PASS)
            break;

        if(i==0)
        {
            memcpy(pRefResults, &tempScanResults, sizeof(scanResults));
            dlpspec_copy_scanData_hdr_to_scanResults(pData, pRefResults);
            num_data = tempScanResults.cfg.section[0].num_patterns;
        }
        else
        {
            memcpy(&pRefResults->intensity[num_data], &tempScanResults.intensity[0],
                   tempScanResults.cfg.section[0].num_patterns*sizeof(int));
            memcpy(&pRefResults->wavelength[num_data], &tempScanResults.wavelength[0],
                   tempScanResults.cfg.section[0].num_patterns*sizeof(double));
            num_data += tempScanResults.cfg.section[0].num_patterns;
            pRefResults->length += tempScanResults.length;
        }
    }
    return ret_val;
}

DLPSPEC_ERR_CODE dlpspec_scan_interpret(const void *pBuf, const size_t bufSize,
	   	scanResults *pResults)
/**
 * Function to interpret a serialized scan data blob into a results struct
 *
 * @param[in]   pBuf        Pointer to serialized scan data blob
 * @param[in]   bufSize     buffer size, in bytes
 * @param[out]  pResults    Pointer to scanResults struct
 *
 * @return      Error code
 *
 */
{
    uScanData *pData;
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
    SCAN_TYPES type;

    if ((pBuf == NULL) || (pResults == NULL))
        return (ERR_DLPSPEC_NULL_POINTER);

    void *pCopyBuff = (void *)malloc(bufSize);

    if(pCopyBuff == NULL)
        return (ERR_DLPSPEC_INSUFFICIENT_MEM);

    memcpy(pCopyBuff, pBuf, bufSize);

    ret_val = dlpspec_scan_read_data(pCopyBuff, bufSize);
    if(ret_val < 0)
    {
        goto cleanup_and_exit;
    }
    
    pData = (uScanData *)pCopyBuff;
    if(pData->data.header_version != CUR_SCANDATA_VERSION)
    {
        ret_val = ERR_DLPSPEC_FAIL;
        goto cleanup_and_exit;
    }
    memset(pResults,0,sizeof(scanResults));

    type = dlpspec_scan_data_get_type(pData);

    if(type == HADAMARD_TYPE)
    {
        ret_val = dlpspec_scan_had_interpret(pCopyBuff, pResults);
    }
    else if(type == COLUMN_TYPE)
    {
        ret_val = dlpspec_scan_col_interpret(pCopyBuff, pResults);
    }
    else if(type == SLEW_TYPE)
    {
        ret_val = dlpspec_scan_slew_interpret(pCopyBuff, pResults);
    }
	else
	{
		ret_val = ERR_DLPSPEC_INVALID_INPUT;
	}

    cleanup_and_exit:
    if(pCopyBuff != NULL)
	    free(pCopyBuff);

    return ret_val;
}

static DLPSPEC_ERR_CODE dlpspec_scan_scale_for_pga_gain(const scanResults 
		*pScanResults, scanResults *pRefResults)
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
	int j;

    if (pScanResults->pga != pRefResults->pga)
    {
        if (pRefResults->pga > 0)
        {
            for (j=0; j < ADC_DATA_LEN; j++)
            {
                if (pRefResults->wavelength[j] != 0)
                    pRefResults->intensity[j] = pRefResults->intensity[j]
					   	* pScanResults->pga / pRefResults->pga;
                else
                    break;
            }
        }
        else
          ret_val = ERR_DLPSPEC_INVALID_INPUT;
    }
	return ret_val;
}

static DLPSPEC_ERR_CODE dlpspec_scan_recomputeRefIntensities(const scanResults 
		*pScanResults, scanResults *pRefResults, const refCalMatrix *pMatrix)
/**
 * Function to interpret a results struct of intensities into a predicted 
 * spectrum which would have been measured with a target configuration that
 * has a different pixel width and/or PGA setting. Due to the diffraction 
 * efficiency of the DMD varying with wavelength and the width of on pixels, 
 * the efficiency of reflection can vary with these inputs. This is used
 * internally by the dlpspec_scan_interpReference() function.
 *
 * @param[in]		pScanResults    Scan results from sample scan data 
 *									(output of dlpspec_scan_interpret function)
 * @param[in,out]   pRefResults     Pointer to scanResults struct with the
 *									original scan data. This is assumed to have
 *									only one scan section (ref scan cannot be 
 *									a slew scan).
 * @param[in]       pMatrix         Pointer to the reference calibration matrix. This
 *                                  matrix will be opto-mechanical design specific.
 * 
 * @return          Error code
 *
 */
{
    double factor[ADC_DATA_LEN];
    double wavelengths[ADC_DATA_LEN];

    int i = 0, j = 0;
    int temp_val = 0;
    int s_idx;
	uint32_t section_data_len;
	uint32_t adc_data_idx = 0;
    int px_width_lower_bound =0, px_width_upper_bound=0;
    int ref_val = 0;
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);

    if ((pRefResults == NULL) || (pMatrix == NULL) || (pScanResults == NULL))
        return (ERR_DLPSPEC_NULL_POINTER);

    memset(wavelengths,0,sizeof(double)*ADC_DATA_LEN);
    memset(factor,0,sizeof(double)*ADC_DATA_LEN);

	for(s_idx = 0; s_idx < pScanResults->cfg.head.num_sections; s_idx++)
	{
        for (j=0; j < REF_CAL_INTERP_WAVELENGTH; j++)
        {
            factor[j] = 1;
            wavelengths[j] = pMatrix->wavelength[j];
        }

		section_data_len = pScanResults->cfg.section[s_idx].num_patterns;
		/* If width is not the same between reference cal data config and input, 
		 * then we need to compute the values */
		if (((pRefResults->cfg.head.num_sections == 1) 
			&& (pScanResults->cfg.head.num_sections == 1)
			 && (pScanResults->cfg.section[0].width_px == 
			     pRefResults->cfg.section[0].width_px)) == false)
		{
			/* Compute the indices to pixel widths less and greater than pixel 
			 * width used for reference calibration. This is used later on to 
			 * normalize factors with respect to reference calibration intensities
			 */
			for (i=0;i < REF_CAL_INTERP_WIDTH;i++)
			{
				if (pMatrix->width[i] < pRefResults->cfg.section[0].width_px)
					continue;
				else if (pMatrix->width[i] == pRefResults->cfg.section[0].width_px)
				{
					px_width_lower_bound = i;
					px_width_upper_bound = i;
				}
				else
				{
					px_width_lower_bound = i-1;
					px_width_upper_bound = i;
				}
				break;
			}

			for (j=0; j < REF_CAL_INTERP_WAVELENGTH; j++)
			{
				if (i == 0)
				{
					ret_val = dlpspec_compute_from_references(pMatrix->width[i],
							pMatrix->width[i+1],
							pMatrix->ref_lookup[i][j],
							pMatrix->ref_lookup[i+1][j],
							pScanResults->cfg.section[s_idx].width_px,
							&temp_val);
				}
				else if (i == (REF_CAL_INTERP_WIDTH - 1))
				{
					ret_val = dlpspec_compute_from_references(pMatrix->width[i-1],
							pMatrix->width[i],
							pMatrix->ref_lookup[i-1][j],
							pMatrix->ref_lookup[i][j],
							pScanResults->cfg.section[s_idx].width_px,
							&temp_val);
				}
				else
				{
					ret_val = dlpspec_compute_from_references(pMatrix->width[i],
							pMatrix->width[i-1],
							pMatrix->ref_lookup[i][j],
							pMatrix->ref_lookup[i-1][j],
							pScanResults->cfg.section[s_idx].width_px,
							&temp_val);
				}

				if (ret_val < 0)
				{
					return ret_val;
				}

				// Compute the intensity at pixel width used for reference 
				// calibration and use it to normalize the computed factor
				if (px_width_lower_bound == px_width_upper_bound)
					ref_val = pMatrix->ref_lookup[px_width_lower_bound][j];
				else
				{
					ret_val = dlpspec_compute_from_references(
							pMatrix->width[px_width_lower_bound],
							pMatrix->width[px_width_upper_bound],
							pMatrix->ref_lookup[px_width_lower_bound][j],
							pMatrix->ref_lookup[px_width_upper_bound][j],
							pRefResults->cfg.section[0].width_px,
							&ref_val);
				}

				if (ret_val < 0)
				{
					return ret_val;
				}

				factor[j] = factor[j] * temp_val / ref_val;
			}

			/* Next adjust the factors based on wavelengths in reference scan data 
			 * and ones used in reference matrix measurements */
            ret_val = dlpspec_interpolate_double_wavelengths(&pRefResults->wavelength[adc_data_idx],
                    wavelengths,
                    factor,
                    section_data_len);
			if (ret_val < 0)
			{
				return ret_val;
			}

            for (i = 0; i < section_data_len; adc_data_idx++, i++)
			{
				if (pRefResults->wavelength[adc_data_idx] != 0)
				{
					pRefResults->intensity[adc_data_idx] = 
                        pRefResults->intensity[adc_data_idx] * factor[i];
				}
				else
					break;
			}
		}
	}

	ret_val = dlpspec_scan_scale_for_pga_gain(pScanResults, pRefResults);
    return (ret_val);
}


DLPSPEC_ERR_CODE dlpspec_scan_interpReference(const void *pRefCal, 
		size_t calSize, const void *pMatrix, size_t matrixSize, 
		const scanResults *pScanResults, scanResults *pRefResults)
/**
 * Function to interpret reference scan data into what the reference scan would have been 
 * if it were scanned with the configuration which @p pScanResults was scanned with.
 * This can be used to compute a reference for an arbitrary scan taken when a physical
 * reflective reference is not available to take a new reference measurement.
 *
 * @param[in]   pRefCal  	    Pointer to serialized reference calibration data
 * @param[in]   calSize         Size of reference calibration data blob
 * @param[in]   pMatrix         Pointer to serialized reference calibration matrix
 * @param[in]   matrixSize      Size of reference calibration matrix data blob
 * @param[in]   pScanResults    Scan results from sample scan data (output of dlpspec_scan_interpret function)
 * @param[out]  pRefResults     Reference scan data result
 *
 * @return      Error code
 *
 */
{
    DLPSPEC_ERR_CODE ret_val = (DLPSPEC_PASS);
    scanData *pDesRefScanData = NULL;  //To hold deserialized reference scan data
    refCalMatrix *pDesRefCalMatrix = NULL; //To hold deserialized reference cal matrix data
    int i = 0;

    if ((pRefCal == NULL) || (pMatrix == NULL) || (pScanResults == NULL) || 
			(pRefResults == NULL))
        return (ERR_DLPSPEC_NULL_POINTER);
    
    /* New error checking since SCAN_DATA_BLOB_SIZE and REF_CAL_MATRIX_BLOB_SIZE 
    will vary based on compilation target with sizeof() call */
    if ((calSize == 0) || (matrixSize == 0))
        return (ERR_DLPSPEC_INVALID_INPUT);
    
    /* Previous error checking
    if ((calSize == 0) || (calSize > SCAN_DATA_BLOB_SIZE) ||
        (matrixSize == 0) || (matrixSize > REF_CAL_MATRIX_BLOB_SIZE))
        return (ERR_DLPSPEC_INVALID_INPUT);
    */

    // Make a local copy of the input data and deserialize them
    pDesRefScanData = (scanData *)malloc(calSize);
    if (pDesRefScanData == NULL)
        return (ERR_DLPSPEC_INSUFFICIENT_MEM);
    memcpy(pDesRefScanData,pRefCal, calSize);

    pDesRefCalMatrix = (refCalMatrix *)malloc(matrixSize);
    if (pDesRefCalMatrix == NULL)
	{
		ret_val = ERR_DLPSPEC_INSUFFICIENT_MEM;
        goto cleanup_and_exit;
	}

    memcpy(pDesRefCalMatrix, pMatrix, matrixSize);
    ret_val = dlpspec_deserialize((void *)pDesRefCalMatrix, matrixSize, 
			REF_CAL_MATRIX_TYPE);
    if (ret_val < 0)
    {
        goto cleanup_and_exit;
    }

    // Interpret reference scan data - creates scan results from reference scan data
    memset(pRefResults,0,sizeof(scanResults));
    ret_val = dlpspec_scan_interpret(pDesRefScanData, calSize, pRefResults);
    if (ret_val < 0)
    {
        goto cleanup_and_exit;
    }

	/* No need to interpolate if the two scan configs are same */
	if(dlpspec_scan_cfg_compare(&pScanResults->cfg, &pRefResults->cfg) == DLPSPEC_PASS)
	{
		ret_val = dlpspec_scan_scale_for_pga_gain(pScanResults, pRefResults);
        goto cleanup_and_exit;
	}
	
	ret_val = dlpspec_valid_configs_to_interp(&pScanResults->cfg, &pRefResults->cfg);
	if (ret_val < 0)
	{
		goto cleanup_and_exit;
	}
		

    /*
     * Check for data integrity before interpolating wavelengths
     */
	for (i =0; i< pScanResults->length; i++)
	{
		if (pScanResults->wavelength[i] == 0)
        {
            ret_val = (ERR_DLPSPEC_INVALID_INPUT);
            goto cleanup_and_exit;
        }
	}

	for (i =0; i< pRefResults->length; i++)
	{
		if ((pRefResults->wavelength[i] == 0) || (pRefResults->intensity[i] == 0))
        {
            ret_val = (ERR_DLPSPEC_INVALID_INPUT);
            goto cleanup_and_exit;
        }
	}

    /*	Using wavelengths from pScanResults, wavelengths from pRefResults, and magnitudes of pRefResult
     * 	modify refIntensity using piecewise linear interpolation at refNM wavelengths
     */
    ret_val = dlpspec_interpolate_int_wavelengths(pScanResults->wavelength,
                                                  pScanResults->length,
                                                  pRefResults->wavelength,
                                                  pRefResults->intensity,
                                                  pRefResults->length);
    if (ret_val < 0)
    {
        goto cleanup_and_exit;
    }

    // Populate data length - may be required by functions down stream
    pRefResults->length = pScanResults->length;

    /*	Transfer function from pRefResults at the scan configuration taken 
	 *	during reference calibration to the scan configuration used in 
	 *	pScanResults. Inputs will be: refIntensity, scanConfig,
     * 	refWavelength, and the baked in model equation / coefficients. 
	 * 	Primary drivers will be pattern width
     * 	but there may be some differences between linescan and Hadamard also.
     */
    ret_val = dlpspec_scan_recomputeRefIntensities(
			pScanResults, pRefResults, pDesRefCalMatrix);
    if (ret_val < 0)
    {
        goto cleanup_and_exit;
    }

    /*	TBD: Add transfer function from pRefResults at the environmental 
	 *	readings in pRefResults to what it would be in pScanResults with those 
	 *	environmental readings. Inputs will be: refIntensity, refEnvironment, 
	 *	and scanEnvironment and the baked in model equation / coefficients. 
	 *	Primary drivers will be humidity, detector photodiode, and detector 
	 *	temperature
     *  Timeline: v2.0
     */

    cleanup_and_exit:
    if (pDesRefScanData != NULL)
        free(pDesRefScanData);
    if (pDesRefCalMatrix != NULL)
        free(pDesRefCalMatrix);

    return (ret_val);
}

SCAN_TYPES dlpspec_scan_slew_get_cfg_type(const slewScanConfig *pCfg)
/**
 * If the cfg has only one section, returns the type of that section. Otherwise
 * returns type as SLEW_TYPE.
 *
 * @param[in]   pCfg  	        Pointer to slew scan configuration
 *
 * @return      returns the type of scan as defined in SCAN_TYPES enum
 *
 */
{
	if(pCfg->head.num_sections != 1)
		return SLEW_TYPE;
	else
	{
		if(pCfg->section[0].section_scan_type == COLUMN_TYPE)
			return COLUMN_TYPE;
		else
			return HADAMARD_TYPE;
	}
}

int16_t dlpspec_scan_slew_get_num_patterns(const slewScanConfig *pCfg)
/**
 * Returns the total number of patterns in this slew scan. The number returned excludes the count of black
 * patterns inserted during scan to compensate for stray light.
 *
 * @param[in]   pCfg  	        Pointer to slew scan configuration
 *
 * @return      Total number of patterns in this slew scan (does not include the count of black
 * 									patterns inserted during scan to compensate for stray light)
 *
 */
{
    int16_t pattern_count = 0;
    int i;

    if(pCfg == NULL)
        return ERR_DLPSPEC_NULL_POINTER;

    for(i=0; i<pCfg->head.num_sections; i++)
            pattern_count += pCfg->section[i].num_patterns;

    return pattern_count;
}

int16_t dlpspec_scan_slew_get_end_nm(const slewScanConfig *pCfg)
/**
 * Returns the largest wavelength that this slew scan definition includes.
 *
 * @param[in]   pCfg  	        Pointer to slew scan configuration
 *
 * @return      the largest wavelength that this slew scan definition includes.
 *
 */
{

    int16_t end_nm = 0;
    int i;

    if(pCfg == NULL)
        return ERR_DLPSPEC_NULL_POINTER;

    for(i=0; i<pCfg->head.num_sections; i++)
    {
        if(pCfg->section[i].wavelength_end_nm > end_nm)
            end_nm = pCfg->section[i].wavelength_end_nm;
    }

    return end_nm;
}

uint32_t dlpspec_scan_get_exp_time_us(EXP_TIME time_enum)
/**
 * Returns the actual exposure time for a given section in microseconds given the
 * specified enumerated exposure time value. Since the user is not allowed to pass
 * any desired number as the exposure time, we have defined an enum EXP_TIME which
 * is to be passed in the exp_time field of each section in a slew scan definition.
 * Then this function is to be used to converted that enum value to the actual exposure
 * time in microseconds.
 *
 * @param[in]   time_enum  	   Enumerated value that is specified as exposure time.
 *
 * @return      Actual exposure time in microseconds corresponding to the given enum value.
 *
 */
{
	switch(time_enum)
	{
	case 	T_635_US:
		return 635;
	case	T_1270_US:
		return 1270;
	case	T_2450_US:
		return 2450;
	case	T_5080_US:
		return 5080;
	case	T_15240_US:
		return 15240;
	case	T_30480_US:
		return 30480;
	case	T_60960_US:
		return 60960;
	default:
		return 0;
	}
}

DLPSPEC_ERR_CODE dlpspec_scan_section_get_adc_data_range(const slewScanData 
		*pData, int section_index,int *p_section_start_index, uint16_t *p_num_patterns,
		uint16_t *p_num_black_patterns)
/**
 * Given a slew scan data, this function helps separate data corresponding to different
 * sections of the scan. For the given section index, it returns the start index of adc
 * data corresponding to that section, number of non-black patterns in that section and
 * number of black patterns.
 *
 * @param[in]   pData  	    			Pointer to slew scan data
 * @param[in]   section_index         	section specifier
 * @param[out]  p_section_start_index   start index of ADC data corresponding to given section
 * @param[out]  p_num_patterns         	number of patterns (excluding additonally inserted black patterns)
 * 										in the given section.
 * @param[out]  p_num_black_patterns    Number of black patterns inserted during scan corresponding
 * 										to the given section.
 *
 * @return      Error code
 *
 */
{
	uint16_t num_patterns;
	uint16_t num_black_patterns;
    scanConfig cfg;
    int i;
    int j;
    int32_t section_start_index = 0;

    for(i=0; i<=section_index; i++)
    {
        if(pData->slewCfg.section[i].section_scan_type == COLUMN_TYPE)
        {
            num_patterns = pData->slewCfg.section[i].num_patterns;
        }
        else if (pData->slewCfg.section[i].section_scan_type == HADAMARD_TYPE)
        {
            cfg.wavelength_start_nm = pData->slewCfg.section[i].wavelength_start_nm;
            cfg.wavelength_end_nm = pData->slewCfg.section[i].wavelength_end_nm;
            cfg.width_px = pData->slewCfg.section[i].width_px;
            cfg.num_patterns = pData->slewCfg.section[i].num_patterns;
            cfg.num_repeats = pData->slewCfg.head.num_repeats;
            cfg.scan_type = pData->slewCfg.section[i].section_scan_type;

            dlpspec_scan_had_genPatDef(&cfg, &pData->calibration_coeffs, &patDefH);
            num_patterns = patDefH.numPatterns;
        }
        else
        {
            return ERR_DLPSPEC_INVALID_INPUT;
        }

        num_black_patterns = 0;
        for(j=section_start_index; j < (section_start_index + num_patterns + num_black_patterns); j++)
            if((j+1)%pData->black_pattern_period == 0)
            	num_black_patterns++;

        if(i==section_index)
        {
            *p_section_start_index = section_start_index;
            *p_num_patterns = num_patterns;
            *p_num_black_patterns = num_black_patterns;
        }
        else
        {
            section_start_index += (num_patterns + num_black_patterns);
        }
    }

    return DLPSPEC_PASS;
}

DLPSPEC_ERR_CODE format_scan_interpret(void *pBuf, scanResults *pResults)
{
    int i, length;
    void *pBufAdd;
    if(pBuf != NULL)
    {
        length = *((int *) pBuf);
        pResults->length = length;
        pBufAdd = (unsigned char *) pBuf + sizeof(int);
        pBuf = pBufAdd;

        for(i = 0; i < length; i++)
        {
            pResults->wavelength[i] = *((double *)pBuf);
            //printf("%f\t",pResults->wavelength[i]);
            pBufAdd = (unsigned char *) pBuf + sizeof(double);
            pBuf = pBufAdd;

            pResults->intensity[i] = *((int *)pBuf);
            //printf("%d\n",pResults->intensity[i]);
            pBufAdd = (unsigned char *) pBuf + sizeof(int);
            pBuf = pBufAdd;
        }
     }

     return DLPSPEC_PASS;

}
/** @} // group group_scan
 *
 */
