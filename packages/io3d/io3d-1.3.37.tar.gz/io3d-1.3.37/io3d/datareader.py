#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Module for readin 3D dicom data
"""

# import funkcí z jiného adresáře
import logging

logger = logging.getLogger(__name__)
import argparse

import numpy as np
import os.path
import sys

try:
    import dicom
except:
    import pydicom as dicom

# -------------------- my scripts ------------


from . import dcmreaddata as dcmr
from . import tgz
from . import misc
from . import dcmtools


# def dicomdir_info(dirpath, *args, **kwargs):
#     """ Get information about seried in dicom dir.
#     Other parameters are described in dcmreaddata.DicomReader.
#     """
#     return dcmreaddata.dicomdir_info(dirpath=dirpath, *args, **kwargs)

def read(datapath, qt_app=None,
         dataplus_format=True, gui=False,
         start=0, stop=None, step=1, convert_to_gray=True, series_number=None, **kwargs):
    """
    Simple read function. Internally call DataReader.Get3DData()
    """
    dr = DataReader()
    return dr.Get3DData(
        datapath=datapath, qt_app=qt_app, dataplus_format=dataplus_format,
        gui=gui, start=start, stop=stop, step=step,
        convert_to_gray=convert_to_gray, series_number=series_number, use_economic_dtype=True,
        **kwargs)


class DataReader:

    def __init__(self):

        self.overlay_fcn = None

    def Get3DData(self, datapath, qt_app=None,
                  dataplus_format=True, gui=False,
                  start=0, stop=None, step=1, convert_to_gray=True, series_number=None,
                  use_economic_dtype=True,
                  **kwargs):
        """
        :datapath directory with input data
        :qt_app if it is set to None (as default) all dialogs for series
        selection are performed in terminal. If qt_app is set to
        QtGui.QApplication() dialogs are in Qt.

        :dataplus_format is new data format. Metadata and data are returned in
        one structure.
        """
        self.orig_datapath = datapath
        datapath = os.path.expanduser(datapath)



        if series_number is not None and type(series_number) != int:
            series_number = int(series_number)

        if not os.path.exists(datapath):
            logger.error("Path '" + datapath + "' does not exist")
            return
        if qt_app is None and gui is True:
            from PyQt4.QtGui import QApplication
            qt_app = QApplication(sys.argv)

        datapath = os.path.normpath(datapath)

        self.start = start
        self.stop = stop
        self.step = step
        self.convert_to_gray = convert_to_gray
        self.series_number = series_number
        self.kwargs = kwargs
        self.qt_app = qt_app
        self.gui = gui


        if os.path.isfile(datapath):
            logger.debug('file read recognized')
            data3d, metadata = self.__ReadFromFile(datapath)

        elif os.path.exists(datapath):
            logger.debug('directory read recognized')
            data3d, metadata = self.__ReadFromDirectory(datapath=datapath)
                # datapath, start, stop, step, gui=gui, **kwargs)
        else:
            logger.error('Data path "%s" not found' % (datapath))

        if convert_to_gray:
            if len(data3d.shape) > 3:
                # @TODO implement better rgb2gray
                data3d = data3d[:, :, :, 0]
        if use_economic_dtype:
            data3d = self.__use_economic_dtype(data3d)

        if dataplus_format:
            logger.debug('dataplus format')
            # metadata = {'voxelsize_mm': [1, 1, 1]}
            datap = metadata
            datap['data3d'] = data3d
            logger.debug('datap keys () : ' + str(datap.keys()))
            return datap
        else:
            return data3d, metadata

    def __ReadFromDirectory(self, datapath): #, start, stop, step, **kwargs):
        start  = self.start
        stop = self.stop
        step = self.step
        kwargs = self.kwargs
        gui = self.gui

        if dcmr.is_dicom_dir(datapath):  # reading dicom
            logger.debug('Dir - DICOM')
            reader = dcmr.DicomReader(datapath, series_number=self.series_number, gui=gui, **kwargs) # qt_app=None, gui=True)
            data3d = reader.get_3Ddata(start, stop, step)
            metadata = reader.get_metaData()
            metadata['series_number'] = reader.series_number
            metadata['datadir'] = datapath
            self.overlay_fcn = reader.get_overlay
        else:  # reading image sequence
            import SimpleITK as sitk
            logger.debug('Dir - Image sequence')

            logger.debug('Getting list of readable files...')
            flist = []
            for f in os.listdir(datapath):
                try:
                    sitk.ReadImage(os.path.join(datapath, f))
                except:
                    logger.warning("Cant load file: " + str(f))
                    continue
                flist.append(os.path.join(datapath, f))
            flist.sort()

            logger.debug('Reading image data...')
            image = sitk.ReadImage(flist)
            logger.debug('Getting numpy array from image data...')
            data3d = sitk.GetArrayFromImage(image)

            metadata = {}  # reader.get_metaData()
            metadata['series_number'] = 0  # reader.series_number
            metadata['datadir'] = datapath
            spacing = image.GetSpacing()
            metadata['voxelsize_mm'] = [
                spacing[2],
                spacing[0],
                spacing[1],
            ]

        return data3d, metadata

    def __use_economic_dtype(self, data3d):
        return misc.use_economic_dtype(data3d)

    def __ReadFromFile(self, datapath):
        path, ext = os.path.splitext(datapath)
        ext = ext[1:]
        if ext in ('pklz', 'pkl'):
            logger.debug('pklz format detected')
            from . import misc
            data = misc.obj_from_file(datapath, filetype='pkl')
            data3d = data.pop('data3d')
            # etadata must have series_number
            metadata = {
                'series_number': 0,
                'datadir': datapath
            }
            metadata.update(data)

        elif ext in ['hdf5']:
            data = self.read_hdf5(datapath)
            data3d = data.pop('data3d')

            # back compatibility
            if 'metadata' in data.keys():
                data = data['metadata']
            # etadata must have series_number
            metadata = {
                'series_number': 0,
                'datadir': datapath
            }
            metadata.update(data)

        elif ext in ['idx']:
            from . import idxformat
            idxreader = idxformat.IDXReader()
            data3d, metadata = idxreader.read(datapath)
        elif ext in ['dcm', 'DCM', 'dicom']:
            data3d, metadata = self._read_with_sitk(datapath)
            metadata = self._fix_sitk_bug(datapath, metadata)
        elif ext in ["bz2"]:
            new_datapath = tgz.untar(datapath)
            data3d, metadata = self.__ReadFromDirectory(new_datapath)
        else:
            logger.debug('file format "' + ext + '"')
            # reading raw file
            data3d, metadata = self._read_with_sitk(datapath)

        return data3d, metadata

    def _read_with_sitk(self, datapath):
        import SimpleITK as sitk
        image = sitk.ReadImage(datapath)
        data3d = dcmtools.get_pixel_array_from_sitk(image)

        # data3d, original_dtype = dcmreaddata.get_pixel_array_from_dcmobj(image)
        metadata = {}  # reader.get_metaData()
        metadata['series_number'] = 0  # reader.series_number
        metadata['datadir'] = datapath
        spacing = image.GetSpacing()
        metadata['voxelsize_mm'] = [
            spacing[2],
            spacing[0],
            spacing[1],
        ]
        return data3d, metadata

    def _fix_sitk_bug(self, path, metadata):
        """
        There is a bug in simple ITK for Z axis in 3D images. This is a fix
        :param path:
        :param metadata:
        :return:
        """
        ds = dicom.read_file(path)
        try:
            metadata["voxelsize_mm"][0] = ds.SpacingBetweenSlices
        except:
            logger.warning("Read dicom 'SpacingBetweenSlices' failed")

        return metadata

    def read_hdf5(self, datapath):
        """
        Method is not implemented
        """
# TODO implement this better, this is not working

        import h5py
        f = h5py.File(datapath, 'r')
        # import ipdb; ipdb.set_trace() #  noqa BREAKPOINT
        dd = self.__read_h5_key(f)
        # datap = {}
        # for item in f.attrs.keys():
        #     datap[item] = f.attrs['item']
        f.close()
        return dd

    def __read_h5_key(self, grp):
        import h5py
        import numpy as np
        retval = {}
        for key in grp.keys():
            data = grp.get(key)
            if type(data) == h5py.Dataset:
                retval[key] = np.array(data)
            elif type(data) == h5py.Group:
                retval[key] = self.__read_h5_key(data)
            else:
                retval[key] = data


        return retval

    def GetOverlay(self):
        """ Generates dictionary of ovelays
        """

        if self.overlay_fcn == None:  # noqa
            return {}
        else:
            return self.overlay_fcn()


def get_datapath_qt(qt_app):
    # just call function from dcmr
    return dcmr.get_datapath_qt(qt_app)


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        '-i', '--inputfile',
        default=None,
        required=True,
        help='input file'
    )
    parser.add_argument(
        '-sn', '--seriesnumber',
        default=None,
        help='seriesnumber'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    data3d, metadata = read(args.inputfile, series_number = args.seriesnumber, dataplus_format=False)

    import sed3
    ed = sed3.sed3(data3d)
    ed.show()


if __name__ == "__main__":
    main()
