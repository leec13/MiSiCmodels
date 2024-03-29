import argparse 
import warnings

import os, sys
from os.path import dirname, basename, isfile, join
import importlib
import importlib.util
from pathlib import Path

import glob
from pathlib import Path

from skimage.io import imsave,imread
import skimage.io
from skimage.measure import label
from skimage.transform import rescale, resize

import tiffile as tiffile
import numpy as np


import napari
from napari.layers import Image
from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider
from magicgui import event_loop, magicgui

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#from MiSiC.MiSiC import *
#import MiSiCgui
from MiSiCmodels.utils import *

import models

gdict = {"gDir":"", "gfilename" : os.path.join("~", "out.tif"), "gdims" : None, "width" : None, "gnoise" : None, "gthresh":220, "ginvert" : None, "gpos" : None, "gsave_all" : None, "gchannel":0}

p = Path(__file__).parents[1]
p = join(p, "models")
modpaths = glob.glob(join(Path(p), "*.py"))
print(modpaths)

MODELS = [ basename(f)[:-3] for f in modpaths if isfile(f) and not f.endswith('__init__.py')]
print(MODELS)

mmodd = MODELS[0]
#modpath = modpaths[MODELS.index("misic_synthetic_b")]
amodel = "models."+ mmodd
currentModel = importlib.import_module(amodel)

misic = currentModel.SegModel()

viewer = None

def updatemeta(metadict = gdict, idx = 1):
    viewer.layers[idx].metadata = metadict


def seg_img(im, scale=1, noise="0.000", invert=True, frame=0, save=False, threshold=220):
    
    noise = float(noise)
    rtim = np.zeros(gdict["gdims"])
    p = gdict["gpos"]
    global thresh
    thresh = threshold

    if save:
        print("running...")
        hyperS = np.zeros(im.shape)
        for iT in range(im.shape[0]) :
            imp = im[iT,:,:]
            sr,sc = imp.shape
            imp = rescale(imp,scale)
            if noise > 0 : imp = random_noise(imp,mode = 'gaussian',var = noise)
            imp = normalize2max(imp)
            y1 = misic.segment(imp,invert = invert)
            y = np.zeros((sr,sc,1))
            y[:,:,0] = resize(rescale(y1[:,:,gdict["gchannel"]],1.0/scale),(sr,sc))
            #y[:,:,1] = resize(rescale(y1[:,:,1],1.0/scale),(sr,sc))
            if rtim.ndim == 3 : rtim[iT,:,:] = (y[:,:,0])
            elif rtim.ndim == 4 : rtim[iT,p[1],:,:] = (y[:,:,0])
            else: rtim[iT,p[1],p[2],:,:] = (y[:,:,0])
            hyperS[iT,:,:] =  (y[:,:,0])
            print("time = ", iT)
            #print("Finish")
            savestr = "all"
    
    

    else :
        print("running...")
        hyperS = np.zeros(im.shape)
        sr,sc = im.shape
        im = rescale(im,scale)
        if noise > 0 : im = random_noise(im, mode = 'gaussian', var = noise)
        im = normalize2max(im)
        y1 = misic.segment(im,invert = invert)
        y = np.zeros((sr,sc,1))
        y[:,:,0] = resize(rescale(y1[:,:,gdict["gchannel"]],1.0/scale),(sr,sc))
        #y[:,:,1] = resize(rescale(y1[:,:,1],1.0/scale),(sr,sc))
        if rtim.ndim == 2 : rtim[:,:] = (y[:,:,0])
        elif rtim.ndim == 3 : rtim[p[0],:,:] = (y[:,:,0])
        elif rtim.ndim == 4 : rtim[p[0],p[1],:,:] = (y[:,:,0])
        else: rtim[p[0],p[1],p[2],:,:] = (y[:,:,0])
        hyperS =  (y[:,:,0])
        savestr = str(frame)
    

    gshape = viewer.layers[-1].metadata["gdims"]
    gshape = "_".join([str(i) for i in gshape])

    width = str(gdict["width"])

    imsave(str(gdict["gfilename"])+"_W="+width+"_N="+str(noise)+"_DIM="+gshape+"_frame="+savestr+"_mask.tif",(255.0*hyperS).astype(np.uint8))
    print("Finish")
    return((255.0*rtim).astype(np.uint8))

def main():
    with napari.gui_qt():
        global viewer
        viewer = napari.Viewer()

        def updatelayer(layer):
            viewer.layers[-1].metadata=gdict
            gui.refresh_choices("layer")
            viewer.layers[-1].metadata=gdict
            print("event", layer)

        def defaultpath(apath):
            global gdict    
            #viewer.add_image(tifffile.imread(apath))
            print("avant",os.path.join(apath, viewer.layers[0].name))
            gdict["gDir"] = apath
            gdict["gfilename"] = os.path.join(apath, viewer.layers[0].name)
            print("apres",gdict["gfilename"])
        
        def loadmodel(apath):   
            print("model=",apath)
            global misic
            spec = importlib.util.spec_from_file_location("module.name", apath)
            currentModel = importlib.util.module_from_spec(spec)
            #currentModel = importlib.import_module(apath)
            spec.loader.exec_module(currentModel)
            misic = currentModel.SegModel()
            return None
            
        
        def changelabels(thresh):
            #& ("seg" not in laynames)
            gui1.value = thresh
            print(thresh)
            laynames = [ l.name for l in viewer.layers]
            if ('seg' in laynames):
                i = laynames.index("seg")
                viewer.layers.pop(i)

            if ('image_mask result' in laynames)  :
                im = viewer.layers['image_mask result'].data > (thresh)
                label_image = label(im)
                viewer.add_labels(label_image, name="seg")
                gdict["gthresh"] = thresh
        




        @magicgui(call_button="get_mask", noise={"fixedWidth": 50}, layout="vertical")
        def image_mask(layer: Image, mean_width = 6, noise = "0.00", PhaseContrast = True, process_all = False) -> Image:
            global gdict
            p = tuple([int(round(x)) for x in viewer.dims.point])
            #print("pressed", viewer.layers)
            if process_all & (layer.data.ndim > 2) :
                if layer.data.ndim == 5 : img = layer.data[:, p[1], p[2],:,:]
                elif layer.data.ndim == 4 : img = layer.data[:, p[1],:,:]
                elif layer.data.ndim == 3 : img = layer.data[:,:,:]
                else: img = layer.data
                gdict["gfilename"] = os.path.join(gdict["gDir"], layer.name)
                gdict["gdims"] = layer.data.shape
                gdict["width"] = mean_width
                gdict["gnoise"] = noise
                gdict["ginvert"] = PhaseContrast
                gdict["gpos"] = p
                gdict["gsave_all"] = process_all

                updatemeta(gdict, 0)
                return seg_img(img, scale=round(10/mean_width, 2), noise=noise, invert=PhaseContrast, frame = viewer.dims.point[0], save=process_all)

            else:
                if layer.data.ndim == 5 : img = layer.data[p[0], p[1], p[2],:,:]
                elif layer.data.ndim == 4 : img = layer.data[p[0], p[1],:,:]
                elif layer.data.ndim == 3 : img = layer.data[p[0],:,:]
                else: img = layer.data
                gdict["gfilename"] = os.path.join(gdict["gDir"], layer.name)
                gdict["gdims"] = layer.data.shape
                gdict["width"] = mean_width
                gdict["gnoise"] = noise
                gdict["ginvert"] = PhaseContrast
                gdict["gpos"] = p
                gdict["gsave_all"] = process_all

                updatemeta(gdict, 0)
                return seg_img(img, scale=round(10/mean_width, 2), noise=noise, invert=PhaseContrast, frame = viewer.dims.point[0], save=process_all)
        

        #viewer.grid_view()
        # instantiate the widget
        gui = image_mask.Gui()
        # add our new widget to the napari viewer
        viewer.window.add_dock_widget(gui, area="right")
        
        # keep the dropdown menus in the gui in sync with the layer model
        #viewer.layers.events.changed.connect(lambda x: gui.refresh_choices("layer"))
        viewer.layers.events.changed.connect(updatelayer)



        @magicgui(
            auto_call=True,
            threshold={'widget_type': QSlider, 'minimum': 1, 'maximum': 255, 'orientation':Qt.Horizontal, "fixedWidth": 600},
            value = {"fixedWidth": 50}
        )
        def make_labels(threshold = 220, value = "220"):
            return threshold
        gui1 = make_labels.Gui(show = True)
        viewer.window.add_dock_widget(gui1)
        #viewer.window.add_dock_widget(label={'widget_type': QLabel, 'text':"label"})
        gui1.threshold_changed.connect(changelabels)

        @magicgui(call_button="save_labels")
        def funcsave_labels():
            imsave(str(gdict["gfilename"])+"_thresh_"+str(gdict["gthresh"])+"_labels.tif",(-4294967295.0*viewer.layers["seg"].data).astype(np.uint32))
            return None
        gui4 = funcsave_labels.Gui(show=True)
        viewer.window.add_dock_widget(gui4)

        @magicgui(call_button="HELP")
        def funcHELP():
            #print("debut")
            msg = QMessageBox()
            msg.setWindowTitle("Help1")
            msg.setText("read Napari : https://napari.org/tutorials/\n"+
            "read the doc : https://github.com/leec13/MiSiCgui\n"+
            "0 - drag and drop the image\n"
            "1 - select default directory\n"+
            "2 - Add a shape layer\n"+
            "3 - trace some widths\n"+
            "4 - get the mean width (button)\n"+
            "5 - set the mean width (field)\n"+
            "6 - get the mask\n"+
            "7 - to create segmentation mouve threshold cursor (only 2D and Time Lapse)")
            msg.exec_()
           
            return None
        gui5 = funcHELP.Gui(show=True)
        viewer.window.add_dock_widget(gui5)

        @magicgui(call_button="get_WIDTH", mean_width={"disabled": True, "fixedWidth": 50})
        def meanfunc(mean_width=""):
            if (viewer.layers[-1].name == "Shapes") & (viewer.layers[-1].selected) :
                data = viewer.layers[-1].data
                c = 0
                for d in data:
                    c += (sum((d[1,:] - d[0,:])**2))**0.5
                return(str(round(c/len(data))))
            else : return ""

        gui3 = meanfunc.Gui(show=True)
        viewer.window.add_dock_widget(gui3, area="right")
        gui3.called.connect(lambda result: gui3.set_widget("mean_width", result))

        @magicgui(default_dir={"mode": "existing_directory"})
        def filepicker(default_dir=Path("~")):
            return default_dir
        # instantiate the widget
        gui2 = filepicker.Gui(show=True)
        viewer.window.add_dock_widget(gui2, area="right")
        gui2.default_dir_changed.connect(defaultpath)

        @magicgui(auto_call=True, model_file={"mode": "r"})
        def modelpicker(model_file=Path("~"), channel = 0):
            gdict["gchannel"] = channel
            return model_file
        # instantiate the widget
        gui22 = modelpicker.Gui(show=True)
        viewer.window.add_dock_widget(gui22, area="right")
        gui22.model_file_changed.connect(loadmodel)

        
        # @magicgui(auto_call=True, models_list={"choices": MODELS})
        # def sel_model(models_list=MODELS[0], channel = 0) :
        #     global misic
        #     gdict["gchannel"] = channel
        #     #amodel = "models."+models_list
        #     currentModel = importlib.import_module(amodel)
        #     #print(currentModel)
        #     #modpath = '/Users/leon/Desktop/Equipes_Local/SP/models/h5/MiSiDC04082020.h5'
        #     modpath = modpaths[MODELS.index(models_list)]
        #     misic = currentModel.SegModel()
        #     print(models_list)
        #     return None
        # gui6 = sel_model.Gui(show = True)
        # viewer.window.add_dock_widget(gui6, area="right")
        

            
        #viewer.grid_view()


if __name__ == "__main__":
    # execute only if run as a script
    main()
