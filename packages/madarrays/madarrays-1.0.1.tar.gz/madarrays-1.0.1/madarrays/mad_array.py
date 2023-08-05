# -*- coding: utf-8 -*-
# ######### COPYRIGHT #########
#
# Copyright(c) 2018
# -----------------
#
# * Laboratoire d'Informatique et Systèmes <http://www.lis-lab.fr/>
# * Université d'Aix-Marseille <http://www.univ-amu.fr/>
# * Centre National de la Recherche Scientifique <http://www.cnrs.fr/>
# * Université de Toulon <http://www.univ-tln.fr/>
#
# Contributors
# ------------
#
# * Ronan Hamon <firstname.lastname_AT_lis-lab.fr>
# * Valentin Emiya <firstname.lastname_AT_lis-lab.fr>
# * Florent Jaillet <firstname.lastname_AT_lis-lab.fr>
#
# Description
# -----------
#
# Python package for audio data structures with missing entries
#
# Licence
# -------
# This file is part of madarrays.
#
# madarrays is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ######### COPYRIGHT #########
"""Definition of a masked array.

.. moduleauthor:: Ronan Hamon
.. moduleauthor:: Valentin Emiya
"""
import warnings

import numpy as np


def _merge_masks(ma1, ma2):
    """Merge the masks of two MadArray objects and return the arguments used
    for initialisation of the resulting MadArray.

    Parameters
    ----------
    ma1 : MadArray
       First masked array to consider.
    ma2 : MadArray
       Second masked array to consider.

    Returns
    -------
    dict
        Arguments to be used for the initialisation of a MadArray.
    """
    if ma1._complex_masking or ma2._complex_masking:

        if ma1._complex_masking:
            mm1 = ma1.unknown_magnitude_mask
            mp1 = ma1.unknown_phase_mask
        else:
            mm1 = ma1.unknown_mask
            mp1 = ma1.unknown_mask

        if ma2._complex_masking:
            mm2 = ma2.unknown_magnitude_mask
            mp2 = ma2.unknown_phase_mask
        else:
            mm2 = ma2.unknown_mask
            mp2 = ma2.unknown_mask

        mask_magnitude = np.logical_or(mm1, mm2)
        mask_phase = np.logical_or(mp1, mp2)

        return {'mask_magnitude': mask_magnitude, 'mask_phase': mask_phase}
    else:
        return {'mask': np.logical_or(ma1.unknown_mask, ma2.unknown_mask)}


def _complex_masking_only(f):
    def decorated(self):
        if not self._complex_masking:
            errmsg = 'Method not defined if masking is not complex.'
            raise ValueError(errmsg)
        return f(self)
    return decorated


class MadArray(np.ndarray):
    """Subclass of numpy.ndarray to handle data with missing elements.

    .. _type_entry_madarray:

    **Type of entry**: entries of array can be *int*, *float*, or *complex*.

    .. _masking_madarray:

    **Masking**: the masking of entries has two different modes:

    * entries can be either masked or not masked, leading to a boolean mask,
      whose entries are equal to True if the corresponding data entry is
      masked, or False otherwise. This is the default mode;
    * complex entries can have only the magnitude or phase component masked, or
      both. The resulting mask has integers entries, equal to:

        * *0* if the phase and the magnitude are not masked (known magnitude
          and phase);
        * *1* if only the phase is masked (known magnitude, unknown phase);
        * *2* if only the magnitude is masked (unknown magnitude, known phase);
        * *3* if the magnitude and the phase are masked (unknown magnitude and
          phase).

      This mode is selected by setting :paramref:`complex_masking` to True.
      Entries are converted to a complex type.

    .. _indexing_madarray:

    **Indexing**: two different mode to index a MadArray are implemented:

    * a MadArray array of shape corresponding to the indices is returned, with
      both the data matrix and the mask properly indexed. This is the default
      mode;
    * a MadArray with the shape unchanged is returned, where non-indexed
      entries are set as masked. This mode is selected by setting the parameter
      :paramref:`masked_indexing` to True.

    .. _numpy_behaviour_madarray:

    **Numpy behaviour**: it is possible to use standard operations (+, -, /,
    //, \*, T) between two :class:`MadArray`, likewise operations between numpy
    arrays. The resulting object has a mask consisting of the union of the
    operands. It is also possible to use pickle operations to jointly store the
    data and the mask.

    Parameters
    ----------
    data : array_like
        One-dimensional array. See :ref:`Type of Entry<type_entry_madarray>`.
    mask : boolean array_like, optional
        Mask if type of entry is int or float. See
        :ref:`Masking<masking_madarray>`.
    mask_magnitude : boolean array_like or None, optional
        Magnitude mask if type of entry is complex. See
        :ref:`Masking<masking_madarray>`.
    mask_phase : boolean or array_like or None, optional
        Phase mask if type of entry is complex. See
        :ref:`Masking<masking_madarray>`.
    complex_masking : bool or None, optional
        Indicate how the masking is performed. If None, set to False. See
        :ref:`Masking<masking_madarray>`.
    masked_indexing : bool or None, optional
        Indicate how the indexing is performed. If None, set to False. See
        :ref:`Indexing<indexing_madarray>`.

    Warnings
    --------
    This class inherits from ndarray or subclass of ndarray. Instances can be
    then manipulated like ndarrays (e.g., indexation). While some methods have
    been implemented taking into account the mask, some may cause unexpected
    behavior (e.g., mean).

    See also
    --------
    :mod:`numpy.doc.subclassing`.

    Notes
    -----
    This class implements an alternative masked array different from
    np.ma.MadArray. The reason of this choice is that it is only used as a
    container of a ndarray and a mask. No masked operations are needed.
    """

    def __new__(cls, data, mask=None, mask_magnitude=None, mask_phase=None,
                masked_indexing=None, complex_masking=None, **kwargs):

        _data = np.array(data, **kwargs)

        if complex_masking is None:
            if isinstance(data, MadArray):
                complex_masking = data._complex_masking
            else:
                complex_masking = False

        if masked_indexing is None:
            if isinstance(data, MadArray):
                masked_indexing = data._masked_indexing
            else:
                masked_indexing = False

        if not (np.issubdtype(_data.dtype, np.floating) or
                np.issubdtype(_data.dtype, np.integer) or
                np.issubdtype(_data.dtype, np.complexfloating)):
            errmsg = 'Invalid dtype: {}'
            raise TypeError(errmsg.format(data.dtype))

        if not complex_masking:

            if mask_magnitude is not None:
                warnmsg = 'Argument `mask_magnitude` is ignored.'
                warnings.warn(warnmsg)

            if mask_phase is not None:
                warnmsg = 'Argument `mask_phase` is ignored.'
                warnings.warn(warnmsg)

            if mask is None:
                if isinstance(data, MadArray):
                    mask = data.unknown_mask
                else:
                    mask = np.zeros(_data.shape, dtype=np.bool)
            else:
                mask = np.array(mask, dtype=np.bool)
                if mask.shape != _data.shape:
                    errmsg = "Mask shape {} and data shape {} not compatible."
                    raise ValueError(errmsg.format(mask.shape, data.shape))
                mask = mask

        else:

            if not np.issubdtype(_data.dtype, np.complexfloating):
                _data = _data.astype(np.complex)

            if mask is not None:
                warnmsg = 'Argument `mask` is ignored.'
                warnings.warn(warnmsg)

            if mask_magnitude is None:

                if isinstance(data, MadArray):
                    if data._complex_masking:
                        mask_magnitude = data.unknown_magnitude_mask
                    else:
                        mask_magnitude = data.unknown_mask
                else:
                    mask_magnitude = np.zeros_like(data, dtype=np.bool)
            else:
                if mask_magnitude.shape != _data.shape:
                    errmsg = 'Magnitude mask shape {} and data shape {} not '\
                        'compatible.'
                    raise ValueError(errmsg.format(mask_magnitude.shape,
                                                   _data.shape))

            if mask_phase is None:

                if isinstance(data, MadArray):
                    if data._complex_masking:
                        mask_phase = data.unknown_phase_mask
                    else:
                        mask_phase = data.unknown_mask
                else:
                    mask_phase = np.zeros_like(data, dtype=np.bool)
            else:
                if mask_phase.shape != _data.shape:
                    errmsg = 'Phase mask shape {} and data shape {} not '\
                        'compatible.'
                    raise ValueError(errmsg.format(
                        mask_phase.shape, _data.shape))

            mask = np.zeros(_data.shape, dtype=np.uint8)
            mask[np.logical_and(mask_phase, ~mask_magnitude)] = 1
            mask[np.logical_and(~mask_phase, mask_magnitude)] = 2
            mask[np.logical_and(mask_phase, mask_magnitude)] = 3

        # create the object
        obj = np.ndarray.__new__(cls, _data.shape, dtype=_data.dtype)
        obj[:] = _data
        obj._mask = mask
        obj._masked_indexing = masked_indexing
        obj._complex_masking = complex_masking

        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._mask = getattr(obj, '_mask', None)
        self._complex_masking = getattr(obj, '_complex_masking', None)
        self._masked_indexing = getattr(obj, '_masked_indexing', None)

    def __array_wrap__(self, obj, context=None):
        return obj[()] if obj.shape == () else obj

    def __getitem__(self, index):

        if (getattr(self, '_masked_indexing', None) is not None and
                self._masked_indexing):

            mask = np.zeros(self.shape, dtype=np.bool)
            mask[index] = True
            return MadArray(self, mask=np.logical_or(~mask, self._mask))
        else:
            out_arr = super().__getitem__(index)
            if getattr(out_arr, '_mask', None) is not None:
                out_arr._mask = out_arr._mask[index]
            return out_arr

    def __reduce__(self):
        pickled_state = super().__reduce__()
        new_state = pickled_state[2] + (self._mask, self._complex_masking,
                                        self._masked_indexing)
        return pickled_state[0], pickled_state[1], new_state

    def __setstate__(self, state):
        self._mask = state[-3]
        self._complex_masking = state[-2]
        self._masked_indexing = state[-1]
        super().__setstate__(state[0:-3])

    @property
    def known_mask(self):
        """Boolean mask for known coefficients.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if the corresponding value
            in the object is known. If complex masking, entries set to True if
            both magnitude and phase are known.
        """
        if self._complex_masking:
            return self._mask == 0
        else:
            return ~self._mask

    @property
    def unknown_mask(self):
        """Boolean mask for unknown coefficients.

        Returns
        -------
        boolean nd-array
            Boolean array with values set to True if the corresponding value in
            the object is unknown. If complex masking, entries set to True if
            magnitude and/or phase are unknown.
        """
        if self._complex_masking:
            return self.any_unknown_mask
        else:
            return np.copy(self._mask)

    @property
    @_complex_masking_only
    def any_unknown_mask(self):
        """Boolean mask for coefficients with unknown magnitude and/or phase.

        Not defined if non complex masking.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if magnitude and/or phase
            are unknown.

        Raises
        ------
        ValueError
            If `complex_masking` is False.
        """
        return ~(self._mask == 0)

    @property
    @_complex_masking_only
    def all_unknown_mask(self):
        """Boolean mask for coefficients with both unknown magnitude and phase.

        Not defined if non complex masking.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if both magnitude and phase
            are unknown.

        Raises
        ------
        ValueError
            If `complex_masking` is False.
        """
        return self._mask == 3

    @property
    @_complex_masking_only
    def known_phase_mask(self):
        """Boolean mask for coefficients with known phase.

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if phase is known.

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return ~np.logical_or(self._mask == 1, self._mask == 3)

    @property
    @_complex_masking_only
    def unknown_phase_mask(self):
        """Boolean mask for coefficients with unknown phase.

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if phase is unknown

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return np.logical_or(self._mask == 1, self._mask == 3)

    @property
    @_complex_masking_only
    def known_magnitude_mask(self):
        """Boolean mask for coefficients with known magnitude.

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if magnitude is known.

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return ~np.logical_or(self._mask == 2, self._mask == 3)

    @property
    @_complex_masking_only
    def unknown_magnitude_mask(self):
        """Boolean mask for coefficients with unknown magnitude

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if magnitude is unknown.

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return np.logical_or(self._mask == 2, self._mask == 3)

    @property
    @_complex_masking_only
    def unknown_phase_only_mask(self):
        """Boolean mask for coefficients with unknown phase and known magnitude.

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if phase is unknown and
            magnitude is known.

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return self._mask == 1

    @property
    @_complex_masking_only
    def unknown_magnitude_only_mask(self):
        """Boolean mask for coefficients with unknown magnitude and known phase.

        Not defined for int or float entries.

        Returns
        -------
        boolean nd-array
            Boolean array with entries set to True if magnitude is unknown and
            phase is known.

        Raises
        ------
        ValueError
            If masking is not complex.
        """
        return self._mask == 2

    @property
    def n_missing_data(self):
        """Number of missing data.

        Returns
        -------
        double or tuple
            Number of masked coefficients if dtype is int or float. Number of
            masked coefficients in phase and magnitude masks if dtype is
            complex.

        """
        if self._complex_masking:
            return (np.sum(self.unknown_magnitude_mask),
                    np.sum(self.unknown_phase_mask))
        else:
            return np.sum(self.unknown_mask)

    @property
    def ratio_missing_data(self):
        """Ratio of missing data.

        Returns
        -------
        double or tuple
            Ratio of masked coefficients if dtype is int or float. Ratio of
            masked coefficients in phase and magnitude masks if dtype is
            complex.

        """
        if self._complex_masking:
            return (np.average(self.unknown_magnitude_mask),
                    np.average(self.unknown_phase_mask))
        else:
            return np.average(self.unknown_mask)

    def is_masked(self):
        """Indicate if one or several elements are masked."""
        return np.any(self._mask)

    def to_np_array(self, fill_value=None):
        """Return a numpy array.

        If :paramref:`fill_value` is not None, masked elements are replaced
        according to the type of entries:

        * :paramref:`fill_value` if the type of entries is *int* or *float*;
        * If the type is *complex*, missing entries are replaced either by:
            * a complex number with the known magnitude value without the phase
              information if only the phase is masked;
            * a complex number of magnitude 1 with the known phase if only the
              magnitude is masked;
            * by :paramref:`fill_value` if both magnitude and phase are masked.

        Parameters
        ----------
        fill_value : scalar or None
            Value used to fill masked elements. If None, the initial value is
            kept.

        Returns
        -------
        nd-array
        """
        data = np.array(self)
        if fill_value is not None:
            if self._complex_masking:
                upom = self.unknown_phase_only_mask
                umom = self.unknown_magnitude_only_mask
                data[upom] = np.abs(data[upom])
                data[umom] = np.exp(1j * np.angle(data[umom]))
                data[self.all_unknown_mask] = fill_value
            else:
                data[self.unknown_mask] = fill_value
        return data

    def __add__(self, other):
        if isinstance(other, MadArray):
            if self._complex_masking or other._complex_masking:
                errmsg = 'Operation not permitted when complex masking.'
                raise ValueError(errmsg)

            return MadArray(np.add(self.to_np_array(),
                                   other.to_np_array()),
                            **_merge_masks(self, other),
                            masked_indexing=self._masked_indexing)
        else:
            return super().__add__(other)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        if isinstance(other, MadArray):
            if self._complex_masking or other._complex_masking:
                errmsg = 'Operation not permitted when complex masking.'
                raise ValueError(errmsg)

            return MadArray(np.multiply(self.to_np_array(),
                                        other.to_np_array()),
                            **_merge_masks(self, other),
                            masked_indexing=self._masked_indexing)
        else:
            return super().__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, MadArray):
            if self._complex_masking or other._complex_masking:
                errmsg = 'Operation not permitted when complex masking.'
                raise ValueError(errmsg)

            return MadArray(np.true_divide(self.to_np_array(),
                                           other.to_np_array()),
                            **_merge_masks(self, other),
                            masked_indexing=self._masked_indexing)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, MadArray):
            if self._complex_masking or other._complex_masking:
                errmsg = 'Operation not permitted when complex masking.'
                raise ValueError(errmsg)

            return MadArray(np.floor_divide(self.to_np_array(),
                                            other.to_np_array()),
                            **_merge_masks(self, other),
                            masked_indexing=self._masked_indexing)
        else:
            return super().__floordiv__(other)

    def __eq__(self, other):
        if isinstance(other, MadArray):
            return np.logical_and(self.to_np_array(0) == other.to_np_array(0),
                                  self._mask == self._mask)
        else:
            return np.array(self) == other

    def __ne__(self, other):
        return np.logical_not(self == other)

    def is_equal(self, other):
        if not isinstance(other, MadArray):
            return False

        if not np.all(self == other):
            return False

        if not (self._complex_masking == other._complex_masking and
                self._masked_indexing == other._masked_indexing):
            return False

        return True

    @property
    def T(self):
        """Transpose of the MadArray."""
        return self.transpose()

    def copy(self):
        return MadArray(self)

    def transpose(self):
        mat = super().transpose()
        mat._mask = mat._mask.transpose()
        return mat

    def __str__(self):
        arr = np.array(self)

        if np.issubdtype(self.dtype, np.integer):
            arr = arr.astype(np.float64)

        arr[self.unknown_mask] = np.nan
        arr_str = np.ndarray.__str__(arr)
        arr_str = arr_str.replace('nan', 'x')

        if np.issubdtype(self.dtype, np.integer):
            arr_str = arr_str.replace('.', '')

        string = 'MadArray, dtype={}, {} missing entries ({:.1f}%)\n{}'

        return string.format(self.dtype,
                             self.n_missing_data,
                             100 * self.ratio_missing_data, arr_str)

    def __repr__(self):
        string = '<MadArray at {}>'
        return string.format(hex(id(self)))
