
#from tensorflow.keras.models import load_model
#from tensorflow.keras.utils import get_file

import numpy as np

#from skimage.transform import resize,rescale
#from skimage.feature import shape_index
#from skimage.util import pad,random_noise
#from skimage.io import imread,imsave

#import matplotlib.pyplot as plt

#from MiSiC.utils import *
#from utils_gui import *

#class name is mandatdatory
class SegModel():
    def __init__(self):
        pass
    
    #segment function is manadatory
    def segment(self,im):
        #triviel segementation, segmented.shape = (widht, height, channels) is mandatory
        segmented = np.zeros((im.shape[0],im.shape[1],2))
        segmented[:,:,0] = im > 126
        segmented[:,:,1] = im > 220
        
        return segmented