# plot_seq.py

import shutil, sys, os, pandas as pd, re

""" magnetmatter modules """
from find_tools import findfolders_abspath, findfiles_abspath, findfile_abspath
from find_tools import findfolders, findfiles, findfile
import plot_predata
import subplots_seq_tools
import seqfile2seqcsv
import datfiles2datcsv
import extract_pcr
import seqcsv2sizecsv
import pdb; trace = pdb.set_trace




def plot_seq(workingdir = ""):
  """ workingdir is ./root of project.
  Searches all subfolders,
  creates plots and store in ./root/_mytest in separate experiment folders.

  this function executes:
    clean_output_folder
    plot_predata
    plot_refined_data
    plot_piecewise_refinements
    clean_after_plotting
  """

  class Notebook():
    """ reduce the need to pass several arguments to different functions """
    def __init__(self):
      self.lorsizelist = []
      # self.newlist = [] # seen used in plot_seq_tools for seqdf.
      self.phases = []
      self.wavelength = 0
      self.seqdf = pd.DataFrame
      self.sizedf = pd.DataFrame
      self.datdf = pd.DataFrame
      self.outpath = "folder where all graphs are created in subfolders"
      self.suboutpath = "path to subfolder in outpath"
      self.workingdir = "parent folder of all experiments"
      self.experiments = []
      self.exp_path = "current experiment"
      self.exp_name = "current experiment"
      self.ref_path = "current sequential refinement"
      self.ref_name = "plain name of the folder of sequential refinement"
      self.datdftype = "current types include dmc and dioptas"
      # self.plt_border_settings = "these are messed up when doing continues plotting combining contourf and plt.style.use"
      self.refinement_folders = []
      self.TwoByTwo = "subplotmanager for 2 x 2 subplot"
      self.TwoByOne = "subplotmanager for 1 x 2 subplots"
      self.TwoByTwoTruncated = "not really sure what this one does..."




  nb = Notebook()
  nb.workingdir = workingdir if workingdir != "" else os.getcwd()
  nb.outpath = os.path.join(nb.workingdir, "_mytest")

  """ important: setting working directory """
  os.chdir(nb.workingdir)

  """ cleaning up output folder """
  retval = clean_output_folder(nb)

  """ looping over all folders with presumed experimental data
  if such data is absent or something goes wrong,
  we skip the specific folder """
  exp_folders_to_skip = []
  for nb.exp_path in findfolders_abspath():
    nb.exp_name = os.path.basename(nb.exp_path)
    os.chdir(nb.exp_path)

    # if nb.exp_name == "FS_g18nm_P021_400oC_b":
    #   print("nb.exp_name =",nb.exp_name)
    #   import pdb; pdb.set_trace();
    """ ignore certain experiments. should be removed later """
    if os.path.basename(nb.exp_path) in [exp for exp in "400oC_a 400oC_c FS_g18nm_P021_500oC_a plt_styles archieve".split()]:
      print("    skipping current nb.exp_name = ", nb.exp_name)
      exp_folders_to_skip.append(-1)
      continue

    """ important: setting working folder """
    os.chdir(nb.exp_path)

    """ defining the folder where plots will be saved """
    nb.suboutpath = os.path.join(nb.workingdir, nb.outpath, os.path.basename(nb.exp_path))
    if not os.path.exists(nb.suboutpath):
      os.makedirs(nb.suboutpath)

    """ reading or generate datcsv """
    retval = read_predata(nb)
    if retval == -1:
      print("read_predata went wrong in nb.exp_name = ", nb.exp_name)
      exp_folders_to_skip.append(retval)
      continue

    """ trying to plot predata.
    We expect dioptas or DMC .dat files. """
    retval = plot_predata_handler(nb)
    """ something went wrong in plot_predata,
    we skip this experimental folder altogehter """
    exp_folders_to_skip.append(retval)
    """ note that plotting predata and refined data
    are separated. apparently the plt.style.use interfered
    with the formatting of all following created figures.
    therefore we have these two separate for-loops. """

  nb.TwoByTwo          = subplots_seq_tools.SubplotManager(nb, nrows=2,ncols=2)
  nb.TwoByOne          = subplots_seq_tools.SubplotManager(nb, nrows=2,ncols=1)
  nb.TwoByTwoTruncated = subplots_seq_tools.SubplotManager(nb, nrows=2,ncols=2)

  os.chdir(nb.workingdir)
  for nb.exp_path, stop in zip(findfolders_abspath(), exp_folders_to_skip):
    if stop:
      continue
    nb.exp_name = os.path.basename(nb.exp_path)
    """ important: setting working folder """
    os.chdir(nb.exp_path)
    """ defining the folder where plots will be saved """
    nb.suboutpath = os.path.join(nb.workingdir, nb.outpath, os.path.basename(nb.exp_path))
    if not os.path.exists(nb.suboutpath):
      os.makedirs(nb.suboutpath)

    """ reading or generate csv """
    retval = read_predata(nb)
    if retval == -1:
      print("read_predata went wrong. skipping this.")
      return -1

    """ parsing seq file to extract information and calculating the
    app. cryst. size to plot along with phase weight fractions """
    for nb.ref_path in findfolders_abspath():
      retval = read_refined_data(nb)
      # retval = plot_refined_data(nb)
    """ finding all folders (with a sequentially refined model)
    in current experimental folder """

    """ We try to combine all the piece-wise refinements """
    retval = prepare_piecewise_refinements(nb)
    retval = plot_piecewise_refinements(nb)

  """ checking if no plots have been generated. If not, output folder is deleted. """
  retval = clean_after_plotting(nb)
  return 0



def plot_piecewise_refinements(nb):

  """ plotting the concatenated _size and _PWF .csv found in refinement folders """
  # plot_seq_tools.plotphaseweightfractions(nb, title = nb.exp_name)
  # plot_seq_tools.size_plot(nb, title = nb.exp_name)

  """ (x,2) subplots for each xth experiments. """
  print(nb.TwoByTwo.flataxes)
  trace()
  mylength =len(nb.TwoByTwo.flataxes)
  nb.TwoByTwo.ax = nb.TwoByTwo.flataxes.pop(0)
  nb.TwoByTwo.title = "a test"+str(mylength);
  nb.TwoByTwo.hidelegend = False;  nb.TwoByTwo.xpositionLegend = None
  nb.TwoByTwo.plotphaseweightfractions()
  nb.TwoByTwo.ax = nb.TwoByTwo.flataxes.pop(0)
  nb.TwoByTwo.savefig = mylength <= 2
  print("nb.TwoByTwo.savefig =", nb.TwoByTwo.savefig)
  nb.TwoByTwo.title = "_nonaggr";
  nb.TwoByTwo.xpositionLegend = None;  nb.TwoByTwo.hidelegend = False
  nb.TwoByTwo.size_plot()

  """ all data plotted in (2,1) subplots """
  nb.TwoByOne.remove_xlabel_and_xticks = True;  nb.TwoByOne.ax = nb.TwoByOne.flataxes[0];
  nb.TwoByOne.title = "a test";  nb.TwoByOne.hidelegend = False;
  nb.TwoByOne.xpositionLegend = 0.5
  nb.TwoByOne.plotphaseweightfractions()

  nb.TwoByOne.savefig = nb.TwoByTwo.savefig

  nb.TwoByOne.remove_xlabel_and_xticks = False;  nb.TwoByOne.ax = nb.TwoByOne.flataxes[1]
  nb.TwoByOne.hidelegend = False;  nb.TwoByOne.xpositionLegend = 0.5;  nb.TwoByOne.title = "_aggr"
  nb.TwoByOne.size_plot()

  """ (2,2) subplot with reduced view """
  myxlim = (0,16)
  nb.TwoByTwoTruncated.remove_xlabel_and_xticks = True;  nb.TwoByTwoTruncated.ax = nb.TwoByTwoTruncated.flataxes[0]
  nb.TwoByTwoTruncated.title = "ThisTitleWillNotBeShown";  nb.TwoByTwoTruncated.hidelegend = True;  nb.TwoByTwoTruncated.xlim = None
  nb.TwoByTwoTruncated.plotphaseweightfractions()
  # nb.TwoByTwoTruncated._setting_up_legend( nb.TwoByTwoTruncated.flataxes[0], xposition = 1.1 )

  nb.TwoByTwoTruncated.ax = nb.TwoByTwoTruncated.flataxes[1];  nb.TwoByTwoTruncated.title = "ThisTitleWillNotBeShown"
  nb.TwoByTwoTruncated.hidelegend = False;  nb.TwoByTwoTruncated.xpositionLegend = -0.1;  nb.TwoByTwoTruncated.xlim = myxlim
  nb.TwoByTwoTruncated.plotphaseweightfractions()

  nb.TwoByTwoTruncated.remove_xlabel_and_xticks = False;  nb.TwoByTwoTruncated.ax = nb.TwoByTwoTruncated.flataxes[2]
  nb.TwoByTwoTruncated.title = "_aggr_trunc";  nb.TwoByTwoTruncated.hidelegend = True;  nb.TwoByTwoTruncated.xlim = None
  nb.TwoByTwoTruncated.size_plot()
  # nb.TwoByTwoTruncated.flataxes[1].legend()._visible = False

  nb.TwoByTwoTruncated.savefig = nb.TwoByTwo.savefig

  nb.TwoByTwoTruncated.ax = nb.TwoByTwoTruncated.flataxes[3];  nb.TwoByTwoTruncated.title = "_aggr_trunc"
  nb.TwoByTwoTruncated.hidelegend = False;  nb.TwoByTwoTruncated.xpositionLegend = -0.1;  nb.TwoByTwoTruncated.xlim = myxlim
  nb.TwoByTwoTruncated.size_plot()
  # nb.TwoByTwoTruncated.flataxes[3].legend()._visible = False


  return 0







def prepare_piecewise_refinements(nb):
  """ search for all _size and _PWF .csv in refinement folders
  to read in as pd.DataFrame and merge of possible.

  these df are stored in the notebook-object. """
  size_paths = []
  seq_paths = []
  phases = []
  for f in findfolders_abspath(nb.exp_path):
    if os.path.exists(os.path.join(f,"_size.csv")):
      size_paths += [ os.path.join(f,"_size.csv") ]
      seq_paths += [ os.path.join(f,"_seq.csv") ]
      pcr = sorted(findfiles_abspath(".pcr", path = f), key = lambda x : len(x) )[0]
      phases.append(extract_pcr.getphases(pcr))
  mysize = []
  myseq = []
  for csv in seq_paths:
    myseq.append( pd.read_csv(csv, index_col = "NEW_REFINEMENT") )
  for csv in size_paths:
    mysize.append( pd.read_csv(csv, index_col = "NEW_REFINEMENT") )

  # myseq = myseq
  # mysize = mysize
  unique_phase_nr2 = 999
  import itertools
  flat = list(itertools.chain.from_iterable(phases))
  flatdict = dict()
  for phase in set(flat):
    if phase in flatdict.keys():
      continue
    for num,phs in enumerate(phases):
      try:
        j = phs.index(phase) + 1
        # print("j =",j)
        # print("num =",num)
        # print("phases =",phs)
        # print("phase =",phase)
        # print("flatdict =",flatdict)
        # print("unique_phase_nr2 =",unique_phase_nr2)
      except ValueError:
        continue
      # print("mysize[num].columns =",mysize[num].columns)
      myseq[num].columns = [ re.sub("_ph"+str(j), "_ph"+str(unique_phase_nr2),x) for x in myseq[num].columns ]
      mysize[num].columns = [ re.sub("_ph"+str(j), "_ph"+str(unique_phase_nr2),x) for x in mysize[num].columns ]
      # print("mysize[num].columns =",mysize[num].columns)
      flatdict[phase] = unique_phase_nr2
    unique_phase_nr2 -= 1
  myseq = sorted(myseq, key = lambda x : min(x.index))
  mysize = sorted(mysize, key = lambda x : min(x.index))
  # for p in myseq: print(p.index)
  # for p in mysize: print(p.index)
  nb.seqdf = pd.concat(myseq)
  nb.sizedf = pd.concat(mysize)
  # print(flatdict)
  # for p in mysize: print(p.columns)
  keys = [k for k in flatdict.keys()]
  inv_map = {val: key for key, val in flatdict.items()}
  nb.phases = []
  for num,mykey in enumerate(sorted(inv_map.keys()), 1):
    phase = inv_map[mykey]
    nb.phases.append(phase)
    nb.seqdf.columns = (lambda mykey=mykey, nb = nb, num = num: [re.sub("_ph"+str(mykey), "_ph"+str(num),x) for x in nb.seqdf.columns])()
    nb.sizedf.columns = (lambda mykey=mykey, nb = nb, num = num: [re.sub("_ph"+str(mykey), "_ph"+str(num),x) for x in nb.sizedf.columns])()

  nb.lorsizelist = [col for col in nb.seqdf.columns if col.startswith("Y-cos") and not col.endswith("_err")]

  """ we use the extracted time stamps from the nb.datdf.columns
  for the concatenated dataframes. We blindly assume that the
  first dataframe is added manually to give the zero point of
  the experiment.
  This code is only useful for neutron data!

  extra code has to be written for synchrotron data. """
  # print("nb.seqdf.columns =",nb.seqdf.columns)
  # print("nb.sizedf.columns =",nb.sizedf.columns)

  if nb.datdftype == "dmc":
    """ we skip the first frame for neutron data.
    this will be changed in the future. the first frame will be indexed 1 and not 0
    in this way it can be included in the sequential refinement. """
    try:
      nb.seqdf.index = nb.datdf.columns[1:]
    except:
      print("len(nb.seqdf.index) =", len(nb.seqdf.index))
      print("len(nb.datdf.columns[1:]) =", len(nb.datdf.columns[1:]) )
      print("seq_paths[0] =\n", seq_paths[0])
      trace()
    nb.sizedf.index = nb.seqdf.index
  elif nb.datdftype == "dioptas":
    FirstFrame = int(nb.datdf.columns[0].strip("frame"))
    nb.seqdf.index = [(int(x.strip("frame"))-FirstFrame) * 5 / 60 for x in nb.datdf.columns]
    nb.sizedf.index = nb.seqdf.index

  nb.seqdf.index.name = "time [minutes]"
  nb.sizedf.index.name = nb.seqdf.index.name
  # nb.seqdf = sorted(myseq, key = lambda x : min(x.index))
  # nb.sizedf = sorted(mysize, key = lambda x : min(x.index))
  return 0




def clean_output_folder(nb):
  """ removing everything in the destination folder for graphs.
  This is maybe not necessary, but it does ensure that old/obsolete
  refinements are removed. """
  try:
    sys.stdout.write("... \"_mytest\" folder")
    shutil.rmtree(nb.outpath)
    sys.stdout.write(" - SUCCESFULLY REMOVED!\n")
    return 0
  except:
    sys.stdout.write(" - FAILURE!\n")
    return -1

def clean_after_plotting(nb):
  os.chdir(nb.outpath)
  for f in findfolders_abspath():
    if os.listdir(f) == []:
      os.rmdir(f)
      print("    removed " + str(os.path.basename(f)) + " from " + str(os.path.dirname(nb.outpath)) )
    # return # premature return to save time when debugging.
  return 0


def read_predata(nb):
  """ reading in or generating data frames """
  datcsv = [x for x in os.listdir() if x.endswith("_dats.csv")]
  if len(datcsv) > 1:
    print("found more _dats.csv, we skip workingdir =",nb.workingdir)
    return -1
  if len(datcsv) == 1:
    nb.datdf = pd.read_csv(datcsv[0])
    if "angle" in nb.datdf.columns:
      nb.datdf = nb.datdf.set_index("angle")
    try:
      """ when reading in dataframe, the columns are strings,
      we need them to be float64 """
      """ this is only needed for DMC data... can we homogenize the dataframes?
      EDIT: we want this inhomogenity now to decide what type datdf is :) """
      nb.datdf.columns = [float(x) for x in nb.datdf.columns]
      nb.datdftype = "dmc"
    except:
      nb.datdftype = "dioptas"
  else:
    datafolders = [x[0] for x in os.walk(nb.exp_path) if x[0].split("\\")[-1] == "tset"]
    if len(datafolders) == 0:
      return -1
    if len(datafolders) != 1:
      print("There are more than one subfolder named 'tset'. skipping ", nb.exp_path)
      return -1
    try:
      nb.datdf = datfiles2datcsv.generate_CSV_from_dmc_dat(workingdir = datafolders[0])
      nb.datdftype = "dmc"
    except Exception as dmc_error:
      try:
        nb.datdf = datfiles2datcsv.genereate_CSV_from_dioptas_dat(workingdir = datafolders[0])
        nb.datdftype = "dioptas"
      except Exception as dioptas_error:
        print("dmc_error =",dmc_error)
        print("dioptas_error =",dioptas_error)
        import pdb; pdb.set_trace();
        print("get creative.")
        return -1
  return 0

def plot_predata_handler(nb):
  """ missing introduction """
  print("--inside experiment folder:", os.path.basename(nb.exp_path))

  """ plotting data frames """
  """ these try except statements should be changed to if os.path.exsists'ish """
  if nb.datdftype == "dioptas":
    d1 = plot_predata.Dioptas(nb, minute_range = (0,24), printsize = "four_in_docx")
    retval1 = d1.run()
    print("found and plotted dioptas .dat/_dats_csv file(s)")
  elif nb.datdftype == "dmc":
    d2 = plot_predata.Dmc(nb, minute_range = (0,230), printsize = "four_in_docx")
    retval2 = d2.run()
    print("found and plotted dmc .dat/_dats_csv file(s)")
  else:
    print("found neither dioptas or DMC data to make heat map plots.")
    return -1
  """ no mistakes """
  return 0




def read_refined_data(nb):
  """  """
  print("    working on:", nb.ref_path)
  """ important: setting new working directory """
  os.chdir(nb.ref_path)
  """ defining object to store information passed between functions. """
  seq = findfile_abspath(".seq")
  """ find the pcr with shortest filename """
  pcr = findfiles(".pcr")
  if len(pcr) == 0: print("!-!-!-! skipping \"" + nb.exp_path + "\" + --> no .pcr was found"); return -1
  pcr.sort(key=lambda x: len(x))
  pcr = pcr[0]

  """ extracting list with phasenames """
  nb.phases = extract_pcr.getphases(pcr)

  """ extracting wavelength """
  nb.wavelength = extract_pcr.getwavelength(pcr)

  """ storing the folder name of the sequentially refined model """
  nb.ref_name = os.path.basename(os.getcwd())

  """ check if _seq.csv exists and if it has been changed later than its
  parent .pcr file. This saves some computing power and man-hour.
  """
  seqcsvpath = os.path.join(nb.ref_path, "_seq.csv")
  if os.path.exists(seqcsvpath) and os.stat(seqcsvpath).st_mtime > os.stat(pcr).st_mtime:
    """ st_mtime is the time in seconds since 1970ish telling
    when the content of file was last changed.
    with st_mtime we ask if the pcr was modified before the seqcsv file

    26. marts 2018: I, Pelle, was checking if this was actually executing as expecting. Both _size and _seq csv files
    were updated as intended! """
    nb.seqdf = pd.read_csv(seqcsvpath, index_col = "NEW_REFINEMENT")
  else:
    seqcsvpath = seqfile2seqcsv.seq2csv(seq)
  nb.seqdf = pd.read_csv(seqcsvpath, index_col = "NEW_REFINEMENT")

  """ finding the lorentizian size broadening parameters used for
  calculating the app. cryst. sizes """
  nb.lorsizelist = [col for col in nb.seqdf.columns if col.startswith("Y-cos") and not col.endswith("_err")]

  """ check if _size.csv exists and if it has been changed later than its
  parent .pcr file. This saves some computing power and man-hour.
  """
  sizecsvpath = os.path.join(nb.ref_path, "_size.csv")
  if os.path.exists(sizecsvpath) and os.stat(sizecsvpath).st_mtime > os.stat(pcr).st_mtime:
    """ st_mtime yields the number of seconds since 1970'ish """
    nb.sizedf = pd.read_csv(sizecsvpath, index_col = "NEW_REFINEMENT")
  else:
    nb.sizedf = seqcsv2sizecsv.calculate_size(nb)




def plot_refined_data(nb):
  """ plotting refined data """

  os.chdir(nb.ref_path)

  """ plotting the phase weight fractions """
  plot_seq_tools.plotphaseweightfractions(nb)

  """ plotting and saving the app. cryst. size informations. """
  plot_seq_tools.size_plot(nb)

  return 0






# END
