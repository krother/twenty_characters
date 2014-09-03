#!/usr/bin/env python

__author__ = "Cristian Hoof & Kristian Rother"
__copyright__ = "Copyright 2008, Cristian Hoof & Kristian Rother"
__credits__ = ["Kaethe Wenzel"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Kristian Rother"
__email__ = "krother@rubor.de"
__status__ = "Production"

from unittest import main, TestCase
from PIL import Image
from twenty_characters import *
import os

GOOD_FASTA_FILE = 'test_data/good_fasta_file.fasta'
BAD_FASTA_FILE = 'test_data/bad_fasta_file.fasta'


class TwentyCharacterTests(TestCase):
    
    def test_check_fasta(self):
        """Should return boolean"""
        result = check_fasta(read_fasta(GOOD_FASTA))
        self.assertTrue(result)
        result = check_fasta(read_fasta(BAD_FASTA))
        self.assertFalse(result)
        
    def test_read_fasta(self):
        result = read_fasta(GOOD_FASTA)
        right_sequences = [
            ('>seq_name1','DSLLRSSARSLLEFNTTMGCQPSDSQHRIQT'),
            ('>seq_name2','----------LLKMNYTGG----DTCHKVST'),
            ]
        self.assertEqual(result,right_sequences)
        
    def test_read_fasta_file(self):
        result = read_fasta_file(GOOD_FASTA_FILE)
        right_sequences = [
            ('>seq_name1','DSLLRSSARSLLEFNTTMGCQPSDSQHRIQT'),
            ('>seq_name2','----------LLKMNYTGG----DTCHKVST'),
            ]
        self.assertEqual(result,right_sequences)

    def test_assign_image_for_character(self):
        result_dict = assign_image_for_character(AA_PATH)
        right_image = Image.open(AA_PATH + 'A.png')
        self.assertEqual(list(result_dict['A'].getdata()), list(right_image.getdata())) 
        self.assertTrue(result_dict.has_key('Y'))
        self.assertTrue(result_dict.has_key('S'))        
        self.assertTrue(result_dict.has_key('-'))
    
    def test_resize_images(self):
        """AA dict should be resizeable.""" 
        aa_dict = assign_image_for_character(AA_PATH)
        result_dict = resize_images(aa_dict, (50,50))
        right_image = Image.open('test_data/A_50x50.png')
        self.assertEqual(result_dict['A'].size, right_image.size)
        self.assertEqual(list(result_dict['A'].getdata()), list(right_image.getdata()))

    def test_create_image_for_sequence(self):
        """Should create images for single sequences."""
        aa_dict = assign_image_for_character(AA_PATH)
        result_image = create_image_for_sequence(('>text', 'ASL'), aa_dict, hspacing=0)
        right_image = Image.open('test_data/asl_image.png')
        self.assertEqual(result_image.size[0], right_image.size[0])
        self.assertEqual(list(result_image.getdata()), list(right_image.getdata()))

    def test_create_image_for_sequence_hspacing(self):
        """Should create images for single sequences."""
        aa_dict = assign_image_for_character(AA_PATH)
        result_image = create_image_for_sequence(('>text', 'ASL'), aa_dict, hspacing=10)
        right_image = Image.open('test_data/asl_image.png')
        self.assertEqual(result_image.size[0], right_image.size[0]+20)
        self.assertEqual(result_image.size[1], right_image.size[1])

        
    def test_create_image_list(self):
        """Should create a list of images."""
        aa_dict = assign_image_for_character(AA_PATH)
        result = create_image_list([('name1','ASL'),('name2','ASLF')],aa_dict,hspacing=0)
        right_image = Image.open('test_data/asl_image.png')
        self.assertEqual(len(result),2)
        self.assertEqual(list(result[0].getdata()),list(right_image.getdata()))
        self.assertNotEqual(list(result[1].getdata()),list(right_image.getdata()))
    
    def test_join_image_list(self):
        right_image = Image.open('test_data/output.png')
        fasta = read_fasta(GOOD_FASTA)
        aa_dict = assign_image_for_character(AA_PATH)
        img_list = create_image_list(fasta, aa_dict,hspacing=10)
        result_image = join_image_list(img_list,vspacing=10)
        self.assertEqual(result_image.size[0], right_image.size[0])
        self.assertEqual(list(right_image.getdata()), list(result_image.getdata())) 
        
    def test_join_image_list_vspacing(self):
        right_image = Image.open('test_data/asl_image.png')
        right_data = list(right_image.getdata())
        fasta = read_fasta(GOOD_FASTA)
        aa_dict = assign_image_for_character(AA_PATH)
        img_list = create_image_list((('seq','ASL'),('seq','ASL')), aa_dict,hspacing=10)
        result_image = join_image_list(img_list,vspacing=10)
        result_data = list(result_image.getdata())
        result_slice = result_data[-len(right_data):]
        self.assertEqual(len(result_slice), len(right_data))
        
    def test_commandline(self):
        """test command line options"""
        if os.access("temp_output.png", os.F_OK):
            os.remove("temp_output.png")
        cmd = "python twenty_characters.py -i %s -a " % (GOOD_FASTA_FILE) + AA_PATH + " -o temp_output.png -x 10 -y 10" 
        os.system(cmd)
        right_image = Image.open('test_data/output.png')
        result_image = Image.open('temp_output.png')
        self.assertEqual(result_image.size, right_image.size)
        self.assertEqual(list(right_image.getdata()), list(result_image.getdata())) 
        os.remove('temp_output.png')
 
GOOD_FASTA = """>seq_name1
DSLLRSSARSLLEFNTTMGCQPSDSQHRIQT

>seq_name2
----------LLKMNYTGG----DTCHKVST
""".split('\n')

BAD_FASTA = """>sjfweilu0o34298ruo23
\r3jo2i3

""".split('\n')

if __name__== '__main__':
    main()
