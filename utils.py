
from datetime import datetime
import random
import string
import numpy as np
import math
from random import uniform, gauss, triangular

def get_name(length):
    timestamp = datetime.now().strftime("%H%M%S")
    unique = ""
    for x in range(length):
        unique += random.choice(string.ascii_letters)
    return f"{timestamp}{unique}"

def get_random(bits: int, distribution='uniform', samples=1, **kwargs):
    '''

    Generates samples of integer randomly distributed data.

    Parameters
    ----------
    bits: int
        Number of bits for the integer data.
    distribution: string
        Name of the desired random distribution. Could be:
            "gaussian" or "normal" for a normal distribution.
            "uniform" or "rectangular" for a uniform distribution.
            "triangular" for a triangular distribution.
            TODO: Add more distributions
    samples: int
        Number of samples.

    **kwargs (optional)
        median: int
            The center of the distribution (works only for certain distributions)
        std: int
            Standard deviation of the destribution (only gaussian/normal distribution)
        limits: int tuple
            Lower and upper limit of the dataset. By default it takes the whole range of numbers: [0,2^n-1]

    Returns
    -------
    data
        Randomized data sampled from the specified random distribution

    '''
    '''Pasing kwargs'''
    if not 'low_limit' in kwargs:
        low_limit=0 #Lower threshold for generated numbers
    else:
        low_limit=np.min([kwargs['low_limit'],2**bits])
    if not 'high_limit' in kwargs:
        high_limit=2**bits #Upper threshold for the generated data
    else:
        high_limit=np.min([kwargs['high_limit'],2**bits])
    if not 'median' in kwargs:
        median=(high_limit+low_limit)/2 #by default is centered at the mean
    else:
        median=kwargs['median']
    if not 'variance' in kwargs:
        variance=1
    else:
        variance=kwargs['variance']

    '''Distributions case'''
    data=[]
    if distribution in {'uniform', 'rectangular'}:
        data=(int(math.floor(uniform(low_limit,high_limit))) for i in range(samples))
    elif distribution=='triangular':
        data=(int(math.floor(triangular(low_limit,high_limit,mode=median))) for i in range(samples))
    elif distribution in {'normal', 'gaussian'}:
        while len(data)<samples:
            i=int(math.floor(gauss(median,variance)))
            if low_limit<=i<=high_limit: data.append(i)
    else:
        raise ValueError(f'{distribution} is not a valid distribution name')

    return data
