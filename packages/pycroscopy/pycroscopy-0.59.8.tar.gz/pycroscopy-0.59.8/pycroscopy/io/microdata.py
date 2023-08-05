# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 10:42:03 2015

@author: Suhas Somnath, Numan Laanait

The MicroData classes

"""

from __future__ import division, print_function, absolute_import, unicode_literals
import socket
from warnings import warn

from .io_utils import getTimeStamp


class MicroData(object):
    """
    Generic class that is extended by the MicroDataGroup and MicroDataset objects
    """

    def __init__(self, name, parent):
        """
        Parameters
        ----------
        name : String
            Name of the data group / dataset object
        parent : String
            HDF5 path to the parent of this object. Typically used when
            appending to an existing HDF5 file
        """
        self.name = name
        self.attrs = dict()
        self.parent = parent
        self.indexed = False


class MicroDataGroup(MicroData):
    """
    Holds data that will be converted to a h5.Group by io.ioHDF5
    Note that it can also hold information (e.g. attributes) of an h5.File.
    This is consistent with class hierarchy of HDF5, i.e. h5.File extends h5.Group.
    """

    def __init__(self, name, parent='/'):
        """
        Parameters
        ----------
        name : String
            Name of the data group
        parent : (Optional) String
            HDF5 path to the parent of this object. Typically used when
            appending to an existing HDF5 file
            Default value assumes that this group sits at the root of the file
        """
        super(MicroDataGroup, self).__init__(name, parent)
        self.children = list()
        self.attrs['machine_id'] = socket.getfqdn()
        self.attrs['timestamp'] = getTimeStamp()

        if name != '':
            self.indexed = self.name[-1] == '_'

        pass

    def addChildren(self, children):
        """
        Adds Children to the class to make a tree structure.

        Parameters
        ----------
        children : list of MicroData objects
            Children can be a mixture of groups and datasets

        Returns
        -------
        None
        """
        for child in children:
            if isinstance(child, MicroData):
                child.parent = self.parent + self.name
                self.children.append(child)
            else:
                warn('Children must be of type MicroData.')

    def __str__(self):
        self.showTree()

    def showTree(self):
        """
        Return the tree structure given by MicroDataGroup.
        
        """

        def __tree(child, parent):
            print(parent + '/' + child.name)
            if isinstance(child, MicroDataGroup):
                for ch in child.children:
                    __tree(ch, parent + '/' + child.name)

        # print(self.parent+self.name)
        for child in self.children:
            __tree(child, self.parent + self.name)


class MicroDataset(MicroData):
    """
    Holds data (i.e. numpy.ndarray) as well as instructions on writing, attributes, etc...
    This gets converted to a h5.Dataset by io.ioHDF5.\n    

    Region references need to be specified using the 'labels' attribute. See example below    
    """

    def __init__(self, name, data, dtype=None, compression=None, chunking=None, parent=None, resizable=False,
                 maxshape=None):
        """
        Parameters
        ----------
        name : String
            Name of the dataset
        data : Object
            See supported objects in h5py
        dtype : datatype, 
            typically a datatype of a numpy array =None
        compression : (Optional) String
            See h5py compression. Leave as 'gzip' as a default mode of compression
        chunking : (Optional) tuple of ints
            Chunking in each dimension of the dataset. If not provided, 
            default chunking is used by h5py when writing this dataset
        parent : (Optional) String
                HDF5 path to the parent of this object. This value is overwritten
                when this dataset is made the child of a datagroup.
        resizable : Boolean (Optional. default = False)
            Whether or not this dataset is expected to be resizeable.
            Note - if the dataset is resizable the specified maxsize will be ignored. 
        maxshape : (Optional) tuple of ints
            Maximum size in each axis this dataset is expected to be
            if this parameter is provided, io will ONLY allocate space. 
            Make sure to specify the dtype appropriately. The provided data will be ignored
            
        Examples
        --------   
        1. Small auxillary datasets :
        
        >>> ds_ex_efm = MicroDataset('Excitation_Waveform', np.arange(10))
        
        2. Datasets with slicing information :
        
        >>> ds_spec_inds = MicroDataset('Spectroscopic_Indices', spec_ind_mat)
            ds_spec_inds.attrs['labels'] = {'Time Index':(slice(0,1), slice(None))}
            
        3. Initializing large primary datasets of known sizes :
        
        >>> ds_raw_data = MicroDataset('Raw_Data', data=[], maxshape=(1024,16384), dtype=np.float16,
        >>>                            chunking=(1,16384), compression='gzip')
                    
        4. Intializing large datasets whose size is unknown in one or more dimensions:
        
        >>> ds_raw_data = MicroDataset('Raw_Data', np.zeros(shape=(1,16384), dtype=np.complex64),
        >>>                            chunking=(1,16384), resizable=True,compression='gzip')
        """

        def _make_iterable(item):
            if item is not None:
                if type(item) not in [list, tuple]:  # another (inelegant) way of asking if this object is iterable
                    item = tuple([item])
            return item

        super(MicroDataset, self).__init__(name, parent)
        self.data = data
        self.dtype = dtype
        self.compression = compression
        self.chunking = _make_iterable(chunking)
        self.resizable = resizable
        self.maxshape = _make_iterable(maxshape)
        if resizable is True:
            self.maxshape = None  # Overridden
            self.shape = None
        elif maxshape is not None:
            self.shape = self.maxshape
        else:
            self.shape = self.data.shape

    def __getitem__(self, item):
        return self.data[item]
