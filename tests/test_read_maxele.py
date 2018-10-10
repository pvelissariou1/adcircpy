#! /usr/bin/env python
import unittest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from AdcircPyTests import AdcircPyEnvironment
from AdcircPy import AdcircPy

class testReadMaxeleAscii(AdcircPyEnvironment, unittest.TestCase):
  def setUp(self):
    self.read_environment_variables()

  def test_read_maxele_ascii(self):
    maxele = AdcircPy.read_output(self._os.getenv("MAXELE_ASCII_PATH"),
                                  fort14=self._os.getenv("FORT14_PATH"))
    maxele.make_plot()
    plt.close(plt.gcf())

  def test_read_maxele_ascii_no_fort14(self):
    with self.assertRaises(Exception) as context:
      AdcircPy.read_output(self._os.getenv("MAXELE_ASCII_PATH"))
    self.assertTrue('a fort.14 is required' in str(context.exception))

class testReadMaxeleNetCDF(AdcircPyEnvironment, unittest.TestCase):
  def setUp(self):
    self.read_environment_variables()

  def test_read_maxele_ascii(self):
    maxele = AdcircPy.read_output(self._os.getenv("MAXELE_NC_PATH"))
    maxele.make_plot()
    plt.close(plt.gcf())

  def test_read_netcdf_maxele_no_fort14(self):
    """
    NOTE: This function is returning True
    but in reality the fort.14 file is being ignored.
    Need to collect boundary data from fort.14 before returning object.
    """
    AdcircPy.read_output(self._os.getenv("MAXELE_NC_PATH"),
                         fort14=self._os.getenv("FORT14_PATH"))

if __name__ == '__main__':
  unittest.main()
