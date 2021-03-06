from keras.datasets import mnist
import numpy as np
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K
from keras import optimizers

def auto_encoder(input_size):
    input_img = Input(shape=(input_size, input_size,3))  # adapt this if using `channels_first` image data format

    x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x= MaxPooling2D((2, 2), padding='same')(x)
    encoded = Conv2D(32, (3, 3), activation='relu', padding='same')(x)

    # at this point the representation is (7, 7, 32)

    x = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(32, (3, 3,), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
<<<<<<< HEAD
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    decoded = Conv2D(1, (2, 2), activation='relu', padding='valid')(x)

    model = Model(input_img, decoded)
    opt=optimizers.adadelta(lr=0.01)
    model.compile(opt, loss='mean_squared_error')
    
    return model
=======
    decoded = Conv2D(3, (2, 2), activation='sigmoid', padding='valid')(x)

    model = Model(input_img, decoded)
    opt = optimizers.adadelta(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=opt, loss='mean_squared_error')

    return model
>>>>>>> 9fa128b598a9a44b93920c8ff98ce4abc8de4abe
