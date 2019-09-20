import Filter
import random

# which state for exploration
class ExploreStates(Enum):
    EXPLORE_STRAIGHT = 0
    EXPLORE_LEFT = 1
    EXPLORE_RIGHT = 2
    EXPLORE_STOP = 3


def weightChange(self, w, delta):
    '''
    changes a synaptic weight "w" by the amount "delta"
    and makes sure it never goes below 0 and above 1
    '''
    w += delta
    if w > 1:
        w = 1
    if w < 0:
        w = 0
    return w



class Limbic_system:
    

    def ofc5HTreceptors(x, htR1, htR2):
        htR1 = htR1 + self.OFC_5HTR1_OFFSET
        htR2 = htR2 + self.OFC_5HTR2_OFFSET
        r = (1-exp(-math.pow(x/htR1,htR1)))*htR2
        if (r < 0.00001):
            return 0;
        return r;


    def __init__(self):
        # simulation step counter
        self.step = 0

        # shunting inhibition is implemented as:
        # neuronal_activity / ( 1 + inhibition * shunting_inhibition_factor )
        self.shunting_inhibition_factor = 200

        self.OFC_5HTR1_OFFSET = 0
        self.OFC_5HTR2_OFFSET = 0

        ##############################################################
        # NAcc core
        ##############################################################
	
        # I see the light green object and I approach the light
        # green one
        self.core_weight_lg2lg = 0.2

        # I see the dark green object and I approach the dark green one
        self.core_weight_dg2dg = 0.2

        # motor activities
        self.CoreGreenOut = 0
        self.CoreBlueOut = 0
        self.mPFC2CoreExploreLeft = 0
        self.mPFC2CoreExploreRight = 0

        # learning rate of the core
        self.learning_rate_core = 0.075

        # dopamine activity
        self.core_DA = 0

        # is positive if DA is elevated and neg if there's a DA dip
        self.core_plasticity = 0

        # counter after which the rat starts exploring
        self.coreExploreCtr = 0;


        #################################################################
        # NAcc l-shell
        #################################################################

        # l-shell activity
        self.lShell = 0

        # dopamine activity
        self.shell_DA = 0

        # is positive if DA is elevated and neg if there's a DA dip
        self.shell_plasticity = 0

        # weights for the shell system
        self.lShell_weight_pflg = 0
        self.lShell_weight_pfdg = 0

        # learning rate in the shell
        self.learning_rate_lshell = 0.001;


        ##################################################################
        # VTA
        ##################################################################

        # baseline activity of the VTA so that it's possible to inhibit
        # and activate it.
        self.VTA_baseline_activity = 0.10

        # actual baseline for LTD/LTP
        self.VTA_zero_val = VTA_baseline_activity/1.99


        ###################################################################
        # RMTg
        ###################################################################
        self.RMTg = 0


        ####################################################################
        # mPFC
        ####################################################################

        # filters smooth out any sharp step responses
        self.visual_direction_Green_mPFC_filter = Filter.SecondOrderFilter()
        self.visual_direction_Green_mPFC_filter.init_lowpass(0.01)
        self.visual_direction_Blue_mPFC_filter = Filter.SecondOrderFilter()
        self.visual_direction_Blue_mPFC_filter.init_lowpass(0.01)

        self.visual_direction_Green_trace = 0
        self.visual_direction_Blue_trace = 0
	
        self.mPFC_Green = 0
        self.mPFC_Blue = 0
	
        self.mPFC_receptor_5HT1 = 0
        self.mPFC_receptor_5HT2 = 0

        # counters which are triggered at random moment and generate a bias then
        self.mPFCspontGreen = 0
        self.mPFCspontBlue = 0

        self.exploreState = 0

        self.mPFC_spont_act_value = 0.2

        #########################################################
        # VTA
        self.VTA = 0

        #########################################################
        # Lateral Hypotyalamus (LH)
        self.LH = 0

        ###################################################################
        # dorsolateral ventral pallidum (dlVP)
        self.dlVP = 0

        #################################################################
    	# EP
        self.EP=0

        ####################################################################
	    # Lateral habenula (LHb)
        self.LHb = 0

        ######################################################################
        # Dorsal Raphe Nucleus (DRN)
        self.DRN = 0

        ######################################################################
	    # Oribtofrontal Cortex (OFC)
        self.OFC = 0
        self.OFCprev = 0
        self.OFCpersist = 0

        # learning rate for the OFC, just now from HC to OFC
        self.learning_rate_OFC = 0.01

	    # weights from the hippocampus place fields to the OFC
        self.pfLg2OFC = 0
        self.pfDg2OFC = 0

        # smoothes the signal when touching the object and
        # creates a curiosity reaction
        self.on_contact_direction_Green_filter = Filter.SecondOrderFilter()
        self.on_contact_direction_Green_filter.init_lowpass(0.1)
        self.on_contact_direction_Blue_filter = Filter.SecondOrderFilter()
        self.on_contact_direction_Blue_filter.init_lowpass(0.1)

	    # copies of the input signals
        self.reward = 0
        self.placefieldGreen = 0
        self.placefieldBlue = 0
        self.on_contact_direction_Green = 0
        self.on_contact_direction_Blue = 0
        self.visual_direction_Green = 0
        self.visual_direction_Blue = 0
        self.visual_reward_Green = 0
        self.visual_reward_Blue = 0

        # start logging
        self.flog = open("log.dat","w")

        
    def doStep(self, _reward,
            _placefieldGreen, _placefieldBlue,
            _on_contact_direction_Green, _on_contact_direction_Blue,
            _visual_direction_Green, _visual_direction_Blue,
            _visual_reward_Green, _visual_reward_Blue):
        self.reward = _reward
        self.placefieldGreen = _placefieldGreen
        self.placefieldBlue = _placefieldBlue
        self.on_contact_direction_Green = _on_contact_direction_Green
        self.on_contact_direction_Blue = _on_contact_direction_Blue
        self.visual_direction_Green = _visual_direction_Green
        self.visual_direction_Blue = _visual_direction_Blue
        self.visual_reward_Green = _visual_reward_Green
        self.visual_reward_Blue = _visual_reward_Blue

        # smooth out the visual stuff
        self.visual_direction_Green_trace = visual_direction_Green_mPFC_filter.filter(self.visual_direction_Green)
        self.visual_direction_Blue_trace = visual_direction_Blue_mPFC_filter.filter(self.visual_direction_Blue)

        if self.mPFCspontGreen > 0:
            self.mPFCspontGreen = self.mPFCspontGreen - 1
            self.mPFC_Green_spont_act = self.mPFC_spont_act_value
        else:
            self.mPFC_Green_spont_act = 0
            if random.random() < (1.0/1000.0):
                self.mPFCspontGreen = 500

        if self.mPFCspontBlue > 0:
            self.mPFCspontBlue = self.mPFCspontBlue - 1
            self.mPFC_Blue_spont_act = self.mPFC_spont_act_value
        else:
            self.mPFC_Blue_spont_act = 0
            if random.random() < (1.0/1000.0):
                self.mPFCspontBlue = 500

        # This is also generated in the mPFC and then fed down to the NAcc core with the command
        # to explore
        if self.exploreState == ExploreStates.EXPLORE_LEFT:
            mPFC2CoreExploreLeft = 0.1
            mPFC2CoreExploreRight = 0
    		if random.random() < 0.03:
	    		exploreState = random.choice(list(ExploreStates))
        elif self.exploreState == ExploreStates.EXPLORE_RIGHT:
            mPFC2CoreExploreLeft = 0
            mPFC2CoreExploreRight = 0.1
    		if random.random() < 0.03:
	    		exploreState = random.choice(list(ExploreStates))
        elif self.exploreState == ExploreStates.EXPLORE_STOP:
            mPFC2CoreExploreLeft = 0
            mPFC2CoreExploreRight = 0
            if random.random() < 0.03:
    			exploreState = random.choice(list(ExploreStates))
        else:
            mPFC2CoreExploreLeft = 0.1
            mPFC2CoreExploreRight = 0.1
            if random.random() <0.05:
                exploreState = random.choice(list(ExploreStates))

        if HT5DEBUG:
            mPFC_Green = visual_direction_Green_trace + visual_reward_Green + mPFC_Green_spont_act
            mPFC_Blue = visual_direction_Blue_trace + visual_reward_Blue + mPFC_Blue_spont_act
        else:
            mPFC_Green = ofc5HTreceptors(visual_direction_Green_trace + visual_reward_Green*2 + mPFC_Green_spont_act,1+DRN,2+DRN)
            mPFC_Blue = ofc5HTreceptors(visual_direction_Blue_trace + visual_reward_Blue*2 + mPFC_Blue_spont_act,1+DRN,2+DRN)

        # the activity in the LH is literally that of the reward
        LH = reward;

        # the VTA gets its activity from the LH and is ihibited by the RMTg
	    VTA = (LH + VTA_baseline_activity) / (1 + RMTg * shunting_inhibition_factor)

        ########################
        # OFC
        # place field -> Orbitofrontal Cortex weight.
        # The OFC remembers the reward value of a place.
        # So the higher the weight the higher the OFC activity
        # when the animal is inside that place field where there has been
        # reward experienced in the past.
        OFC = pfLg2OFC * placefieldGreen + pfDg2OFC * placefieldBlue
        if (((placefieldGreen-OFCprev) > 0.01) and (OFCpersist==0)):
            OFCpersist = 200

        OFCprev = placefieldGreen
        
        if LH > 0.5:
		    OFCpersist = 0

	    if OFCpersist>0:
            OFCpersist = OFCpersist -1

	    pfLg2OFC = weightChange(pfLg2OFC, learning_rate_OFC * DRN * placefieldGreen);
	    pfDg2OFC = weightChange(pfDg2OFC, learning_rate_OFC * DRN * placefieldBlue);


        # massive weight decay if there is no reward after a long period!
        # todo
        #        if ((OFCpersist>0) and (OFCpersist<100)):
        #		pfLg2OFC = pfLg2OFC * 0.999;

        # the dorsal raphe activity is driven by the OFC in a positive way
        DRN = (LH + OFC * 4) / (1+RMTg * shunting_inhibition_factor + DRN_SUPPRESSION) + DRN_OFFSET

        # lateral shell activity
        # the place field feeds into the Nacc shell for the time being.
        lShell = placefieldGreen * lShell_weight_pflg + placefieldBlue * lShell_weight_pfdg

        # Let's do heterosynaptic plasticity in the shell
        shell_DA = VTA
        
        # shell plasticity can experience a "dip" where then the weights
        # decrease. That's when it's below its baseline.

        shell_plasticity = shell_DA - VTA_zero_val

        lShell_weight_pflg = weightChange(lShell_weight_pflg, learning_rate_lshell * shell_plasticity * placefieldGreen)
        lShell_weight_pfdg = weightChange(lShell_weight_pfdg, learning_rate_lshell * shell_plasticity * placefieldBlue)

	    # the shell inhibits the dlVP
	    # dlVP = 1/(1+lShell * shunting_inhibition_factor)

        # another inhibition: the dlVP inhibits the EP
        EP = 1/(1+dlVP * shunting_inhibition_factor);

        # the EP excites the LHb
        LHb = EP + LHB_BIAS;

        # and the LHb excites the RMTg
        RMTg = LHb;

	    # core
	    # we have two core units
	    # if the Green is high then the rat approaches the Green marker
        CoreGreenOut= (mPFC_Green * core_weight_lg2lg)
	
        # if the Blue is high then the rat approaches the Blue marker
        CoreBlueOut= (mPFC_Blue * core_weight_dg2dg)

        float core_threshold = 0.25
        
        if (CoreGreenOut < core_threshold):
             CoreGreenOut = 0
	    if (CoreBlueOut < core_threshold):
            CoreBlueOut = 0;

	    # plasticity
        core_DA = VTA;
        core_plasticity = core_DA - VTA_zero_val;

        core_weight_lg2lg = weightChange(core_weight_lg2lg, learning_rate_core * core_plasticity * mPFC_Green)
        core_weight_dg2dg = weightChange(core_weight_dg2dg, learning_rate_core * core_plasticity * mPFC_Blue)

	    # we assume that the Core performs lateral inhibtion to shut down exploration
	    if ((CoreGreenOut > 0.05) and (CoreBlueOut > 0.05)):
            mPFC2CoreExploreLeft = 0
            mPFC2CoreExploreRight = 0

	# logging();

	self.step = self.step + 1
