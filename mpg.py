from __future__ import print_function, absolute_import, division

import numpy as np
import pandas as pd

import pathlib 

import matplotlib.pyplot as plt
import seaborn as sns

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

'''
====================================
'''

dataset_path = keras.utils.get_file("auto-mpg.data", "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data")

column_names = ['MPG','Cylinders','Displacement','HorsePower','Weight','Acceleration',
'Model Year', 'Origin']

raw_dataset = pd.read_csv(dataset_path, names = column_names, na_values = '?',
comment = '\t', sep = ' ',skipinitialspace = True)
dataset = raw_dataset.copy()

'''
==========================================
'''
dataset = dataset.dropna()
origin = dataset.pop('Origin')
dataset['USA'] = (origin == 1)*1.0
dataset['Europe'] = (origin == 2)*1.0
dataset['Japan'] = (origin == 3)*1.0

train_dataset = dataset.sample(frac = 0.8, random_state = 0)
test_dataset = dataset.drop(train_dataset.index)

#sns.pairplot(train_dataset[['MPG','Cylinders','Displacement','Weight']], diag_kind = 'kde')

train_stats = train_dataset.describe()
train_stats.pop('MPG')
train_stats = train_stats.transpose()

train_labels = train_dataset.pop('MPG')
test_labels = test_dataset.pop('MPG')

def norm(x):
	return (x - train_stats['mean'])/(train_stats['std'])
normed_train_data = norm(train_dataset)
normed_test_data = norm(test_dataset)

def build_model():
	
	model = keras.Sequential([
	layers.Dense(64, activation = tf.nn.relu, input_shape = [len(train_dataset.keys())]),
	layers.Dense(64, activation = tf.nn.relu),
	layers.Dense(1)
	])
	optimizer = tf.keras.optimizers.RMSprop(0.001)
	
	model.compile(loss = 'mean_squared_error', optimizer = optimizer, metrics = ['mean_absolute_error','mean_squared_error'])
	return model

model = build_model()

class PrintDot(keras.callbacks.Callback):
	def on_epoch_end(self,epoch,logs):
		if epoch % 100 == 0:
			print('')
		print('.', end = ' ')

EPOCHS = 1000

early_stop = keras.callbacks.EarlyStopping(monitor = 'val_loss', patience = 10)
history = model.fit(
  normed_train_data, train_labels,
  epochs = EPOCHS, validation_split = 0.2, verbose = 0,
  callbacks = [early_stop,PrintDot()])

def plot_history(history):
	hist = pd.DataFrame(history.history)
	hist['epoch'] = history.epoch
	
	plt.figure()
	plt.xlabel('#epochs')
	plt.ylabel('mean abs error [MPG]')
	plt.plot(hist['epoch'],hist['mean_absolute_error'], label = 'Train Error')
	plt.plot(hist['epoch'],hist['val_mean_absolute_error'], label = 'Val Error')
	plt.ylim([0,5])
	plt.legend()
	
	plt.figure()
	plt.xlabel('#epochs')
	plt.ylabel('mean abs error [$MPG^2$]')
	plt.plot(hist['epoch'],hist['mean_squared_error'], label = 'Train Error')
	plt.plot(hist['epoch'],hist['val_mean_squared_error'], label = 'Val Error')
	plt.ylim([0,20])
	plt.legend()
	plt.show()
	
test_predictions = model.predict(normed_test_data).flatten() #vectorize the result

plt.scatter(test_labels, test_predictions)
plt.xlabel('True Value [MPG]')
plt.ylabel('Predicted Value [MPG]')
plt.axis('equal')
plt.axis('square')
plt.xlim([0,plt.xlim()[1]])
plt.ylim([0,plt.ylim()[1]])
_ = plt.plot([-100,100],[-100,100])
plt.show()