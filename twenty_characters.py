import re,  time
from PIL import Image
from optparse import OptionParser

## default values for mode, path and size of pictures and for the alphabet used

MODE = 'LA'
AA_CHARS = '-ACDEFGHIKLMNPQRSTVWXY' 
AA_PATH = 'aa_images/small/'
COLOR = (255,255) 
LINEPITCH = 10
COLUMNPITCH = 10

def check_fasta(fasta_seqs):
    """
    Checks whether the given FASTA string is syntactically correct.
    (does not violate the format). Returns Boolean.
        
    INPUT
      a list of (name,sequence) tuples.
    
    OUTPUT
      boolean
    """
    for name,seq in fasta_seqs:
        if not re.match(r">", name): 
            return False
        if not re.match(r"^[-ACDEFGHIKLMNPQRSTVWXY]+$", seq): 
            return False
    return True
    
    
def read_fasta(fasta_data):
    """
    Parses the given FASTA file into tuples of (name, sequence).
    
    INPUT
      fasta_data - FASTA line iterator.
    
    OUTPUT
      a list of (name,sequence) tuples.
    """
    fasta_seq_list = []
    comment_string = ""
    fasta_string = ""
    
    for line in fasta_data:
        if len(line)>=1 and line[0] == '>':
            fasta_seq_list.append((comment_string, fasta_string))
            comment_string = line.strip()
            fasta_string = ""
        else:
            fasta_string += line.strip()
    
    fasta_seq_list.append((comment_string, fasta_string))
    fasta_seq_list.pop(0)
    return fasta_seq_list

def read_fasta_file(path):
    """
    Parses the given FASTA file into tuples of (name, sequence).
    
    INPUT
      path - location of a FASTA file.
    
    OUTPUT
      a list of (name,sequence) tuples.
    """     
    fasta_seq_list = read_fasta(open(path))
    return fasta_seq_list


def create_image_list(fasta_seq_list, aa_dict, hspacing=COLUMNPITCH):
    """
    Creates image files for a set of sequences,
    
    INPUT
       seq_list - a list of (name,sequence) tuples.
       aa_dict - a dictionary with aa characters as keys,
                 and PIL.Image objects as values.
    OUTPUT
       a list of PIL.Image objects.
    """
    png_list = []
    for seq in fasta_seq_list:
        png_list.append(create_image_for_sequence(seq, aa_dict,hspacing)) 
    return png_list
    
def join_image_list(image_list, vspacing=LINEPITCH):
    """
    Joins a list of images vertically to a single image.
    INPUT
        image_list - a list of PIL.Image objects
        vspacing - vertical spacing between images.
    Output
        image - single PIL Objekt
    """        
    max_width = max([im.size[0] for im in image_list])
    max_height = max([im.size[1] for im in image_list])
    height = len(image_list) * max_height + vspacing * (len(image_list)-1)
    image = Image.new('LA', (max_width, height), COLOR)

    for i, im in enumerate(image_list):
        image.paste(im, (0, i * (max_height + vspacing)))
    return image


def assign_image_for_character(path):
    """
    INPUT
       path - a path containing images of aa characters.
    
    OUTPUT
        a dictionary with aa characters as keys,
            and PIL.Image objects as values.
    """
    aa_dict = {}        
    for character in AA_CHARS:
        try:        
            aa_dict[character] = Image.open('%s/%s.png' % (path, character), 'r')
        except IOError:
            aa_dict[character] = None 
               
    return aa_dict

def resize_images(aa_dict, size):
    """
    Changes the size of images.
    INPUT
        aa_dict - a dict containing images of aa characters.
        size - requested size in pixels as a tuple (width, height)
    OUTPUT
        a dictionary with aa characters as keys,
            and PIL.Image objects as values.
    """
    resized_aa_dict = {}
    for character in aa_dict:
        if aa_dict[character] != None:
            resized_aa_dict[character] = aa_dict[character].resize(size) 
    return resized_aa_dict

def check_aa_images(aa_dict):
    """ Checks if all letters from an aa_dictionary have same size and mode
         INPUT   aa_dict
         OUTPUT Bool
    """
    pass

def create_image_for_sequence(fasta_seq_list, aa_dict, hspacing=COLUMNPITCH):
    """
    Creates an image for a single sequence.
    
    INPUT
       fasta_seq_list - a single (name,sequence) tuple.
       aa_dict - a dictionary with aa characters as keys,
                 and PIL.Image objects as values.
       hspacing - horizontal spacing of characters
    
    OUTPUT
       fasta_seq_png - a PIL.Image object.
    """
    size = aa_dict['A'].size
    width = size[0] * len(fasta_seq_list[1]) + hspacing * (len(fasta_seq_list[1])-1)
    height = size[1]
     
    fasta_seq_png = Image.new(MODE, (width, height), COLOR)
       
    for i, aa_character in enumerate(fasta_seq_list[1]):
        fasta_seq_png.paste(aa_dict[aa_character], (i * (size[0] + hspacing), 0))
    return fasta_seq_png        


def twenty_characters(options):
    aa_dict = assign_image_for_character(options.aa_dir)
    if options.size:
        aa_dict=resize_images(aa_dict, options.size)
    fasta_seqs = read_fasta_file(options.fasta_file)
    hspacing, vspacing = COLUMNPITCH, LINEPITCH
    if options.hspacing:
        hspacing = int(options.hspacing)
    if options.vspacing:
        vspacing = int(options.vspacing)

    image_list = create_image_list(fasta_seqs, aa_dict, hspacing)
    image = join_image_list(image_list, vspacing) 
    image.save(options.png_file)
   

if __name__ == '__main__':
    parser = OptionParser(usage='''Twenty Characters
Converts FASTA alignments into images using arbitrary character sets.
(c) 2008 by Cristian Hoof and Kristian Rother
usage: python twenty_characters.py -i <.fasta> -a <aa png dir> -o <.png> [-x <horiz-spacing=0>] [-y <vert-spacing=10>]
''')

    parser.add_option ("-i", "--input", dest="fasta_file", help="name of FASTA file with sequences")
    parser.add_option ("-o", "--output", dest="png_file", help="name of PNG image file to be created")
    parser.add_option ("-a", "--aa_dir", dest="aa_dir", help="name with png files for each aa character")
    parser.add_option ("-x", "--hspacing", dest="hspacing", help="horizontal spacing between characters")
    parser.add_option ("-y", "--vspacing", dest="vspacing", help="vertical spacing between characters")
    parser.add_option ("-s", "--size", dest="size", help="resizes images")

    options, args = parser.parse_args()

    if not options.fasta_file:
            parser.error("Error: input file argument missing")
    if not options.png_file:
            parser.error("Error: output file argument missing")
    if not options.aa_dir:
            parser.error("Error: character directory argument missing")

    twenty_characters(options)
    
