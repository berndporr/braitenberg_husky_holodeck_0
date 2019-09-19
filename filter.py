import math

class SecondOrderFilter:
    '''
    Implements a 2nd order IIR filter in an efficient way for realtime
    processing with one sample in and one sample out. No arrays are
    used for processing. Just simple variables.
    '''
    
    def __init__(self):
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
        self.hold = input - self.b1 * self.hold1 - self.b2 * self.hold2
        self._output = self.a0 * self.hold + self.a1 * self.hold1 + self.a2 * self.hold2
        self.hold2 = self.hold1
        self.hold1 = self.hold
        return self._output

    def init_with_zero_pole(self, gain, zero, pole):
        '''
        Valid second order filters have poles and zeros which are complex conjugates of each other
        only need one zero and one pole as parameter.
        '''
        self.a0 = gain
        self.a1 = -2 * gain * zero.real
        self.a2 = gain * ( zero.real * zero.real + zero.imag * zero.imag )
        self.b1 = -2 * pole.real
        self.b2 = pole.real * pole.real + pole.imag * pole.imag
        self.hold1 = 0
        self.hold2 = 0

    def init_lowpass(self, frequency, qFactor = 0.49):
        '''
        Setup a lowpass filter with normalised frequency and Q factor (>0.5)
        '''
        Omega = 2 * math.tan( math.pi * frequency )
        Omega2 = Omega * Omega
        c0 = 2 * Omega / qFactor
        c1 = 4 + c0 + Omega2
        self.a0 = Omega2 / c1
        self.a1 = 2 * self.a0
        self.a2 = self.a0
        self.b1 = 2 * (Omega2 - 4) / c1
        self.b2 = (4 - c0 + Omega2) / c1

    def init_highpass(self,frequency, qFactor = 0.71):
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

    def normalise(self, frequency, qFactor, stepFunction = False):
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


def calc_impulse_response(filename,lp):
    f = open(filename,"w")
    lp.filter(0)
    v = lp.filter(1)
    for i in range(1000):
        f.write(str(v))
        f.write("\n")
        v = lp.filter(0)
    f.close



def unitTest():
    lp = SecondOrderFilter()
    lp.init_lowpass(0.1,1)
    calc_impulse_response("impulse_q1.dat",lp)
    lp = SecondOrderFilter()
    lp.init_lowpass(0.1)
    calc_impulse_response("impulse_damped.dat",lp)

if __name__ == "__main__":
    unitTest()