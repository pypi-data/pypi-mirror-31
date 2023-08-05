import pandas as pd
import matplotlib.pyplot as plt

def DefaultSetup():
	plt.rcParams['font.family'] = 'serif'
	plt.rcParams['font.weight'] = 'light'
	plt.rcParams['font.size'] = 16
	plt.rcParams['figure.figsize'] = [12,8]
	pd.options.display.max_columns = 999