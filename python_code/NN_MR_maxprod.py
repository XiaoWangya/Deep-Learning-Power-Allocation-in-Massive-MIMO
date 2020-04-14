import numpy as np
np.random.seed(1337) # for reproducibility

import pdb

import scipy.io as sio
import keras
from keras.layers import Input, Dense, Lambda, Layer, Activation,Dropout,GaussianNoise
from keras.models import Model, Sequential,load_model
from keras import backend as K
from keras import optimizers, metrics
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.initializers import glorot_uniform
from matplotlib import pyplot
from keras.utils.vis_utils import plot_model

def create_relu_advanced(max_value=1.):
    def relu_advanced(x):
        return K.relu(x, max_value=K.cast_to_floatx(max_value))
    return relu_advanced

def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


def rel_mse(x_true, x_pred):
    loss = K.square(K.abs((x_true - x_pred)/ x_true))
    return K.mean(loss, axis=-1)




# cell indexes
cells = [1, 2, 3, 4]

for cell_index in cells:
    # Load input
    mat_contents = sio.loadmat('../../data_input/multi_cell/dataset_maxprod.mat')

    # row numbers input set size columns number training set size
    Input = mat_contents['Input_tr_dB_normalized']
    #output
    Output = mat_contents['Output_tr_MR_maxprod_cell_' + str(cell_index)]

    Input_tr = np.transpose(Input)
    Output_tr = np.transpose(Output)

    # Load maximum power
    p_max = mat_contents['Pmax']

    print("Size input vector", Input.shape)
    print("Size output vector", Output.shape)
    # Size of input vector
    k = Input.shape
    # Number of variable to optimize
    N_input = k[0]
    # Number of training setups
    N_tr = k[1]

    # Maximum number of epochs
    N_max_epoch = 50
    # Batch size
    N_batch_size = 256
    # K_initializer = 'random_normal'
    # B_initializer = 'random_uniform'
    K_initializer = 'glorot_uniform'
    B_initializer = 'zeros'
    K_regularizer = None
    # Neural network configuration
    model = Sequential()
    model.add(Dense(128, activation='elu', name = 'layer1', input_shape=(N_input,), kernel_initializer = K_initializer, bias_initializer=B_initializer))
    model.add(Dense(64, activation='elu', name = 'layer2', kernel_initializer =K_initializer, bias_initializer=B_initializer))
    model.add(Dense(32, activation='elu', name = 'layer3', kernel_initializer = K_initializer, bias_initializer=B_initializer))
    model.add(Dense(32, activation='elu', name = 'layer4', kernel_initializer =K_initializer, bias_initializer=B_initializer))
    #model.add(Dense(32, activation='elu', name='layer5', kernel_initializer=K_initializer, bias_initializer=B_initializer))
    model.add(Dense(5, activation='elu', name = 'layer6', kernel_initializer = K_initializer, bias_initializer=B_initializer))
    model.add(Dense(6, activation='linear', name = 'layer7', trainable= False))
    model.get_layer('layer7').set_weights((np.column_stack([np.identity(5), np.ones(5)]), np.zeros(6)))


    print(model.summary())

    # Initializer
    #keras.initializers.RandomNormal(mean=0.0, stddev=0.5, seed=None)

    # Optimizer
    adam = optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.1)

    # Early stopping
    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0., patience=50, verbose=0, mode='auto')

    # reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.1, patience=5, min_lr=0.00001, verbose=1)
    # callback = [early_stopping, reduce_lr]

    callback = [early_stopping]

    model.compile(loss=rel_mse, optimizer='adam', metrics=[rmse])
    #
    K.set_value(model.optimizer.lr, 0.001)
    history = model.fit(Input_tr, Output_tr, validation_split=0.03125, epochs=N_max_epoch, batch_size=N_batch_size, callbacks=callback)
    #
    K.set_value(model.optimizer.lr, 0.0001)
    history = model.fit(Input_tr, Output_tr, validation_split=0.03125, epochs=N_max_epoch, batch_size=N_batch_size, callbacks=callback)
    #
    K.set_value(model.optimizer.lr, 0.0001)
    history = model.fit(Input_tr, Output_tr, validation_split=0.03125, epochs=N_max_epoch, batch_size=10*N_batch_size, callbacks=callback)
    #
    K.set_value(model.optimizer.lr, 0.00001)
    history = model.fit(Input_tr, Output_tr, validation_split=0.03125, epochs=N_max_epoch, batch_size=10*N_batch_size, callbacks=callback)

    # # plot metrics
    # print(history.history.keys())
    # pyplot.figure(0)
    # pyplot.plot(history.history['loss'])
    # # pyplot.plot(history.history['mean_absolute_error'])
    # pyplot.legend(['mse'], loc='upper right')
    # pyplot.xlabel('epoch')
    # # pyplot.show()
    #
    # pyplot.figure(1)
    # pyplot.plot(history.history['loss'])
    # pyplot.plot(history.history['val_loss'])
    # pyplot.title('model train vs validation loss')
    # pyplot.ylabel('loss')
    # pyplot.xlabel('epoch')
    # pyplot.legend(['train', 'validation'], loc='upper right')
    # # pyplot.show()

    model.save('saved_neural_networks/NN_MR_maxprod_cell_'+ str(cell_index) +'vReduced128.h5')


    # Test the neural network over a sample of data
    mat_contents = sio.loadmat('../../data_input/multi_cell/testset_maxprod.mat')

    # Load data
    Input_test = mat_contents['Input_tr_dB_normalized']

    # Run the neural network
    output_NN = model.predict(np.transpose(Input_test))
    print(output_NN)
    # Save output in a matlab file
    sio.savemat('../../matlab_code/data_output/multi_cell/pow_MR_maxprod_cell_'+ str(cell_index) +'vReduced128.mat', {'Output_test_' + str(cell_index): np.transpose(output_NN)})

    # nbins = 100
    # dim_NN = output_NN.shape
    # print(output_NN)
    # output = mat_contents['output_MR_maxmin_cell_'+ str(cell_index) ]
    # output = np.log10(output)
    # print('mean')
    # print(np.mean(output, axis=0))
    # print('\n')
    #
    # print(np.std(output, axis=0))
    # output = (output - np.mean(output, axis=0)) / np.std(output, axis=0)
    # dim = output.shape
    # output_reshape = np.reshape(output, (1, dim[0] * dim[1]))
    # output_NN_reshape = np.reshape(output_NN, (1, dim_NN[0] * dim_NN[1]))
    #
    # pyplot.figure(2)
    # pyplot.hist(output_NN_reshape[0, ::], bins=nbins)
    # pyplot.hist(output_reshape[0, ::], bins=nbins)
    # pyplot.legend(['powers NN', 'powers'], loc='upper right')
    #
    # pyplot.show()

    print("End")
