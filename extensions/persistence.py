# persistence.py
# extension to manage everything Bot5 needs for persistence, i.e. saving and loading files.

import bot5utils
from bot5utils import *
from bot5utils import ext as b5

import pickle


class Persist:
    def __init__(self):
        pass

    # pass a filename and a reference to a pickleable object
    def save(self,filename:str,obj):
        with open(os.gentenv('BOT_CONFIG')+"/"+filename,'wb') as savefile:
            pickle.dump(obj,savefile)

    def load(self,filename:str):
            with open(os.gentenv('BOT_CONFIG')+"/"+filename,"rb") as savefile:
                return pickle.load(savefile)




def setup(bot):
    b5('ext').register('persist',Persist())

def teardown(bot):
    b5('ext').unregister('persist')
