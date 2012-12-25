__author__ = 'michael'
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from fsf_file import fsf_file
from exceptions import IOError
from fsf_file import BadFsfException
from utils import pre_to_csv,me_to_csv,get_feat_directory
import unittest


class test_preproc_bad_inputs(unittest.TestCase):
    def runTest(self):
        corrupt_path=os.path.join(os.path.dirname(__file__), "corrupt.fsf")
        self.assertRaises(BadFsfException,fsf_file,corrupt_path)
    def test_corrupt_path(self):
        bad_path=os.path.join(os.path.dirname(__file__), "this_is_a_bad_path.fsf")
        self.assertRaises(IOError,fsf_file,bad_path)

class TestPreproc(unittest.TestCase):
    def setUp(self):
        self.preproc = fsf_file(os.path.join(os.path.dirname(__file__),"pre.fsf"))
    def tearDown(self):
        self.preproc = None
    def test_width(self):
        pre_csv_lines,width,height=pre_to_csv(self.preproc)
        self.assertEqual(width,2)

class TestME(unittest.TestCase):
    def setUp(self):
        self.ME= fsf_file(os.path.join(os.path.dirname(__file__),"ME.fsf"))
        self.me_csv_lines,self.width,self.height=me_to_csv(self.ME)
    def tearDown(self):
        self.ME= None
    def test_width(self):
        self.assertEqual(self.width,2)

class TestGetFeatDirectory(unittest.TestCase):
    def test_no_feat(self):
        path='/Users/Something/SomethingElse'
        self.assertIsNone(get_feat_directory(path))
    def test_longer_filename(self):
        path='/Users/some/path/presumablyanalysisname.gfeat/fykfkyf'
        self.assertEqual(get_feat_directory(path),'/Users/some/path/presumablyanalysisname.gfeat/')
    def test_normal_file_name(self):
        path='/Users/some/path/presumablyanalysisname.gfeat/'
        self.assertEqual(get_feat_directory(path),'/Users/some/path/presumablyanalysisname.gfeat/')
    def test_no_slash(self):
        path='/Users/some/path/presumablyanalysisname.gfeat'
        self.assertEqual(get_feat_directory(path),'/Users/some/path/presumablyanalysisname.gfeat/')

class fsf_file_inputtype(unittest.TestCase):
    def setUp(self):
        self.directory=fsf_file(os.path.join(os.path.dirname(__file__),'FE.fsf'))
        self.copeimage=fsf_file(os.path.join(os.path.dirname(__file__),'FECopeImages.fsf'))
    def tearDown(self):
        self.directory=None
        self.copeimage=None
    def test_dir_version(self):
        self.assertEqual(self.directory.input_type,1)
    def test_c_image_version(self):
        self.assertEqual(self.copeimage.input_type,2)



if __name__ == '__main__':
    unittest.main()



