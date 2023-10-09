import bpy
from bpy.props import (StringProperty, FloatProperty,
                        PointerProperty,
                        )

import subprocess
from pathlib import Path
import os
import pip
import numpy as np
import tifffile

bpy.types.Scene.path_zstack = StringProperty(
        name="",
        description="Zstacker executable",
        options = {'TEXTEDIT_UPDATE'},
        default="",
        maxlen=1024,
        subtype='FILE_PATH')

bpy.types.Scene.path_tif = StringProperty(
        name="",
        description="RGB tif file",
        options = {'TEXTEDIT_UPDATE'},
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    
bpy.types.Scene.axes_order = StringProperty(
        name="",
        description="axes order (only z is used currently)",
        default="zyx",
        maxlen=6)
    
bpy.types.Scene.xy_size = FloatProperty(
        name="",
        description="xy physical pixel size in micrometer",
        default=1.0)
    
bpy.types.Scene.z_size = FloatProperty(
        name="z_size",
        description="z physical pixel size in micrometer",
        default=1.0)



# note that this will write a dynamically linked vdb file, so rerunning the script on a file with the same name
# in the same folder, but with different data, will change the previously loaded data.

def make_and_load_vdb(imgdata, x_ix, y_ix, z_ix, axes_order, tif, zstacker_path, z_scale, xy_scale):
    # unpacks z stack into x/y slices in tmp tif files
    # calls zstacker, which assembles this into a vdb
    # deletes tmp files
    # returns the added volume object blender pointer
    # TODO redo x and y orientation from axes_order; rewrite with pyopenvdb
    tmpfiles = []
    zax =  axes_order.find('z')
    for z in range(imgdata.shape[zax]):
        fname = tif.parents[0] / f"tmp_zstacker/{z:04}.tif"
        plane = imgdata.take(indices=z,axis=zax)
        # if axes_order.find('x') > axes_order.find('y'):
        #     plane = plane.T
        tifffile.imwrite(fname, plane)
        tmpfiles.append(fname)
    identifier = str(x_ix)+str(y_ix)+str(z_ix)

    subprocess.run(" ".join([zstacker_path, "-t 1 -z", str(z_scale/xy_scale) ,str(tif.parents[0] / "tmp_zstacker"),  str(tif.with_name(tif.stem + identifier +".vdb"))]), shell=True)

    for tmpfile in tmpfiles:
        tmpfile.unlink()
    
    bpy.ops.object.volume_import(filepath=str(tif.with_name(tif.stem + identifier +".vdb")), align='WORLD', location=(0, 0, 0))
    return bpy.context.view_layer.objects.active

def load_tif(input_file, zstacker_path, xy_scale, z_scale, axes_order):
    
    tif = Path(input_file)

    with tifffile.TiffFile(input_file) as ifstif:
        imgdata = ifstif.asarray()
        print(imgdata.shape)
        imgdata = np.moveaxis(imgdata, 1,2)
        print(imgdata.shape)
        metadata = dict(ifstif.imagej_metadata)


    (tif.parents[0] / "tmp_zstacker/").mkdir(exist_ok=True)

    # 2048 is maximum grid size for Eevee rendering, so grids are split for multiple
    n_splits = [(dim // 2048)+ 1 for dim in imgdata.shape]
    arrays = [imgdata]


    # Loops over all axes and splits based on length
    # reassembles in negative coordinates, parents all to a parent at (half_x, half_y, bottom) that is then translated to (0,0,0)
    volumes =[]
    a_chunks = np.array_split(imgdata, n_splits[0], axis=0)
    for a_ix, a_chunk in enumerate(a_chunks):
        b_chunks = np.array_split(a_chunk, n_splits[1], axis=1)
        for b_ix, b_chunk in enumerate(b_chunks):
            c_chunks = np.array_split(b_chunk, n_splits[2], axis=2)
            for c_ix, c_chunk in enumerate(reversed(c_chunks)):
                vol = make_and_load_vdb(c_chunk, a_ix, b_ix, c_ix, axes_order, tif, zstacker_path, z_scale, xy_scale)
                bbox = np.array([c_chunk.shape[2],c_chunk.shape[1],c_chunk.shape[0]*(z_scale/xy_scale)])
                scale = np.ones(3)*0.02
                vol.scale = scale
                print(c_ix, b_ix, a_ix)
                offset = np.array([-c_ix-1,-b_ix-1,-a_ix-1])
                
                vol.location = tuple(offset*bbox*scale)
                volumes.append(vol)


    # recenter x, y, keep z at bottom
    center = np.array([0.5,0.5,1]) * np.array([c_chunk.shape[2] * (-len(c_chunks)), c_chunk.shape[1] * (-len(b_chunks)), c_chunk.shape[0] * (-len(a_chunks)*(z_scale/xy_scale))])
    empty = bpy.ops.object.empty_add(location=tuple(center*0.02))

    empty = bpy.context.view_layer.objects.active
    empty.name = str(tif.name) + " container" 

    for vol in volumes:
        vol.parent = empty
        vol.matrix_parent_inverse = empty.matrix_world.inverted()

    empty.location = (0,0,0)

    print('done')
    return



