import math

class SecondOrderFilter:
    '''
    Implements a 2nd order IIR filter in an efficient way for realtime
    processing with one sample in and one sample out. No arrays are
    used for processing. Just simple variables.
    '''

    __init__(self):
        self.hold = 0
        self.hold1 = 0
        self.hold2 = 0
        self.a0 = 0
        self.a1 = 0
        self.a2 = 0
        self.b1 = 0
        self.b2 = 0

    def resetState(self):
        '''
        Resets the internal memory of the filter to zero so that the
        output becomes zero.
        '''
        self.hold = 0
        self.hold1 = 0
        self.hold2 = 0

    def filter(self,input):
        '''
        Performs the filter operation sample by sample.
        '''
	    self.hold = input - b1 * self.hold1 - b2 * self.hold2
	    self._output = a0 * self.hold + a1 * self.hold1 + a2 * self.hold2
	    self.hold2 = self.hold1
	    self.hold1 = self.hold
	return self._output

    init_with_zero_pole(self, gain, zero, pole):
        '''
        Valid second order filters have poles and zeros which are complex conjugates of each other
        only need one zero and one pole as parameter.
        '''
        self.a0 = gain
        self.a1 = -2 * gain * zero.real
        self.a2 = gain * ( zero.real * zero.real + zero.imag * zero.imag
        self.b1 = -2 * pole.real
        self.b2 = pole.real * pole.real + pole.imag * pole.imag
        self.hold1 = 0
        self.hold2 = 0

    init_lowpass(self, frequency, qFactor):
        '''
        Setup a lowpass filter with normalised frequency and Q factor (>0.5)
        '''
	    Omega = 2 * math.tan( math.pi * frequency )
	    Omega2 = Omega * Omega
        c0 = 2 * Omega / qFactor
	    c1 = 4 + self.c0 + Omega2
	    self.a0 = Omega2 / c1
	    self.a1 = 2 * self.a0
	    self.a2 = self.a0
	    self.b1 = 2 * (Omega2 - 4) / c1
	    self.b2 = (4 - c0 + Omega2) / c1

    init_highpass(self,frequency, qFactor):
        '''
        Setup a highpass filter with normalised frequency and Q factor (>0.5)
        '''
	    Omega = 2 * math.tan( math.pi * frequency )
	    Omega2 = Omega * Omega

	    c0 = 2 * Omega / qFactor
	    c1 = 4 + self.c0 + Omega2

	    self.a0 = 4 / c1
	    self.a1 = -2 * self.a0
	    self.a2 = self.a0

	    self.b1 = 2 * (Omega2 - 4) / c1
	    self.b2 = (4 - c0 + Omega2) / c1

    normalise(self, frequency, qFactor, stepFunction = False):
        '''
        Normalise the output with a delta pulse (default) or
        a step function by adjusting the FIR coefficients.
        '''
        self.init_lowpass(frequency, qFactor)
	    max = self.filter(1)

        inputValue = 0
        if stepFunction:
            inputValue = 1

	    while self.filter(inputValue) >= max:
		    max = self._output

        if max > 0:
	        a0 /= max
	        a1 /= max
	        a2 /= max
        
        self.resetState()
