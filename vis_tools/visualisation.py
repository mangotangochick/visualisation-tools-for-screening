'''
Tools for advanced visualisations of screening data.

Example:
These methods might serve as the forecast themselves, but are more likely
to be used as a baseline to evaluate if more complex models offer a sufficient
increase in accuracy to justify their use.

Naive1:
    Carry last value forward across forecast horizon (random walk)

SNaive:
    Carry forward value from last seasonal period

Average: np.sqrt(((h - 1) / self._period).astype(np.int)+1)
    Carry forward average of observations

Drift:
    Carry forward last time period, but allow for upwards/downwards drift.

EnsembleNaive:
    An unweighted average of all of the Naive forecasting methods.
'''