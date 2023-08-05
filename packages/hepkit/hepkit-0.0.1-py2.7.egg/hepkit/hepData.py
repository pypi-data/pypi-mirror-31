import numpy as np
import pandas as pd
import root_numpy as rnp

def PrintPdColumns(df):
	cols = [col for col in df.columns]
	print cols