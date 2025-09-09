# Anopheles-OpenSpliceAI
Jupyter notebook for easy use of OpenSpliceAI model trained with A. gambiae Ifakara reference genome

This repository contains a Jupyter notebook (`11_access_openspliceAI.ipynb`) along with a Conda environment file (`environment.yml`) to reproduce the analysis, as well as the pretrained model required for the prediction of splice sites (`model_best.pt`)

---

## **1. Install Conda**

If you don’t already have Conda installed, follow these steps:

### **Miniconda (lightweight)**
1. Download Miniconda for your OS: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)  
2. Follow the installation instructions for your operating system.  
3. Open a terminal (Linux/Mac) or Anaconda Prompt (Windows) and check installation:

```bash
conda --version
```

## **2. Create the conda environment**
From the project directory, clone the repository, and navigate to the repository folder:

```bash
git clone https://github.com/pelusitoro/Anopheles-OpenSpliceAI.git
cd Anopheles-OpenSpliceAI
```

Create a conda environment with all the packages needed to run the notebook, included in the `.yml` file

```bash
conda env create -n openspliceai -f environment.yml
conda activate openspliceai
```

## **3. Launch Jupyter Notebook**

```bash
jupyter notebook
```
This will open a browser window.
Navigate to `11_access_openspliceAI.ipynb` and open it.
You can now run all cells in the notebook.
If you are familiar with it, using software like Visual Studio is much easier for the use of notebooks like this one.

## **4. Predict and plot splice sites**

Once inside the notebook, the only cell you need to change is the first one, to specify the input files and output directories.

```python
from Bio import SeqIO
import os

os.environ["WORKING_DIR"] = "/rds/general/user/prelucio/projects/tmstorage/live/openspliceAI/openspliceai" #Working directory
os.environ["MODEL_DIR"] = "/home/prelucio/Pablo/openspliceAI/model_best.pt" #PATH to model_best.pt

os.environ["INPUT_FILE"] = "/home/prelucio/Pablo/openspliceAI/QFS_lines/QFS5_REV.gbk" #gbk file with sequence to be analysed and annotations. Can be exported from benchling
os.environ["OUTPUT_DIR"] = "/home/prelucio/Pablo/openspliceAI/QFS_results/QFS5_REV" #Directory where output files will be saved
```

The notebook requires the gbk file of the sequence/construct to be analysed. Output:
- `bed` files with acceptor and donor site predictions
- Graph displaying scores for predicted splice sites
- Possible transcripts based on predicted splicing sites (only use this for input sequences which start from a transcription initiation site)

When preparing the `gbk` file (in Benchling), keep annotations very simple. Make sure to use the following annotation types: (exon, intron, gene, UTR, promoter, terminator). Using these will produce a much cleaner and neat graph. Bear in mind that the label that will be used is whatever you type in the Name cell.

```python
# Assign group
if feature.type in ["exon", "intron", "gene", 'UTR']:
  group = "gene_structure"
elif feature.type in ["promoter", "terminator"]:
  group = "regulatory"
```

If you need to add anything else, in the annotation type cell in Benchling type `misc_feature`. If you want to display these in the graph, set the `show_misc_features` variable to `True`, on top of the cell that generates the graph.

```python
from Bio import SeqIO
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.patches import Rectangle

# --- Settings ---
gbk_file = os.environ["INPUT_FILE"]
pred_output = f'{os.environ["OUTPUT_DIR"]}/predictions'
base_name = os.path.splitext(os.path.basename(gbk_file))[0].replace(" ", "_")
show_misc_features = False
rect_height = 0.2
track_spacing = 0.5
```

If you have any questions, let me know :)
