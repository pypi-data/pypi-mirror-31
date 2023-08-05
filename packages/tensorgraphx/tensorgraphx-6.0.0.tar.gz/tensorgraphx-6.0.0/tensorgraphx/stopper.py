import sys
import numpy as np

class EarlyStopper(object):

    def __init__(self, max_epoch=100, epoch_look_back=None, percent_decrease=None):
        self.max_epoch = max_epoch
        self.epoch_look_back = epoch_look_back
        self.percent_decrease = percent_decrease
        if self.percent_decrease is None:
            self.percent_decrease = 0

        self.best_valid_error = float(sys.maxsize)
        self.best_epoch_last_update = 0
        self.best_valid_last_update = float(sys.maxsize)
        self.epoch = 0


    def reset(self):
        self.best_valid_error = float(sys.maxsize)
        self.best_epoch_last_update = 0
        self.best_valid_last_update = float(sys.maxsize)
        self.epoch = 0


    def continue_learning(self, valid_error, epoch=None):
        '''check if should continue learning, by default first epoch starts with
           1.
        '''
        if epoch:
            self.epoch = epoch
        else:
            self.epoch += 1
        if valid_error < self.best_valid_error:
            self.best_valid_error = valid_error
        if valid_error < self.best_valid_last_update:
            error_dcr = self.best_valid_last_update - valid_error
        else:
            error_dcr = 0

        # check if should continue learning based on the error decrease
        if self.epoch >= self.max_epoch:
            return False

        elif np.abs(float(error_dcr)/self.best_valid_last_update) > self.percent_decrease:
            self.best_valid_last_update = self.best_valid_error
            self.best_epoch_last_update = self.epoch
            return True

        elif self.epoch_look_back is None:
            return True

        elif self.epoch - self.best_epoch_last_update > self.epoch_look_back:
            return False

        else:
            return True
