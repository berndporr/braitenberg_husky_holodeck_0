import Filter

class Limbic_system:
    
    def __init__(self):
        # simulation step counter
        step = 0

        # shunting inhibition is implemented as:
        # neuronal_activity / ( 1 + inhibition * shunting_inhibition_factor )
        shunting_inhibition_factor = 200

        ##############################################################
        # NAcc core
        ##############################################################
	
        # I see the light green object and I approach the light
        # green one
        core_weight_lg2lg = 0.2

        # I see the dark green object and I approach the dark green one
        core_weight_dg2dg = 0.2

        # motor activities
        CoreGreenOut = 0
        CoreBlueOut = 0
        mPFC2CoreExploreLeft = 0
        mPFC2CoreExploreRight = 0

        # learning rate of the core
        learning_rate_core = 0.075

        # dopamine activity
        core_DA = 0

        # is positive if DA is elevated and neg if there's a DA dip
        core_plasticity = 0

        # counter after which the rat starts exploring
        coreExploreCtr = 0;


        #################################################################
        # NAcc l-shell
        #################################################################

        # l-shell activity
        lShell = 0

        # dopamine activity
        shell_DA = 0

        # is positive if DA is elevated and neg if there's a DA dip
        shell_plasticity = 0

        # weights for the shell system
        lShell_weight_pflg = 0
        lShell_weight_pfdg = 0

        # learning rate in the shell
        learning_rate_lshell = 0.001;


        ##################################################################
        # VTA
        ##################################################################

        # baseline activity of the VTA so that it's possible to inhibit
        # and activate it.
        VTA_baseline_activity = 0.10

        # actual baseline for LTD/LTP
        VTA_zero_val = VTA_baseline_activity/1.99


        ###################################################################
        # RMTg
        ###################################################################
        RMTg = 0



        ####################################################################
        # mPFC
        ####################################################################

        # filters smooth out any sharp step responses
        visual_direction_Green_mPFC_filter = Filter.SecondOrderFilter()
        visual_direction_Blue_mPFC_filter = Filter.SecondOrderFilter()

        visual_direction_Green_trace = 0
        visual_direction_Blue_trace = 0
	
        mPFC_Green = 0
        mPFC_Blue = 0
	
        mPFC_receptor_5HT1 = 0
        mPFC_receptor_5HT2 = 0

        # counters which are triggered at random moment and generate a bias then
        mPFCspontGreen = 0
        mPFCspontBlue = 0

        #########################################################
        # VTA
        VTA = 0

        #########################################################
        # Lateral Hypotyalamus (LH)
        LH = 0

        ###################################################################
        # dorsolateral ventral pallidum (dlVP)
        dlVP = 0

        #################################################################
    	# EP
        EP=0

        ####################################################################
	    # Lateral habenula (LHb)
        LHb = 0

        ######################################################################
        # Dorsal Raphe Nucleus (DRN)
        DRN = 0

        ######################################################################
	    # Oribtofrontal Cortex (OFC)
        OFC = 0
        OFCprev = 0
        OFCpersist = 0

        # learning rate for the OFC, just now from HC to OFC
        learning_rate_OFC = 0.01

	    # weights from the hippocampus place fields to the OFC
        pfLg2OFC = 0
        pfDg2OFC = 0


    # smoothes the signal when touching the object and
    # creates a curiosity reaction
    on_contact_direction_Green_filter = Filter.SecondOrderFilter()
    on_contact_direction_Blue_filter = Filter.SecondOrderFilter()

	# copies of the input signals
    reward = 0
    placefieldGreen = 0
    placefieldBlue = 0
    on_contact_direction_Green = 0
    on_contact_direction_Blue = 0
    visual_direction_Green = 0
    visual_direction_Blue = 0
    visual_reward_Green = 0
    visual_reward_Blue = 0

    flog = False
