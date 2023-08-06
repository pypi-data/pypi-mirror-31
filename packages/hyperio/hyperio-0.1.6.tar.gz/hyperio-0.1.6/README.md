<img alt='Hyperparameter scanner for Keras Models' src='https://raw.githubusercontent.com/autonomio/hyperio/master/logo.png' width=250px>

## Hyperparameter Scanning for Keras

![Travis branch](https://img.shields.io/travis/autonomio/hyperio/master.svg)[![Coverage Status](https://coveralls.io/repos/github/autonomio/hyperio/badge.svg?branch=master)](https://coveralls.io/github/autonomio/hyperio?branch=master)

Hyperio provides a hyperparameter scanning solution allowing use of any Keras model, with the simple change where instead calling the parameter (e.g. epochs=25), you call a dictionary key with a label (e.g. params['epochs']).

Hyperio is ideal for data scientists and data engineers that want to remain in complete control of their Keras models, but are tired of mindless parameter hopping and confusing optimization solutions that add complexity instead of taking it away.

See the example Notebook [HERE](https://github.com/autonomio/hyperio/blob/master/examples/Hyperparameter%20Optimization%20with%20Keras%20for%20the%20Iris%20Prediction.ipynb)


## Benefits

Based on a review of more than 30 hyperparameter optimization and scanning solutions, Hyperio offers the most intuitive, easy-to-learn, and permissive access to important hyperparameter optimization capabilities.

- works with ANY keras model
- very easy to implement
- adds zero new overhead
- provides several ways to reduce random-search complexity
- no need to learn any new syntax
- no blackbox / other statistical complexity

## Install

    pip install git+https://github.com/autonomio/hyperio.git

## How to use

Let's consider an example of a simple Keras model:

    model = Sequential()
    model.add(Dense(8, input_dim=x_train.shape[1], activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(y_train.shape[1], activation='softmax'))

    model.compile(optimizer='adam',
                  loss=categorical_crossentropy,
                  metrics=['acc'])

    out = model.fit(x_train, y_train,
                    batch_size=20,
                    epochs=200,
                    verbose=0,
                    validation_data=[x_val, y_val])

Now let's see how the exact same model looks like, prepared for Hyperio scan:

	def iris_model(x_train, y_train, x_val, y_val, params):

	    model = Sequential()
	    model.add(Dense(8, input_dim=x_train.shape[1], activation='relu'))
	    model.add(Dropout(params['dropout']))
	    model.add(Dense(y_train.shape[1], activation='softmax'))

	    model.compile(optimizer=params['optimizer']),
	                  loss=params['loss'],
	                  metrics=['acc'])

	    out = model.fit(x_train, y_train,
	                    batch_size=params['batch_size'],
	                    epochs=params['epochs'],
	                    verbose=0,
	                    validation_data=[x_val, y_val])

	    return out

As you can see, the only thing that changed, is the values that we provide for the parameters. We then pass the parameters with a dictionary:

p = {'lr': (2, 10, 30),
     'first_neuron':[4, 8, 16, 32, 64, 128],
     'hidden_layers':[2,3,4,5,6],
     'batch_size': [2, 3, 4],
     'epochs': [300],
     'dropout': (0, 0.40, 10),
     'weight_regulizer':[None],
     'emb_output_dims': [None],
     'optimizer': [Adam, Nadam],
     'loss': [categorical_crossentropy, logcosh],
     'activation':[relu, elu],
     'last_activation': [softmax]}

Hyperio accepts lists with values, and tuples (start, end, n). Learning rate is normalized to 1 so that for each optimizer, lr=1 is the default Keras setting. Once this is all done, we can run the scan:

	h = Hyperio(x, y, params=p, experiment_name='first_test', model=iris_model, grid_downsample=0.5)

## Options

In addition to the parameter, there are several options that can be set within the Hyperio() call. These values will effect the actual scan, as opposed to anything that change for each permutation.

#### val_split

The validation split that will be used for the experiment. By default .3 to validation data.

#### shuffle

If the data should be shuffle before validation split is performed. By default True.

#### search_method

Three modes are offered: 'random', 'linear', and 'reverse'. Random picks randomly one permutation and then removes it from the search grid. Linear starts from the beginning of the grid, and reverse from the end.

#### reduction_method

There is currently one reduction algorithm available 'spear'. It is based on an approach where depending on the 'reduction_interval' and 'reduction_window' poorly performing parameters are dropped from the scan. If you would like to see a specific algorithm implemented, please create an issue for it.

#### reduction_interval

The number of rounds / permutation attempts after which the reduction method will be applied. The 'reduction_method' must be set to other than None for this to take effect.

#### reduction_window

The number of rounds / permutation attempts for looking back when applying the reduction_method. For continuous optimization, this should be less than reduction_interval or the same.

#### grid_downsampling

Takes in a float value based on which a fraction of the total parameter grid will be picked randomly.

#### early_stopping

Provides a callback functionality where once val_loss (validation loss) is no longer dropping, based on the setting, the round will be terminated. Results for the round will be still recorded before moving on to the next permutation. Accepts a string values 'moderate' and 'strict', or a list with two int values (min_delta, patience). Where min_delta indicates the threshhold for change where the round will be flagged for termination (e.g. 0 means that val_loss is not changing) and patience indicates the number of epochs counting from the flag being raised before the round is actual terminated.

#### dataset_name

This information is used for the master log and naming the experiment results round results .csv file.

#### experiment_no

This will be appended to the round results .csv file and together with the dataset_name form a unique handler for the experiment.  

#### hyperio_log_name

The path to the master log file where a log entry is created for every single scan event together with meta-information such as what type of prediction challenge it is, how the data is transformed (e.g. one-hot encoded). This data can be useful for training models for the purpose of optimizing models. That's right, models that make models.

By default hyperio.log is in the present working directory. It's better to change this to something where it has persistence.

#### debug

Useful when you don't want records to be made in to the master log (./hyperio.log)
