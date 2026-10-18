import unittest
from model import waiting_times, traversal

class ModelTests(unittest.TestCase):
    def test_uniform_enumeration_matches_mean(self):
        for n in range(2,65):
            r=waiting_times(n,1,8,.5,.5)
            actual=sum(min(d,n-d)*r['step'] for d in range(n))/n
            self.assertAlmostEqual(actual,r['ideal'])
    def test_mixture_endpoints(self):
        self.assertEqual(waiting_times(16,1,8,.5,0)['mixture'],37.5)
        self.assertEqual(waiting_times(16,1,8,.5,1)['mixture'],20)
    def test_traversal_wrap_tie_and_same_hub(self):
        self.assertEqual(traversal(16,0,15,'Ideal shorter direction'),[0,15])
        self.assertEqual(len(traversal(16,0,15,'Unidirectional')),16)
        self.assertEqual(traversal(4,0,2,'Ideal shorter direction'),[0,1,2])
        self.assertEqual(traversal(16,3,3,'Unidirectional'),[3])
    def test_zero_service_time(self):
        self.assertEqual(waiting_times(16,0,0,0,.5)['mixture'],0)
    def test_invalid_input(self):
        with self.assertRaises(ValueError): waiting_times(1,1,1,.5,.5)

if __name__=='__main__': unittest.main()
