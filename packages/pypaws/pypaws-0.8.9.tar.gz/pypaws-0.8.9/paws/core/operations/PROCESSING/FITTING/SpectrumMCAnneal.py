from collections import OrderedDict

import numpy as np

from ...Operation import Operation
from xrsdkit.fitting.xrsd_fitter import XRSDFitter 

inputs = OrderedDict(
    q_I=None,
    populations=None,
    fixed_params=None,
    step_size=0.01,
    nsteps_burn=1000,
    nsteps_anneal=1000,
    nsteps_quench=1000,
    T_anneal=0.2,
    T_burn=0.3)
outputs = OrderedDict(
    best_params=None,
    final_params=None,
    report=None)

class SpectrumMCAnneal(Operation):
    """Anneal XRSD parameters by Metropolis-Hastings Monte Carlo.

    This Operation explores the space 
    of parameters for a XRSD pattern,
    seeking a globally optimal fit for some measured data.
    It is useful for refining optimizations 
    that tend to get stuck in local minima.
    """

    def __init__(self):
        super(SpectrumMCAnneal, self).__init__(inputs, outputs)
        self.input_doc['q_I'] = 'n-by-2 array of measured data: '\
            'intensity (arb) with respect to scattering vector (1/Angstrom)'
        self.input_doc['populations'] = 'dict defining scatterer populations, xrsdkit format'
        self.input_doc['fixed_params'] = 'dict (subset of `params`) '\
            'indicating which `params` should be fixed during anneal'
        self.input_doc['step_size'] = 'random walk fractional step size'
        self.input_doc['nsteps_burn'] = 'number of iterations '\
            'to perform in the initial burn-off phase' 
        self.input_doc['nsteps_anneal'] = 'number of iterations '\
            'to perform in the annealing phase' 
        self.input_doc['nsteps_quench'] = 'number of iterations '\
            'to perform in the quenching (zero acceptance) phase' 
        self.output_doc['best_params'] = 'dict of scattering parameters '\
            'yielding the best fit over all trials'
        self.output_doc['final_params'] = 'dict of scattering parameters '\
            'obtained in the final step of the algorithm'
        self.output_doc['report'] = 'dict reporting '\
            'the number of steps and reject ratio'

    def run(self):
        q_I = self.inputs['q_I']
        pops = self.inputs['populations']
        par_fix = self.inputs['fixed_params']
        stepsz = self.inputs['step_size']
        ns_burn = self.inputs['nsteps_burn']
        ns_anneal = self.inputs['nsteps_anneal']
        ns_quench = self.inputs['nsteps_quench']
        T_burn = self.inputs['T_burn']
        T_anneal = self.inputs['T_anneal']

        p_init = pops
        p_best = pops
        p_fin = pops
        rpt = OrderedDict()
        xf = XRSDFitter(q_I,all_pops)
        # TODO: refactor this for new xrsdkit API

        # the burn phase is for escaping local minima.
        p_best,p_fin,rpt_burn = xf.MC_anneal_fit(stepsz,ns_burn,T_burn,par_fix)
        p_best_burn = p_best
        obj_init = rpt_burn['objective_init']
        obj_best = rpt_burn['objective_best']

        if self.message_callback:
            self.message_callback('finished burn. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_burn['objective_init'],
                rpt_burn['objective_best'],
                rpt_burn['objective_final'],
                rpt_burn['reject_ratio']))

        # the anneal phase is expected to gravitate to regions of parameter space
        # where the fit objective is low.
        p_best,p_fin,rpt_anneal = xf.MC_anneal_fit(stepsz,ns_anneal,T_anneal,par_fix)
        if rpt_anneal['objective_best'] < obj_best:
            obj_best = rpt_anneal['objective_best']
        else:
            # if no better params were found during the anneal phase,
            # fall back on the best params from the burn phase
            p_best = p_best_burn
        if self.message_callback:
            self.message_callback('finished anneal. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_anneal['objective_init'],
                rpt_anneal['objective_best'],
                rpt_anneal['objective_final'],
                rpt_anneal['reject_ratio']))

        # the quench phase is expected to stochastically descend, 
        # such that the objective never increases from one step to the next,
        # effectively sinking deeper into the current local minimum.
        p_best,p_fin,rpt_quench = xf.MC_anneal_fit(stepsz,ns_quench,0.,par_fix)
        if self.message_callback:
            self.message_callback('finished quench. \ninit: {} \nbest: {} \nfinal: {} \nRR: {}'
            .format(rpt_quench['objective_init'],
                rpt_quench['objective_best'],
                rpt_quench['objective_final'],
                rpt_quench['reject_ratio']))
        rpt = OrderedDict(
            objective_init = obj_init,
            objective_best = obj_best,
            objective_final = rpt_quench['objective_final'],
            reject_ratio = rpt_anneal['reject_ratio'])
        self.outputs['best_pops'] = p_best 
        self.outputs['final_pops'] = p_fin 
        self.outputs['report'] = rpt 

