#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017.

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of satpy.

# satpy is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# satpy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# satpy.  If not, see <http://www.gnu.org/licenses/>.

# New stuff

import glob
import itertools
import logging
import numbers
import os
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import deque, namedtuple
from fnmatch import fnmatch

import numpy as np
import six
import yaml

from pyresample.geometry import StackedAreaDefinition, SwathDefinition
from satpy.config import recursive_dict_update
from satpy.dataset import DATASET_KEYS, Dataset, DatasetID
from satpy.readers import DatasetDict
from satpy.readers.helper_functions import get_area_slices, get_sub_area
from trollsift.parser import globify, parse

logger = logging.getLogger(__name__)

Shuttle = namedtuple('Shuttle', ['data', 'mask', 'info'])


def listify_string(something):
    """Takes *something* and make it a list.

    *something* is either a list of strings or a string, in which case the
    function returns a list containing the string.
    If *something* is None, an empty list is returned.
    """
    if isinstance(something, (str, six.text_type)):
        return [something]
    elif something is not None:
        return list(something)
    else:
        return list()


def get_filebase(path, pattern):
    """Get the end of *path* of same length as *pattern*."""
    # A pattern can include directories
    tail_len = len(pattern.split(os.path.sep))
    return os.path.join(*path.split(os.path.sep)[-tail_len:])


def match_filenames(filenames, pattern):
    """Get the filenames matching *pattern*."""
    matching = []

    for filename in filenames:
        if fnmatch(get_filebase(filename, pattern), globify(pattern)):
            matching.append(filename)

    return matching


class AbstractYAMLReader(six.with_metaclass(ABCMeta, object)):

    def __init__(self, config_files):
        self.config = {}
        self.config_files = config_files
        for config_file in config_files:
            with open(config_file) as fd:
                self.config = recursive_dict_update(self.config, yaml.load(fd))

        self.info = self.config['reader']
        self.name = self.info['name']
        self.file_patterns = []
        for file_type, filetype_info in self.config['file_types'].items():
            filetype_info.setdefault('file_type', file_type)
            # correct separator if needed
            file_patterns = [os.path.join(*pattern.split('/'))
                             for pattern in filetype_info['file_patterns']]
            self.file_patterns.extend(file_patterns)

        if not isinstance(self.info['sensors'], (list, tuple)):
            self.info['sensors'] = [self.info['sensors']]
        self.sensor_names = self.info['sensors']
        self.datasets = self.config.get('datasets', {})
        self.info['filenames'] = []
        self.ids = {}
        self.load_ds_ids_from_config()

    @property
    def all_dataset_ids(self):
        return self.ids.keys()

    @property
    def all_dataset_names(self):
        # remove the duplicates from various calibration and resolutions
        return set(ds_id.name for ds_id in self.all_dataset_ids)

    @property
    def available_dataset_ids(self):
        logger.warning(
            "Available datasets are unknown, returning all datasets...")
        return self.all_dataset_ids

    @property
    def available_dataset_names(self):
        return (ds_id.name for ds_id in self.available_dataset_ids)

    @abstractproperty
    def start_time(self):
        """Start time of the reader."""

    @abstractproperty
    def end_time(self):
        """End time of the reader."""

    @abstractmethod
    def filter_selected_filenames(self, filenames):
        """Filter provided filenames by parameters in reader configuration.

        Returns: iterable of usable files

        """

    @abstractmethod
    def load(self, dataset_keys):
        """Load *dataset_keys*."""

    def supports_sensor(self, sensor):
        """Check if *sensor* is supported.

        Returns True is *sensor* is None.
        """
        if sensor and not (set(self.info.get("sensors")) &
                           set(listify_string(sensor))):
            return False
        else:
            return True

    def select_files_from_directory(self, directory=None):
        """Find files for this reader in *directory*.

        If directory is None or '', look in the current directory.
        """
        filenames = []
        if directory is None:
            directory = ''
        for pattern in self.file_patterns:
            matching = glob.iglob(os.path.join(directory, globify(pattern)))
            filenames.extend(matching)
        return filenames

    def select_files_from_pathnames(self, filenames):
        """Select the files from *filenames* this reader can handle."""
        selected_filenames = []

        for pattern in self.file_patterns:
            matching = match_filenames(filenames, pattern)
            selected_filenames.extend(matching)
        if len(selected_filenames) == 0:
            logger.warning("No filenames found for reader: %s", self.name)

        return selected_filenames

    def get_ds_ids_by_wavelength(self, wavelength, ids=None):
        """Get the dataset ids matching a given a *wavelength*."""
        if ids is None:
            ids = self.ids
        if isinstance(wavelength, (tuple, list)):
            datasets = [ds for ds in ids
                        if ds.wavelength == tuple(wavelength)]
        else:
            datasets = [ds for ds in ids if ds.wavelength
                        and ds.wavelength[0] <= wavelength <= ds.wavelength[2]]
            datasets = sorted(datasets,
                              key=lambda ch: abs(ch.wavelength[1] - wavelength))
        if not datasets:
            raise KeyError("Can't find any projectable at %sum" %
                           str(wavelength))

        return datasets

    def get_ds_ids_by_id(self, dsid, ids=None):
        """Get the dataset ids matching a given a dataset id."""
        if ids is None:
            ids = self.ids.keys()
        for key in DATASET_KEYS:
            value = getattr(dsid, key)
            if value is None or (key == 'modifiers' and not value):
                # filter everything else except modifiers if it isn't
                # specified (None or tuple())
                continue
            if key == "wavelength":
                ids = self.get_ds_ids_by_wavelength(dsid.wavelength, ids)
            else:
                ids = [ds_id for ds_id in ids if value == getattr(ds_id, key)]
        if len(ids) == 0:
            raise KeyError(
                "Can't find any projectable matching '{}'".format(dsid))
        return ids

    def get_ds_ids_by_name(self, name, ids=None):
        """Get the datasets ids by *name*."""
        if ids is None:
            ids = self.ids
        datasets = [ds_id for ds_id in ids if ds_id.name == name]
        if not datasets:
            raise KeyError("Can't find any projectable called '{}'".format(
                name))

        return datasets

    @staticmethod
    def dfilter_from_key(dfilter, key):
        """Create a dataset filter from a *key*."""
        if dfilter is None:
            dfilter = {}
        else:
            dfilter = dfilter.copy()
        for attr in ['calibration', 'polarization', 'resolution']:
            dfilter[attr] = dfilter.get(attr) or getattr(key, attr, None)
        # modifiers default is an empty tuple so handle it specially
        dfilter['modifiers'] = dfilter.get('modifiers',
                                           getattr(key, 'modifiers', None) or None)

        for attr in ['calibration', 'polarization', 'resolution']:
            if (dfilter[attr] is not None
                    and not isinstance(dfilter[attr], (list, tuple, set))):
                dfilter[attr] = [dfilter[attr]]
        return dfilter

    @staticmethod
    def _get_best_calibration(calibration):
        # default calibration choices
        if calibration is None:
            calibration = ["brightness_temperature", "reflectance", 'radiance',
                           'counts']
        else:
            calibration = [x
                           for x in ["brightness_temperature", "reflectance",
                                     "radiance", "counts"] if x in calibration]
        return calibration

    def _ds_ids_with_best_calibration(self, datasets, calibration):
        """Get the datasets with the best available calibration."""

        calibrations = self._get_best_calibration(calibration)

        new_datasets = []

        for cal in calibrations:
            for ds_id in datasets:
                if ds_id.calibration == cal:
                    new_datasets.append(ds_id)
        for ds_id in datasets:
            if (ds_id not in new_datasets and
                    (ds_id.calibration is None and calibration is None)):
                new_datasets.append(ds_id)
        return new_datasets

    def _ds_ids_from_any_key(self, key):
        """Return a dataset ids from any type of key."""
        if isinstance(key, numbers.Number):
            datasets = self.get_ds_ids_by_wavelength(key)
        elif isinstance(key, DatasetID):
            datasets = self.get_ds_ids_by_id(key)
        else:
            datasets = self.get_ds_ids_by_name(key)

        return datasets

    def filter_ds_ids(self, dataset_ids, dfilter):
        """Filter *dataset_ids* based on *dfilter*."""
        # sort by resolution, highest resolution first (lowest number)
        dataset_ids = sorted(dataset_ids, key=lambda x: x.resolution or -1)

        for attr in ['resolution', 'polarization']:
            if dfilter.get(attr) is not None:
                dataset_ids = [ds_id for ds_id in dataset_ids
                               if getattr(ds_id, attr) in dfilter[attr]]

        calibration = dfilter.get('calibration')
        dataset_ids = self._ds_ids_with_best_calibration(dataset_ids,
                                                         calibration)

        if dfilter.get('modifiers') is not None:
            dataset_ids = [ds_id for ds_id in dataset_ids
                           if ds_id.modifiers == dfilter['modifiers']]

        return dataset_ids

    def get_dataset_key(self, key, dfilter=None, aslist=False):
        """Get the fully qualified dataset id corresponding to *key*.

        Can be either by name or centerwavelength. If `key` is a `DatasetID`
        object its name is searched if it exists, otherwise its wavelength is
        used.
        """
        datasets = self._ds_ids_from_any_key(key)

        dfilter = self.dfilter_from_key(dfilter, key)

        datasets = self.filter_ds_ids(datasets, dfilter)

        if not datasets:
            raise KeyError("Can't find any projectable matching '{}'".format(
                str(key)))
        if aslist:
            return datasets
        else:
            return datasets[0]

    def load_ds_ids_from_config(self):
        """Get the dataset ids from the config."""
        ids = []
        for dataset in self.datasets.values():
            # Build each permutation/product of the dataset
            id_kwargs = []
            for key in DATASET_KEYS:
                val = dataset.get(key)
                if key in ["wavelength", "modifiers"] and isinstance(val,
                                                                     list):
                    # special case: wavelength can be [min, nominal, max]
                    # but is still considered 1 option
                    # it also needs to be a tuple so it can be used in
                    # a dictionary key (DatasetID)
                    id_kwargs.append((tuple(val), ))
                elif key == "modifiers" and val is None:
                    # empty modifiers means no modifiers applied
                    id_kwargs.append((tuple(), ))
                elif isinstance(val, (list, tuple, set)):
                    # this key has multiple choices
                    # (ex. 250 meter, 500 meter, 1000 meter resolutions)
                    id_kwargs.append(val)
                elif isinstance(val, dict):
                    id_kwargs.append(val.keys())
                else:
                    # this key only has one choice so make it a one
                    # item iterable
                    id_kwargs.append((val, ))
            for id_params in itertools.product(*id_kwargs):
                dsid = DatasetID(*id_params)
                ids.append(dsid)

                # create dataset infos specifically for this permutation
                ds_info = dataset.copy()
                for key in DATASET_KEYS:
                    if isinstance(ds_info.get(key), dict):
                        ds_info.update(ds_info[key][getattr(dsid, key)])
                    # this is important for wavelength which was converted
                    # to a tuple
                    ds_info[key] = getattr(dsid, key)
                self.ids[dsid] = ds_info

        return ids


class FileYAMLReader(AbstractYAMLReader):
    """Implementation of the YAML reader."""

    def __init__(self,
                 config_files,
                 filter_parameters=None,
                 filter_filenames=True,
                 **kwargs):
        super(FileYAMLReader, self).__init__(config_files)

        self.file_handlers = {}
        self.filter_filenames = self.info.get('filter_filenames', filter_filenames)
        self.filter_parameters = filter_parameters or {}
        if kwargs:
            logger.warning("Unrecognized/unused reader keyword argument(s) '{}'".format(kwargs))

    @property
    def available_dataset_ids(self):
        for ds_id in self.all_dataset_ids:
            fts = self.ids[ds_id]["file_type"]
            if isinstance(fts, str) and fts in self.file_handlers:
                yield ds_id
            elif any(ft in self.file_handlers for ft in fts):
                yield ds_id

    @property
    def start_time(self):
        if not self.file_handlers:
            raise RuntimeError("Start time unknown until files are selected")
        return min(x[0].start_time for x in self.file_handlers.values())

    @property
    def end_time(self):
        if not self.file_handlers:
            raise RuntimeError("End time unknown until files are selected")
        return max(x[-1].end_time for x in self.file_handlers.values())

    @staticmethod
    def check_file_covers_area(file_handler, check_area):
        """Checks if the file covers the current area.

        If the file doesn't provide any bounding box information or 'area'
        was not provided in `filter_parameters`, the check returns True.
        """
        from trollsched.boundary import AreaDefBoundary, Boundary
        from satpy.resample import get_area_def
        try:
            gbb = Boundary(*file_handler.get_bounding_box())
        except NotImplementedError:
            pass
        else:
            abb = AreaDefBoundary(get_area_def(check_area), frequency=1000)

            intersection = gbb.contour_poly.intersection(abb.contour_poly)
            if not intersection:
                return False
        return True

    def find_required_filehandlers(self, requirements, filename_info):
        """Find the necessary fhs for the current filehandler.

        We assume here requirements are available.
        """
        req_fh = []
        if requirements:
            for requirement in requirements:
                for fhd in self.file_handlers[requirement]:
                    # FIXME: Isn't this super wasteful? filename_info.items()
                    # every iteration?
                    if (all(item in filename_info.items()
                            for item in fhd.filename_info.items())):
                        req_fh.append(fhd)
                        break
                else:
                    raise RuntimeError('No matching file in ' + requirement)
                    # break everything and continue to next
                    # filetype!
        return req_fh

    def sorted_filetype_items(self):
        """Sort the instance's filetypes in using order."""
        processed_types = []
        file_type_items = deque(self.config['file_types'].items())
        while len(file_type_items):
            filetype, filetype_info = file_type_items.popleft()

            requirements = filetype_info.get('requires')
            if requirements is not None:
                # requirements have not been processed yet -> wait
                missing = [req for req in requirements
                           if req not in processed_types]
                if missing:
                    file_type_items.append((filetype, filetype_info))
                    continue

            processed_types.append(filetype)
            yield filetype, filetype_info

    @staticmethod
    def filename_items_for_filetype(filenames, filetype_info):
        """Iterator over the filenames matching *filetype_info*."""
        for pattern in filetype_info['file_patterns']:
            for filename in match_filenames(filenames, pattern):
                try:
                    filename_info = parse(
                        pattern, get_filebase(filename, pattern))
                except ValueError:
                    logger.debug("Can't parse %s with %s.", filename, pattern)
                    continue

                yield filename, filename_info

    def new_filehandler_instances(self, filetype_info, filename_items):
        """Generate new filehandler instances."""
        requirements = filetype_info.get('requires')
        filetype_cls = filetype_info['file_reader']
        for filename, filename_info in filename_items:
            try:
                req_fh = self.find_required_filehandlers(requirements,
                                                         filename_info)
            except RuntimeError:
                logger.warning("Can't find requirements for %s", filename)
                continue
            except KeyError:
                logger.warning("Missing requirements for %s", filename)
                continue

            yield filetype_cls(filename, filename_info, filetype_info, *req_fh)

    def time_matches(self, fstart, fend):
        start_time = self.filter_parameters.get('start_time')
        end_time = self.filter_parameters.get('end_time')
        if start_time and fend and fend < start_time:
            return False
        if end_time and fstart and fstart > end_time:
            return False
        return True

    def metadata_matches(self, sample_dict, file_handler=None):
        # special handling of start/end times
        if not self.time_matches(
                sample_dict.get('start_time'), sample_dict.get('end_time')):
            return False

        for key, val in self.filter_parameters.items():
            if key not in sample_dict:
                continue

            fval = sample_dict[key]
            if key in ['start_time', 'end_time']:
                continue
            elif key == 'area' and file_handler and \
                    not self.check_file_covers_area(file_handler, val):
                break
            elif val != fval:
                # don't use this file
                break
        else:
            # all the metadata keys are equal
            return True
        return False

    def filter_filenames_by_info(self, filename_items):
        """Filter out file using metadata from the filenames.

        Currently only uses start and end time. If only start time is available
        from the filename, keep all the filename that have a start time before
        the requested end time.
        """
        for filename, filename_info in filename_items:
            fend = filename_info.get('end_time')
            fstart = filename_info.setdefault('start_time', fend)
            if fend and fend < fstart:
                # correct for filenames with 1 date and 2 times
                fend = fend.replace(year=fstart.year,
                                    month=fstart.month,
                                    day=fstart.day)
                filename_info['end_time'] = fend
            if self.metadata_matches(filename_info):
                yield filename, filename_info

    def filter_fh_by_metadata(self, filehandlers):
        """Filter out filehandlers using provide filter parameters."""
        for filehandler in filehandlers:
            filehandler.metadata['start_time'] = filehandler.start_time
            filehandler.metadata['end_time'] = filehandler.end_time
            if self.metadata_matches(filehandler.metadata, filehandler):
                yield filehandler

    def filter_selected_filenames(self, filenames):
        for filetype, filetype_info in self.sorted_filetype_items():
            filename_iter = self.filename_items_for_filetype(filenames,
                                                             filetype_info)
            if self.filter_filenames:
                filename_iter = self.filter_filenames_by_info(filename_iter)

            for fn, _ in filename_iter:
                yield fn

    def new_filehandlers_for_filetype(self, filetype_info, filenames):
        """Create filehandlers for a given filetype."""
        filename_iter = self.filename_items_for_filetype(filenames,
                                                         filetype_info)
        if self.filter_filenames:
            # preliminary filter of filenames based on start/end time
            # to reduce the number of files to open
            filename_iter = self.filter_filenames_by_info(filename_iter)
        filehandler_iter = self.new_filehandler_instances(filetype_info,
                                                          filename_iter)
        filtered_iter = self.filter_fh_by_metadata(filehandler_iter)
        return list(filtered_iter)

    def create_filehandlers(self, filenames):
        """Organize the filenames into file types and create file handlers."""
        logger.debug("Assigning to %s: %s", self.info['name'], filenames)

        self.info.setdefault('filenames', []).extend(filenames)
        filename_set = set(filenames)

        for filetype, filetype_info in self.sorted_filetype_items():
            filehandlers = self.new_filehandlers_for_filetype(filetype_info,
                                                              filename_set)

            filename_set -= set([fhd.filename for fhd in filehandlers])
            if filehandlers:
                self.file_handlers[filetype] = sorted(
                    filehandlers,
                    key=lambda fhd: (fhd.start_time, fhd.filename))

    @staticmethod
    def get_shape_n_slices(all_shapes, xslice=slice(None), yslice=slice(None)):
        """Get the shape and slices to use."""
        # rows accumlate, columns stay the same
        overall_shape = [sum([x[0]
                              for x in all_shapes]), ] + all_shapes[0][1:]
        if xslice.start is not None and yslice.start is not None:
            slice_shape = [yslice.stop - yslice.start,
                           xslice.stop - xslice.start]
            overall_shape[0] = min(overall_shape[0], slice_shape[0])
            overall_shape[1] = min(overall_shape[1], slice_shape[1])
        elif len(overall_shape) == 1:
            yslice = slice(0, overall_shape[0])
        else:
            xslice = slice(0, overall_shape[1])
            yslice = slice(0, overall_shape[0])
        return overall_shape, xslice, yslice

    @staticmethod
    def _load_entire_dataset(dsid, ds_info, file_handlers):
        """Load the entire dataset as inplace loading isn't an option."""
        # can't optimize by using inplace loading
        projectables = []
        for fh in file_handlers:
            projectable = fh.get_dataset(dsid, ds_info)
            if projectable is not None:
                projectables.append(projectable)

        # Join them all together
        combined_info = file_handlers[0].combine_info(
            [p.info for p in projectables])
        cls = ds_info.get("container", Dataset)
        return cls(np.ma.vstack(projectables), **combined_info)

    def _load_sliced_dataset(self, dsid, ds_info, file_handlers, xslice, yslice):
        """Load only a piece of the dataset."""
        # we can optimize
        cls = ds_info.get("container", Dataset)
        all_shapes = [list(fhd.get_shape(dsid, ds_info))
                      for fhd in file_handlers]
        overall_shape, xslice, yslice = self.get_shape_n_slices(all_shapes,
                                                                xslice,
                                                                yslice)

        out_info = {'reader': self.name}
        data = np.empty(overall_shape,
                        dtype=ds_info.get('dtype', np.float32))
        mask = np.ma.make_mask_none(overall_shape)

        offset = 0
        out_offset = 0
        failure = True
        for idx, fh in enumerate(file_handlers):
            segment_height = all_shapes[idx][0]
            # XXX: Does this work with masked arrays and subclasses of them?
            # Otherwise, have to send in separate data, mask, and info parameters to be filled in
            # TODO: Combine info in a sane way

            if (yslice.start >= offset + segment_height or
                    yslice.stop <= offset):
                offset += segment_height
                continue
            start = max(yslice.start - offset, 0)
            stop = min(yslice.stop - offset, segment_height)

            shuttle = Shuttle(data[out_offset:out_offset + stop - start],
                              mask[out_offset:out_offset + stop - start],
                              out_info)

            kwargs = {}
            if stop - start != segment_height:
                kwargs['yslice'] = slice(start, stop)
            if (xslice.start is not None and
                    xslice.stop - xslice.start != all_shapes[idx][1]):
                kwargs['xslice'] = xslice

            try:
                fh.get_dataset(dsid, ds_info, out=shuttle, **kwargs)
                failure = False
            except KeyError:
                logger.warning(
                    "Failed to load {} from {}".format(dsid, fh), exc_info=True)
                mask[out_offset:out_offset + stop - start] = True

            out_offset += stop - start
            offset += segment_height

        if failure:
            raise KeyError(
                "Could not load {} from any provided files".format(dsid))

        out_info.pop('area', None)
        return cls(data, mask=mask, copy=False, **out_info)

    def _load_dataset_data(self,
                           file_handlers,
                           dsid,
                           xslice=slice(None),
                           yslice=slice(None)):
        ds_info = self.ids[dsid]
        try:
            # Can we allow the file handlers to do inplace data writes?
            [list(fhd.get_shape(dsid, ds_info)) for fhd in file_handlers]
        except NotImplementedError:
            # FIXME: Is NotImplementedError included in Exception for all
            # versions of Python?
            proj = self._load_entire_dataset(dsid, ds_info, file_handlers)
        else:
            proj = self._load_sliced_dataset(dsid, ds_info, file_handlers,
                                             xslice, yslice)
        # FIXME: areas could be concatenated here
        # Update the metadata
        proj.info['start_time'] = file_handlers[0].start_time
        proj.info['end_time'] = file_handlers[-1].end_time

        return proj

    def _preferred_filetype(self, filetypes):
        """Get the preferred filetype out of the *filetypes* list.

        At the moment, it just returns the first filetype that has been loaded.
        """

        if not isinstance(filetypes, list):
            filetypes = [filetypes]

        # look through the file types and use the first one that we have loaded
        for filetype in filetypes:
            if filetype in self.file_handlers:
                return filetype
        return None

    def _load_area_def(self, dsid, file_handlers):
        """Load the area definition of *dsid*."""
        area_defs = [fh.get_area_def(dsid) for fh in file_handlers]
        area_defs = [area_def for area_def in area_defs
                     if area_def is not None]

        final_area = StackedAreaDefinition(*area_defs)
        return final_area.squeeze()

    def _get_coordinates_for_dataset_key(self, dsid):
        """Get the coordinate dataset keys for *dsid*."""
        ds_info = self.ids[dsid]
        cids = []

        for cinfo in ds_info.get('coordinates', []):
            if isinstance(cinfo, dict):
                cinfo['resolution'] = ds_info['resolution']
            else:
                # cid = self.get_dataset_key(cinfo)
                cinfo = {'name': cinfo, 'resolution': ds_info['resolution']}
            cid = DatasetID(**cinfo)
            cids.append(self.get_dataset_key(cid))

        return cids

    def _get_coordinates_for_dataset_keys(self, dsids):
        """Get all coordinates."""
        coordinates = {}
        for dsid in dsids:
            cids = self._get_coordinates_for_dataset_key(dsid)
            coordinates.setdefault(dsid, []).extend(cids)
        return coordinates

    def _get_file_handlers(self, dsid):
        """Get the file handler to load this dataset."""
        ds_info = self.ids[dsid]

        filetype = self._preferred_filetype(ds_info['file_type'])
        if filetype is None:
            logger.warning("Required file type '%s' not found or loaded for "
                           "'%s'", ds_info['file_type'], dsid.name)
        else:
            return self.file_handlers[filetype]

    def _make_area_from_coords(self, coords):
        """Create an apropriate area with the given *coords*."""
        if len(coords) == 2:
            lon_sn = coords[0].info.get('standard_name')
            lat_sn = coords[1].info.get('standard_name')
            if lon_sn == 'longitude' and lat_sn == 'latitude':
                sdef = SwathDefinition(*coords)
                sensor_str = sdef.name = '_'.join(self.info['sensors'])
                shape_str = '_'.join(map(str, coords[0].shape))
                sdef.name = "{}_{}_{}_{}".format(sensor_str, shape_str,
                                                 coords[0].info['name'],
                                                 coords[1].info['name'])
                return sdef
            else:
                raise ValueError(
                    'Coordinates info object missing standard_name key: ' +
                    str(coords))
        elif len(coords) != 0:
            raise NameError("Don't know what to do with coordinates " + str(
                coords))

    def _load_dataset_area(self, dsid, file_handlers, coords):
        """Get the area for *dsid*."""
        try:
            return self._load_area_def(dsid, file_handlers)
        except NotImplementedError:
            if any(x is None for x in coords):
                logger.warning(
                    "Failed to load coordinates for '{}'".format(dsid))
                return None

            area = self._make_area_from_coords(coords)
            if area is None:
                logger.debug("No coordinates found for %s", str(dsid))
            return area

    # TODO: move this out of here.
    def _get_slices(self, area):
        """Get the slices of raw data covering area.

        Args:
            area: the area to slice.

        Returns:
            slice_kwargs: kwargs to pass on to loading giving the span of the
                data to load.
            area: the trimmed area corresponding to the slices.
        """
        slice_kwargs = {}

        if area is not None and self.filter_parameters.get('area') is not None:
            try:
                slices = get_area_slices(area, self.filter_parameters['area'])
                area = get_sub_area(area, *slices)
                slice_kwargs['xslice'], slice_kwargs['yslice'] = slices
            except (NotImplementedError, AttributeError):
                logger.info("Cannot compute specific slice of data to load.")

        return slice_kwargs, area

    def _load_dataset_with_area(self, dsid, coords):
        """Loads *dsid* and it's area if available."""
        file_handlers = self._get_file_handlers(dsid)
        if not file_handlers:
            return

        area = self._load_dataset_area(dsid, file_handlers, coords)
        slice_kwargs, area = self._get_slices(area)

        try:
            ds = self._load_dataset_data(file_handlers, dsid, **slice_kwargs)
        except (KeyError, ValueError) as err:
            logger.exception("Could not load dataset '%s': %s", dsid, str(err))
            return None

        if area is not None:
            ds.info['area'] = area
        return ds

    def load(self, dataset_keys):
        """Load *dataset_keys*."""
        all_datasets = DatasetDict()
        datasets = DatasetDict()

        # Include coordinates in the list of datasets to load
        dsids = [self.get_dataset_key(ds_key) for ds_key in dataset_keys]
        coordinates = self._get_coordinates_for_dataset_keys(dsids)
        all_dsids = list(set().union(*coordinates.values())) + dsids

        for dsid in all_dsids:
            coords = [all_datasets.get(cid, None)
                      for cid in coordinates.get(dsid, [])]
            ds = self._load_dataset_with_area(dsid, coords)
            if ds is not None:
                all_datasets[dsid] = ds
                if dsid in dsids:
                    datasets[dsid] = ds

        return datasets
