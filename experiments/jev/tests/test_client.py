import copy
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('jev_client',Path(__file__).resolve().parents[1]/'run.py')
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)

class ClientTests(unittest.TestCase):
    def test_valid_probability_distribution(self):
        payload={'model':'jev-1.13.0','questions':{'service_match':{'criteria':{'S001':'Service','INSUFFICIENT_INFORMATION':'Ambiguous'}}}}
        response={'model':'jev-1.13.0','answers':{'service_match':{'type':'choice','choice':'S001','probabilities':{'S001':0.8,'INSUFFICIENT_INFORMATION':0.2},'confidence':0.6}},'usage':{'input_tokens':10,'output_tokens':4}}
        client.validate(response,payload)
        rounded=copy.deepcopy(response)
        rounded["answers"]["service_match"]["probabilities"]={"S001":0.79,"INSUFFICIENT_INFORMATION":0.2}
        client.validate(rounded,payload)
        for change in ('missing_option','nan','wrong_winner','wrong_model','bad_mass'):
            bad=copy.deepcopy(response);a=bad['answers']['service_match']
            if change=='missing_option':del a['probabilities']['INSUFFICIENT_INFORMATION']
            elif change=='nan':a['confidence']=float('nan')
            elif change=='wrong_winner':a['choice']='INSUFFICIENT_INFORMATION'
            elif change=='wrong_model':bad['model']='unexpected'
            elif change=='bad_mass':a['probabilities']['S001']=0.1
            with self.assertRaises(ValueError):client.validate(bad,payload)

if __name__=='__main__':unittest.main()
