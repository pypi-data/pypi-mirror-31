from __future__ import print_function
import abc
import re
from collections import OrderedDict
import copy

from .. import pawstools

class Operation(object):
    """Class template for implementing paws operations"""

    def __init__(self,inputs,outputs):
        self.inputs = OrderedDict(copy.deepcopy(inputs))
        self.outputs = OrderedDict(copy.deepcopy(outputs))
        self.input_locator = OrderedDict.fromkeys(self.inputs.keys())
        self.outputs = OrderedDict.fromkeys(self.outputs.keys()) 
        self.input_doc = OrderedDict.fromkeys(self.inputs.keys()) 

        # input types determine how inputs are handled 
        # when workflows using the operation are executed or serialized
        #self.input_type = OrderedDict.fromkeys(self.inputs.keys()) 

        # input datatypes are used for typecasting,
        # for when values are set indirectly,
        # e.g. through a gui.
        # if an input is not likely to be set via gui,
        # e.g. if it is a complicated or duck-typed object, 
        # this should be left to None,
        # in which case gui applications should have some default behavior.
        self.input_datatype = OrderedDict.fromkeys(self.inputs.keys())

        self.output_doc = OrderedDict.fromkeys(self.outputs.keys()) 
        for name in self.inputs.keys(): 
        #    self.input_type[name] = basic_type 
            self.input_locator[name] = pawstools.InputLocator(pawstools.basic_type,self.inputs[name])
        self.message_callback = self.tagged_print 
        self.data_callback = None 
        self.stop_flag = False

    def __getitem__(self,key):
        if key == 'inputs':
            return self.inputs
        elif key == 'outputs':
            return self.outputs
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def __setitem__(self,key,data):
        if key == 'inputs':
            self.inputs = data
        elif key == 'outputs':
            self.outputs = data
        else:
            raise KeyError('[{}] Operation only recognizes keys {}'
            .format(__name__,self.keys()))
    def keys(self):
        return ['inputs','outputs']

    def tagged_print(self,msg):
        print('[{}] {}'.format(type(self).__name__,msg))

    #def load_defaults(self):
    #    """
    #    Set default types and values into the Operation.input_locators.
    #    """
    #    for name in self.inputs.keys():
    #        tp = self.input_type[name]
    #        val = self.inputs[name]
    #        self.input_locator[name] = InputLocator(tp,val)

    def run(self):
        """
        Operation.run() should use the Operation.inputs
        and set values for all of the items in Operation.outputs.
        """
        pass

    def stop(self):
        self.stop_flag = True
        for inp_name,il in self.input_locator.items():
            if il.tp == entire_workflow:
                if self.inputs[inp_name]:
                    self.inputs[inp_name].stop()

    def get_outputs(self):
        return self.outputs

    @classmethod
    def clone(cls):
        return cls()

    def build_clone(self):
        """Clone the Operation"""
        new_op = self.clone()
        for nm,il in self.input_locator.items():
            new_il = pawstools.InputLocator()
            new_il.tp = copy.copy(il.tp)
            new_il.val = copy.copy(il.val)
            #if il.tp == entire_workflow:
            #    if self.inputs[nm]:
            #        wf = self.inputs[nm]
            #        new_wf = wf.build_clone()
            #        new_wf.data_callback = wf.data_callback
            #        new_wf.message_callback = wf.message_callback
            #        new_op.inputs[nm] = new_wf
            #elif il.tp == plugin_item:
            #    # plugin items should not be copied:
            #    # they are expected to operate safely in the main thread
            #    new_op.inputs[nm] = self.inputs[nm]
            #else: 
            #    # NOTE: have to implement __deepcopy__
            #    # for whatever the input is.
            #    new_op.inputs[nm] = copy.deepcopy(self.inputs[nm]) 
            new_op.input_locator[nm] = new_il
        #new_op.message_callback = self.message_callback
        #new_op.data_callback = self.data_callback
        return new_op

    def setup_dict(self):
        """Produce a dictionary fully describing the setup of the Operation.

        Returns
        -------
        dct : dict
            Dictionary specifying the module name and input setup 
            for the current state of the Operation
        """
        op_modulename = self.__module__[self.__module__.find('operations'):]
        op_modulename = op_modulename[op_modulename.find('.')+1:]
        dct = OrderedDict() 
        dct['op_module'] = op_modulename
        inp_dct = OrderedDict() 
        for nm,il in self.input_locator.items():
            inp_dct[nm] = {'tp':copy.copy(il.tp),'val':copy.copy(il.val)}
        dct['inputs'] = inp_dct 
        return dct

    def set_input(self,input_name,val):
        self.inputs[input_name] = val    

    def clear_outputs(self):
        for k,v in self.outputs.items():
            self.outputs[k] = None

    def description(self):
        """Provide a string describing the Operation.
        """
        return str(type(self).__name__+": "
        + self.doc_as_string()
        + "\n\n--- Inputs ---"
        + self.input_description() 
        + "\n\n--- Outputs ---"
        + self.output_description())

    def doc_as_string(self):
        if self.__doc__:
            return re.sub("\s\s+"," ",self.__doc__.replace('\n','')) 
        else:
            return "none"

    def input_description(self):
        a = ""
        for name in self.inputs.keys(): 
            if self.input_locator[name]:
                display_val = self.input_locator[name]
            else:
                display_val = self.inputs[name] 
            a = a + '\n\n'+self.parameter_doc(name,display_val,self.input_doc[name])
        return a

    def output_description(self):
        a = ""
        for name,val in self.outputs.items(): 
            a = a + '\n\n'+self.parameter_doc(name,val,self.output_doc[name])
        return a
    
    @staticmethod
    def parameter_doc(name,value,doc):
        if isinstance(value, pawstools.InputLocator):
            tp_str = pawstools.input_types[value.tp]
            v_str = str(value.val)
            return "- name: {} \n- value: {} ({}) \n- doc: {}".format(name,v_str,tp_str,doc) 
        else:
            v_str = str(value)
            return "- name: {} \n- value: {} \n- doc: {}".format(name,v_str,doc) 
                
