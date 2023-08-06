# -*- coding: utf-8 -*-
import numpy

from .aggregate_spectroscopy import AggregateSpectroscopy
import quantarhei as qr

class AggregateExcitonAnalysis(AggregateSpectroscopy):
    """Class adding exciton analysis on molecular aggregates
    
    Most of the present methods are available after the aggregate is
    diagonalized by calling the ``diagonalize`` method.
    
    
    """
    
    
    def get_expansion_squares(self, state=0):
        """Returns the squares of expansion coefficients of an excitonic state
        
        """
        coefs = self.SS[:,state]
        sqrs  = self.SS[:,state]**2
        indx = [i for i in range(self.HH.shape[0])]
        return indx, coefs, sqrs
        
        
    def report_on_expansion(self, state=0, N=5):
        """Prints a short report on the composition of an exciton state
        
        """
        try:
            from terminaltables import AsciiTable
        except:
            raise Exception("Get terminaltables package "
                            +"for this functionality")
    
        indx, coefs, sqrs = self.get_expansion_squares(state)
    
        table_data = []
        table_data.append(["index","squares", "coefficients",
                           "state signatures"])
        for i in range(N):
            imax, sqr = _strip_max_coef(indx, sqrs)
            coef = coefs[imax]

            sta = self.get_state_signature_by_index(imax)
            table_data.append([imax, sqr, coef, sta])
            
            #print(imax, "\t", coef,"\t", sta)
            
        table = AsciiTable(table_data)
        print(table.table)


    def get_intersite_mixing(self, state1=0, state2=0):
        """Returns inter site mixing ration
        
        Inter site mixing ratio gives the probability that
        states ``state1`` and ``state2`` are localized
        on different pigments.
        
        """
        ci = self.SS[:,state1]
        cj = self.SS[:,state2]
        
        xi = 1.0
        
        # loop over all electronic states
        for n_el in range(self.Nel):
            # loop over all vibrational states in a given electronic state
            for n_nu in self.vibindices[n_el]:
                for n_mu in self.vibindices[n_el]:
                    x = (ci[n_nu]**2)*(cj[n_mu]**2)
                    xi -= x
                    
        return xi    


    def get_transition_dipole(self, state1=0, state2=0):
        """Returns transition dipole moment between two state. 
        
        If the second state is not specified, we get transition to the first
        state from the ground state.
        
        """
        if self._diagonalized:
            return self.D2[state1, state2]
        
        else:
            raise Exception("Aggregate has to be diagonalized")
            
            
    def get_state_energy(self, state=0):
        """Return the energy of a state with a given index
        
        """
        if self._diagonalized:
            return self.convert_energy_2_current_u(self.HD[state]) 
        else:
            raise Exception("Aggregate has to be diagonalized")


    def exciton_report(self, start=1, stop=None, Nrep=5, criterium=None):
        """Prints a report on excitonic properties of the aggregate
        
        Parameters
        ----------
        
        start : int (default = 1)
            First state to report on. Because 0 is often the ground state,
            it is skipped. For systems with molecular vibrations, first mixed
            states start with an index different from 1.
            
        stop : int (default = None)
            Where to stop the report. if Nono, all states are reported
            
        Nrep : int (default = 5)
            How many sites of the exciton decomposition we should list    
        
        """
        
        start_at = start
        stop_at = stop
        
        print("Report on excitonic properties")
        print("------------------------------\n")
        N01 = self.Nb[0]+self.Nb[1]
        for Nst in range(N01):
            
            if stop_at is None:
                stop_at = N01 + 1
                
            if (Nst >= start_at) and (Nst <= stop_at):
                
                tre = self.get_state_energy(Nst) - self.get_state_energy(0)
                dip = self.get_transition_dipole(0, Nst)
                
                if criterium is not None:
                    cond = criterium([tre, dip])
                    
                else:
                    cond = True
                
                if cond:
                    txt = "Exciton "+str(Nst)
                    Nlength = len(txt)
                    line = "="*Nlength
                    print(txt)
                    print(line)
                    print("")
                    with qr.energy_units("1/cm"):
                        print("Transition energy        : ", tre
                              , "1/cm")
                        print("Transition dipole moment : ", dip
                              , "D")
                    self.report_on_expansion(Nst, N=Nrep)
                    print("")


    #
    #  The following routine does not work with excitons, but rather with
    #  site basis representation 
    #

    # FIXME: move it somewhere else
    def get_state_signature_by_index(self, N):
        """Return aggregate vibronic state signature  by its index
        
        """
        return self.vibsigs[N]
            

def _strip_max_coef(indx, sqrs):
    """Returns the index of the maximum coefficient and the coefficient
    and sets the maximum value to zero.
    
    """
    imax = numpy.argmax(sqrs)
    sqr = sqrs[imax]
    
    # by setting the square to -1 we exclude it from ever becoming a max again
    sqrs[imax] = -1.0
    
    return imax, sqr
        