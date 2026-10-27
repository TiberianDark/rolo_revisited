"""Focused static boundary/domain tests, never execute ROM instructions."""
import unittest
from pathlib import Path
from inventory_world_bunny_domain import catalogue,TARGETS

class WorldBunnyDomainTests(unittest.TestCase):
 def test_exact_slots_and_mutation_graph(self):
  report=catalogue(Path(__file__).resolve().parents[1])
  self.assertEqual([s['target'] for s in report['canonical_targets']],list(TARGETS))
  self.assertEqual([s['slot'] for s in report['canonical_targets']],list(range(0xe83a,0xe84c,2)))
  self.assertEqual([s['selector'] for s in report['canonical_targets']],list(range(9)))
  self.assertEqual([i['address'] for i in report['canonical_writers']],[0x291a,0xe7e4,0xe80a,0xe82a,0xe858])
  self.assertEqual([i['address'] for i in report['definition_references']],[0x9fcc])
  self.assertEqual(report['animation']['controls'],[dict(address=0x13070,command=0,parameter=0)])
  self.assertFalse(report['globally_resolved'])
 def test_rng_domain_for_every_seed(self):
  # Independent unsigned multiply/highword/modulo model of documented716E.
  directions=set();durations=set()
  for seed in range(65536):
   product=(seed or 3)*0x4e35;high=product>>16
   direction=1+high%8;duration=40+high%10
   self.assertTrue(1<=direction<=8);self.assertTrue(40<=duration<=49)
   directions.add(direction);durations.add(duration)
  self.assertEqual(directions,set(range(1,9)));self.assertEqual(durations,set(range(40,50)))

if __name__=='__main__':unittest.main()
