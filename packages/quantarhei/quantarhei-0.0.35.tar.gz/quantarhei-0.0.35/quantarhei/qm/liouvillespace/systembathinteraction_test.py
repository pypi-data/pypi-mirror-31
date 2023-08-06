# -*- coding: utf-8 -*-

from .systembathinteraction import SystemBathInteraction


class TestSystemBathInteraction(SystemBathInteraction):
    
    def __init__(self, name=None):
        
        if name is None:
            raise Exception("Name of the test must be specified")
            
            
        from ...builders.aggregate_test import TestAggregate
        from ...qm.hilbertspace.operators import ProjectionOperator
        
        if name == "dimer-2-env":
            # we get SBI from here
            agg = TestAggregate(name=name)
            agg.build()
    
            super().__init__()
            
            # copy it into the newly created object
            self.__dict__ = agg.sbi.__dict__.copy()
        

        elif name == "dimer-2-lind":
            agg = TestAggregate(name="dimer-2")
            agg.build()
            
            N = agg.get_Hamiltonian().dim
            
            P1 = ProjectionOperator(1, 2, dim=N)
            P2 = ProjectionOperator(2, 1, dim=N)
            
            sys_ops = [P1, P2]
            rates = [1.0/100.0, 1.0/200]
            
            super().__init__(sys_operators=sys_ops, rates=rates)
            
            
        

        
            
        