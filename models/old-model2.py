
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import get_file

import numpy as np

from skimage.transform import resize,rescale
from skimage.feature import shape_index
from skimage.util import pad,random_noise
from skimage.io import imread,imsave

import matplotlib.pyplot as plt

from MiSiC.utils import *
#from utils_gui import *

class SegModel():
    def __init__(self):
        #self.size = 256
        self.scalesvals = [1,1.5,2.0]
        #self.model = load_model(model_name)
        #model_path = get_file(
        #    'old-model.txt',
        #    'https://github.com/pswapnesh/Models/raw/master/old-model.h5', cache_dir='./cache')
        self.model = None
    
    def preprocess(self,im):
        n = len(self.scalesvals)
        # sh = np.zeros((im.shape[0],im.shape[1],n))
        
        # if np.max(im) ==0:
        #     return sh
        # pw = 15
        # im = pad(im,pw,'reflect')
        # sh = np.zeros((im.shape[0],im.shape[1],n))    
        # for i in range(n):
        #     sh[:,:,i] = shape_index(im,self.scalesvals[i])
     
        return None
    
    def segment(self,im,invert = False):
        # im = normalize2max(im)        
        # pw = 16
        # if invert:
        #     im = 1.0-im
        # im = pad(im,pw,'reflect')
        # sh = self.preprocess(im)

        # tiles,params = extract_tiles(sh,size = self.size,padding = 8)

        # yp = self.model.predict(tiles)
        segmented = np.zeros((im.shape[0],im.shape[1],2))
        segmented[:,:,0] = im > 126
        segmented[:,:,1] = im > 220

        return segmented