import unittest
from inventory_worklist import candidate_paths,catalogue

class CandidatePathTests(unittest.TestCase):
    def test_scoped_contract_is_kept_in_unassessed_task(self):
        link=dict(path='contract.json',scope='Alias consumers pending')
        routine=dict(address=1,possible_dependencies=[],status='unassessed',evidence=['fixture'],contract_links=[link])
        inv=dict(rom_sha256='fixture',routines=[routine],unresolved=[])
        result=catalogue(inv,dict(normal_frame=dict(entry=1),states=[]))
        task=result['tasks'][0]
        self.assertEqual(task['contract_links'],[link])
        self.assertIn('Alias consumers pending',task['next'])
        self.assertEqual(result['counts']['unassessed_entry_candidates'],1)

    def test_cycle_and_shortest_candidate_path(self):
        routines=[dict(address=1,possible_dependencies=[2,3]),dict(address=2,possible_dependencies=[1,4]),
                  dict(address=3,possible_dependencies=[4]),dict(address=4,possible_dependencies=[])]
        paths=candidate_paths(routines,[1]);self.assertEqual(paths[4],[1,2,4]);self.assertEqual(len(paths),4)
    def test_unknown_target_preserved_without_fabricated_successors(self):
        self.assertEqual(candidate_paths([dict(address=1,possible_dependencies=[9])],[1]),{1:[1],9:[1,9]})
    def test_duplicate_stop_site_gets_one_task(self):
        stop=dict(address=9,reason='outside ROM',assessment='relocated code')
        inv=dict(rom_sha256='fixture',routines=[],unresolved=[stop,dict(stop)])
        states=dict(normal_frame=dict(entry=1),states=[])
        result=catalogue(inv,states);self.assertEqual(result['counts']['tasks'],1)

if __name__=='__main__':unittest.main()
