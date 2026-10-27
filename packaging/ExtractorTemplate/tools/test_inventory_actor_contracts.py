import unittest
from inventory_actor_contracts import catalogue

class ActorContractTests(unittest.TestCase):
    def fixture(self):
        definitions=[dict(address=10,handler=0xb702,linked=20,field_22=100,secondary_definition=0,secondary_selector=0),
                     dict(address=20,handler=200,linked=0,field_22=101,secondary_definition=0,secondary_selector=0)]
        inv=dict(rom_sha256='fixture',object_definitions=definitions,routines=[],calls=[],object_field_references=[])
        spawns=dict(rom_sha256='fixture',markers=[dict(definition=10,layout_source=1),dict(definition=10,layout_source=1)])
        animations=dict(rom_sha256='fixture',cases=[])
        return inv,spawns,animations
    def test_callback_field_is_context_specific(self):
        result=catalogue(*self.fixture())
        self.assertEqual(result['definitions'][0]['forwarded_callback'],100)
        self.assertIsNone(result['definitions'][1]['forwarded_callback'])
        self.assertEqual(result['definitions'][0]['linked_definition'],20)
    def test_marker_records_not_distinct_encounter_count(self):
        result=catalogue(*self.fixture());row=result['definitions'][0]
        self.assertEqual(row['observed_definition_marker_records'],2)
        self.assertEqual(row['observed_layout_sources'],[1])
        self.assertFalse(result['all_actor_behaviors_ported'])
    def test_operand_duplicates_keep_each_access_once(self):
        inv,spawns,animations=self.fixture()
        inv['routines']=[dict(address=200,blocks=[300],status='unassessed',note='',possible_dependencies=[],observed_services=[])]
        instruction=dict(address=300,mnemonic='MOVE.W',operands='(+58,A5),(+60,A5)')
        inv['object_field_references']=[dict(instruction,offset=58),dict(instruction,offset=60)]
        report=catalogue(inv,spawns,animations)
        fields=next(row for row in report['handlers'] if row['address']==200)['field_access_candidates']
        self.assertEqual([(row['offset'],row['access'],row['width']) for row in fields],[(58,'read',2),(60,'write',2)])
        self.assertEqual(report['counts']['typed_field_access_candidates'],2)
    def test_mismatched_revisions_rejected(self):
        inv,spawns,animations=self.fixture();animations['rom_sha256']='other'
        with self.assertRaises(ValueError):catalogue(inv,spawns,animations)

if __name__=='__main__':unittest.main()
