"""File readers for various commercial instruments."""
import os
import re
import codecs

import numpy as np

from .conf import config

trioptics_enc = 'cp1252'


def read_trioptics_mtfvfvf(file_path):
    """Read MTF vs Field vs Focus data from a Trioptics .txt dump.

    Parameters
    ----------
    file_path : `str` or path_like
        path to read data from

    Returns
    -------
    `MTFvFvF`
        MTF vs Field vs Focus object

    """
    with open(file_path, 'r') as fid:
        lines = fid.readlines()
        imghts, objangs, focusposes, mtfs = [], [], [], []
        for meta, data in zip(lines[0::2], lines[1::2]):  # iterate 2 lines at a time
            metavalues = meta.split()
            imght, objang, focuspos, freqpitch = metavalues[1::2]
            mtf_raw = data.split()[1:]  # first element is "MTF"
            mtf = np.asarray(mtf_raw, dtype=config.precision)
            imghts.append(imght)
            objangs.append(objang)
            focusposes.append(focuspos)
            mtfs.append(mtf)

    if str(file_path)[-7:-4] == 'Tan':
        azimuth = 'Tan'
    else:
        azimuth = 'Sag'

    focuses = np.unique(np.asarray(focusposes, dtype=config.precision))
    focuses = (focuses - np.mean(focuses)) * 1e3
    imghts = np.unique(np.asarray(imghts, dtype=config.precision))
    freqs = np.arange(len(mtfs[0]), dtype=config.precision) * float(freqpitch)
    data = np.swapaxes(np.asarray(mtfs).reshape(len(focuses), len(imghts), len(freqs)), 0, 1)
    return {
        'data': data,
        'focus': focuses,
        'field': imghts,
        'freq': freqs,
        'azimuth': azimuth
    }


def read_trioptics_mtf_vs_field(file_path):
    """Read tangential and sagittal MTF data from a Trioptics .mht file.

    Parameters
    ----------
    file_path : `str` or path_like
        path to a file

    Returns
    -------
    `dict`
        dictionary with keys of freq, field, tan, sag

    """
    # read the file into memory and handle ISO-8859-1 to UTF-8 for non windows platforms
    with codecs.open(file_path, mode='r', encoding=trioptics_enc) as fid:
        data = codecs.encode(fid.read(), 'utf-8').decode('utf-8')

        # compile a pattern that will search for the image heights in the file and extract
        fields_pattern = re.compile(f'MTF=09{os.linesep}(.*?){os.linesep}Legend=09', flags=re.DOTALL)
        fields = fields_pattern.findall(data)[0]  # two copies, only need 1st

        # make a pattern that will search for and extract the tan and sag MTF data.  The match will
        # return two copies; one for vs imght, one for vs angle.  Only keep half the matches.
        tan_pattern = re.compile(r'Tan(.*?)=97', flags=re.DOTALL)
        sag_pattern = re.compile(r'Sag(.*?)=97', flags=re.DOTALL)
        tan, sag = tan_pattern.findall(data), sag_pattern.findall(data)
        endpt = len(tan) // 2
        tan, sag = tan[:endpt], sag[:endpt]

        # now extract the freqs from the tan data
        freqs = np.asarray([float(s.split('(')[0][1:]) for s in tan])

        # lastly, extract the floating point tan and sag data
        # also take fields, to the 4th decimal place (nearest .1um)
        # reformat T/S to 2D arrays with indices of (freq, field)
        tan = np.asarray([s.split('=09')[1:-1] for s in tan], dtype=config.precision)
        sag = np.asarray([s.split('=09')[1:-1] for s in sag], dtype=config.precision)
        fields = np.asarray(fields.split('=09')[0:-1], dtype=config.precision).round(4)
        return {
            'freq': freqs,
            'field': fields,
            'tan': tan,
            'sag': sag,
        }


def read_trioptics_mtf(file_path):
    """Read MTF data from a Trioptics data file.

    Parameters
    ----------
    file_path : path_like
        location of a .mht certificate file

    Returns
    -------
    `dict`
        dictionary with keys focus, wavelength, freq, tan, sag

    """
    # read the file into memory and handle ISO-8859-1 to UTF-8 for non windows platforms
    with codecs.open(file_path, mode='r', encoding=trioptics_enc) as fid:
        data = codecs.encode(fid.read(), 'utf-8').decode('utf-8')

    # compile regex scanners to grab wavelength, focus, and frequency information
    # in addition to the T, S MTF data.
    # lastly, compile a scanner to cut the file after the end of the "MTF Sagittal" scanner
    focus_scanner = re.compile(r'Focus Position  : (\-?\d+\.\d+) mm')
    wavelength_scanner = re.compile(r'Wavelength      : (\d+) nm')
    data_scanner = re.compile(r'\r\n(\d+\.?\d?)=09\r\n(\d+\.\d+)=09')
    sag_scanner = re.compile(r'Measurement Table: MTF vs. Frequency \( Sagittal \)')
    blockend_scanner = re.compile(r'  _____ =20')

    sagpos, cutoff = sag_scanner.search(data).end(), None
    for blockend in blockend_scanner.finditer(data):
        if blockend.end() > sagpos and cutoff is None:
            cutoff = blockend.end()

    # get focus and wavelength
    focus_pos = float(focus_scanner.search(data).group(1))
    wavelength = float(wavelength_scanner.search(data).group(1)) / 1e3  # nm to um

    # simultaneously grab frequency and MTF
    result = data_scanner.findall(data[:cutoff])
    freqs, mtfs = [], []
    for dat in result:
        freqs.append(float(dat[0]))
        mtfs.append(dat[1])

    breakpt = len(mtfs) // 2
    t = np.asarray(mtfs[:breakpt], dtype=config.precision)
    s = np.asarray(mtfs[breakpt:], dtype=config.precision)
    freqs = tuple(freqs[:breakpt])

    return {
        'focus': focus_pos,
        'wavelength': wavelength,
        'freq': freqs,
        'tan': t,
        'sag': s,
    }
