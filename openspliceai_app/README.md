# Anopheles OpenSpliceAI app draft

A small local Streamlit interface for the notebook workflow: upload a GenBank file, run the trained OpenSpliceAI model, inspect donor/acceptor scores over annotated features, and download the plot and BED files.

The pinned `requirements-openspliceai.txt` was assembled from the installed `openspliceai` Conda environment on macOS. It lists the Python packages needed for prediction and the app; use `environment.yml` for the complete Conda environment, including native libraries and Jupyter tools. Windows users should follow the WSL2 instructions below and use `requirements-windows-wsl.txt`.

## Install and run on macOS

These steps assume the lab member has the `Anopheles-OpenSpliceAI` repository, which includes `environment.yml` and `model_best.pt`. Keep the `openspliceai_app` folder inside that repository (for example, as `Anopheles-OpenSpliceAI/openspliceai_app`) so the app can find the model automatically.

1. Install Miniforge (recommended for Apple silicon and Intel Macs) or Miniconda, then open Terminal. If needed, install Git with Apple's command line tools by running `xcode-select --install`.
2. Clone the repository, or open Terminal and change into an existing checkout:

   ```bash
   git clone https://github.com/pelusitoro/Anopheles-OpenSpliceAI.git
   cd Anopheles-OpenSpliceAI
   ```

3. **One time:** create the prediction environment from the repository's environment file:

   ```bash
   conda env create -n openspliceai -f environment.yml
   conda activate openspliceai
   ```

   If the environment already exists, skip environment creation. Activate it with `conda activate openspliceai`.

4. **One time:** install the app dependencies. From the repository root, change to the app folder (adjust its name/path if needed) and install:

   ```bash
   cd openspliceai_app
   python -m pip install -r requirements-openspliceai.txt
   ```

5. **Each time you use the app:** open Terminal, activate the environment, change to the app folder, and launch it:

   ```bash
   conda activate openspliceai
   cd /path/to/Anopheles-OpenSpliceAI/openspliceai_app
   streamlit run app.py
   ```

   You do not need to reinstall anything or export the model path each time. The app looks for `model_best.pt` in the repository and nearby standard locations. If it is not found automatically, enter its full path in the sidebar; setting `OPENSPLICEAI_MODEL` is optional.

6. Streamlit will print a local URL, usually `http://localhost:8501`. Open it in a browser. Upload a GenBank `.gb` or `.gbk` file, choose the plot range and settings, then select **Run predictions**. When the run finishes, use the download buttons to save the PNG plot, zipped BED predictions, or an annotated GenBank file. The GenBank export preserves the input annotations and adds one-base donor/acceptor `misc_feature` entries at the plotted BED position, with their OpenSpliceAI score, strand, and prediction threshold. Only sites with scores strictly above the **Prediction threshold** are added; **Minimum score shown in plot** does not affect the export. Older OpenSpliceAI output may have reversed start/end coordinates for donors; the export handles these rows using the plotted start coordinate.

To stop the app, return to Terminal and press **Control-C**. The app runs on the Mac that launched it; uploaded files and intermediate predictions are stored temporarily and removed when the prediction run ends.

### macOS troubleshooting

- If Terminal says `conda: command not found`, finish the Miniforge/Miniconda shell initialization and open a new Terminal window.
- If the app says it cannot find `openspliceai`, activate the `openspliceai` environment in the same Terminal window before launching Streamlit.
- If it cannot find the model, enter the full path to the repository's `model_best.pt` in the sidebar. Keep the app folder inside the repository for automatic model discovery.
- If environment creation fails while installing PyTorch, first update Conda (`conda update -n base conda`) and retry. The packages specified in `environment.yml` are the intended versions for this model.

## Linux

The app requires Python dependencies from `requirements-openspliceai.txt`, the trained model file, and an environment where the `openspliceai` command is available. Set `OPENSPLICEAI_MODEL` in the shell if automatic model discovery does not find the file, or enter its path in the app sidebar.

## Run on Windows with WSL2

The simplest supported Windows setup is to run the app inside Ubuntu on WSL2. WSL2 is a small Linux environment that runs alongside Windows. OpenSpliceAI depends on `pysam`, which does not publish native Windows wheels, so install the app in WSL2 rather than Windows Python.

### First-time setup (one time only)

1. **Install WSL2 and Ubuntu 22.04.** Open the Start menu, type **PowerShell**, right-click **Windows PowerShell**, and choose **Run as administrator**. Copy and run:

   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

   Restart Windows if it asks. Then open **Ubuntu 22.04** from the Start menu. The first launch will ask you to create a Linux username and password. This is separate from your Windows login. When typing the password, the cursor will not move; type it and press Enter.

2. **Install the basic tools.** In the Ubuntu window, copy and run:

   ```bash
   sudo apt update
   sudo apt install -y python3.10 python3.10-venv python3-pip git
   ```

   Ubuntu will ask for the Linux password you just created. Type it and press Enter.

3. **Download the model repository.** Still in Ubuntu, run:

   ```bash
   cd ~
   git clone https://github.com/pelusitoro/Anopheles-OpenSpliceAI.git
   ```

   This repository includes the trained `model_best.pt` model. The app files (`app.py`, `requirements-windows-wsl.txt`, and `README.md`) should be placed in a folder named `openspliceai_app` inside the newly downloaded `Anopheles-OpenSpliceAI` folder. If you received these app files separately, copy the `openspliceai_app` folder into the repository using Windows File Explorer. To open the right folder in File Explorer, run these commands in Ubuntu:

   ```bash
   cd ~/Anopheles-OpenSpliceAI
   explorer.exe .
   ```

4. **Create the app's Python environment.** In Ubuntu, run:

   ```bash
   cd ~/Anopheles-OpenSpliceAI
   python3.10 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r openspliceai_app/requirements-windows-wsl.txt
   ```

   The install can take several minutes. These dependencies include PyTorch because it runs the trained model during prediction. OpenSpliceAI's command also loads modules for its other operations when it starts, so it needs some packages that prediction itself does not directly use. The file uses pinned package versions based on the lab's Mac environment; the Windows setup runs them under Linux in WSL2.

### Each time you use the app

1. Open **Ubuntu 22.04** from the Windows Start menu.
2. Copy and run these commands:

   ```bash
   cd ~/Anopheles-OpenSpliceAI
   source .venv/bin/activate
   streamlit run openspliceai_app/app.py
   ```

3. Ubuntu will show a local address, usually `http://localhost:8501`. Open that address in your normal Windows web browser. The app should find `model_best.pt` automatically because the app folder is inside the repository. If it does not, enter the model's path in the sidebar. In WSL, it will look similar to `/home/your-linux-username/Anopheles-OpenSpliceAI/model_best.pt`.
4. Upload a GenBank `.gb` or `.gbk` file, choose the plot settings, and click **Run predictions**. Use the download buttons to save the plot and BED files.

To close the app, go back to the Ubuntu window and press **Ctrl+C**. The environment installation is one time; each later use only needs the three launch commands above. Keep the repository and model in the Ubuntu home folder for better performance. The browser's upload and download buttons work from Windows as usual.

### If setup gets stuck

- If Windows says `wsl` is not recognized, install pending Windows updates and restart, then retry the WSL install command.
- If Ubuntu says `python3.10` is unavailable, check that you installed **Ubuntu 22.04**, not a different Ubuntu version.
- If a command reports that `openspliceai_app` or a file cannot be found, check that the app folder is inside `Anopheles-OpenSpliceAI` and is named exactly `openspliceai_app`.
- To reopen the app after closing the Ubuntu window, repeat the commands under **Each time you use the app**. Do not repeat the installation commands.

## Current draft behavior

- Accepts one GenBank record per upload (the notebook effectively plots one sequence).
- Converts it to FASTA and runs `openspliceai predict` with editable flanking size and prediction threshold.
- Shows donor and acceptor scores with a separate plot cutoff, optionally displaying other annotations.
- Displays recognized annotations in a pastel palette, packs overlapping features onto additional rows, and places labels above or below the feature blocks in non-overlapping lanes. Promoters are directional arrows, introns are lines, and the category legend is on the right.
- Supports full-sequence or coordinate-window plots and downloads the PNG, both BED files as a ZIP, and an annotated GenBank file. The GenBank file preserves input annotations and adds one-base donor/acceptor features at the plotted coordinate, with scores only above the prediction threshold.
- Runs locally; uploaded sequences and predictions are stored in a temporary directory and removed after the run.

The app depends on the model's `openspliceai` installation and its existing prediction output format. This first draft is intended for local lab use; it does not yet include multi-record plotting, saved run history, or deployment/authentication.

### OpenSpliceAI paper

Chao K-H, Mao A, Liu A, Pertea M, Salzberg SL. “OpenSpliceAI provides an efficient modular implementation of SpliceAI enabling easy retraining across nonhuman species.” *eLife* 14:RP107454 (2025). [https://doi.org/10.7554/eLife.107454.3](https://doi.org/10.7554/eLife.107454.3)
