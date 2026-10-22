# Run Anopheles OpenSpliceAI with Docker Desktop

This version uses a prebuilt app image published to Docker Hub (and GitHub Container Registry). Lab members do not need to install Git, Python, Conda, or build the Docker image. Docker Desktop runs OpenSpliceAI inside the container; you interact with it in your web browser.

## One-time publishing setup for the repository maintainer

These steps are only needed once by the person maintaining the lab repository. Lab members can skip this section.

1. In Docker Hub, create a **Public** repository named `anopheles-openspliceai-app` under the `pelusitoro` account. The image name will be `pelusitoro/anopheles-openspliceai-app`.
2. In Docker Hub account settings, create a personal access token with read/write permissions. Copy it somewhere safe; do not put it in the repository or send it in chat.
3. On GitHub, open the `Anopheles-OpenSpliceAI` repository and go to **Settings → Secrets and variables → Actions**. Select **New repository secret** and add:
   - `DOCKERHUB_USERNAME` with the Docker Hub username `pelusitoro`.
   - `DOCKERHUB_TOKEN` with the access token from Docker Hub.
4. Push the publishing workflow in `.github/workflows/publish-docker-image.yml` to the `main` branch. GitHub Actions will build and push both `linux/amd64` and `linux/arm64` images to Docker Hub and GHCR. The build includes the repository's `AgamI_model_best.pt`; a change to that file automatically triggers a new image build.

GitHub Actions requires these secrets to publish the image. They are used only by the publishing workflow; the token is not included in the image.

## What you need

- Docker Desktop for Mac or Windows.
- An internet connection for the first image download.

The trained `AgamI_model_best.pt` model is included inside the app image. You do not need to download or mount the model separately.

## 1. Install and open Docker Desktop

### Mac

1. Open the official [Docker Desktop for Mac installation guide](https://docs.docker.com/desktop/setup/install/mac-install/) and download the version for your Mac (Apple silicon or Intel).
2. Open the installer and follow its prompts to move Docker Desktop into Applications.
3. Open Docker Desktop from Applications, accept the agreement, and wait until it reports that Docker is running.

### Windows

1. Open the official [Docker Desktop for Windows installation guide](https://docs.docker.com/desktop/setup/install/windows-install/) and download Docker Desktop.
2. Run the installer and follow its prompts. If asked, enable the WSL 2 backend. Restart Windows if requested.
3. Open Docker Desktop from the Start menu, accept the agreement, and wait until it reports that Docker is running.

If Docker Desktop or WSL is blocked by your institution's computer settings, ask your IT administrator to install or enable it.

## 2. Download the app image in Docker Desktop

1. In Docker Desktop, open **Images**.
2. Select **Search images to run** (or use the search bar at the top of Docker Desktop).
3. Search for:

   ```text
   ghcr.io/pelusitoro/anopheles-openspliceai-app:latest
   ```

4. Select `pelusitoro/anopheles-openspliceai-app` and choose **Pull**. Wait for the download to finish. This only needs to be done once, unless the lab publishes an updated version.

## 3. Start the app

1. In Docker Desktop's **Images** view, find `pelusitoro/anopheles-openspliceai-app` and select **Run**.
2. Expand **Optional settings** and enter the following values (wording can vary slightly by Docker Desktop version):

   | Setting | Value |
   | --- | --- |
   | Container name | `openspliceai-lab-app` |
   | Host port | `8501` |
   | Container port | `8501` |

   No model path, environment variable, or volume mount is needed for the included trained model. If you later want to use a different model, mount that file to the container and set `OPENSPLICEAI_MODEL` to its container path.

3. Select **Run**. Docker Desktop starts the container and shows its logs.
4. Open [http://localhost:8501](http://localhost:8501) in your web browser. Use the **GenBank** tab to upload a `.gb`/`.gbk` file and download the plot, BED files, or annotated GenBank file. Use **FASTA or paste** to upload `.fa`/`.fasta`/`.fna`/`.fas` (multiple records are supported) or paste a DNA sequence; that workflow returns donor and acceptor BED files separately or in a ZIP, without plotting. For context, aim for about 10,000 bases of flanking sequence total (roughly 5,000 on each side of the region you care about). Shorter sequences still run, but predictions near sequence ends have less real context because the model pads with N bases. This is a recommendation, not a minimum input size. It follows the flank sizes examined in the [OpenSpliceAI paper](https://doi.org/10.7554/eLife.107454.3) and the context used by the [original SpliceAI paper](https://doi.org/10.1016/j.cell.2018.12.015). The annotated GenBank file preserves input annotations and adds one-base donor/acceptor features at the plotted BED position, with scores strictly above the prediction threshold; the plot score cutoff does not affect the export. Donors are forward-strand blue features, and acceptors are reverse-strand yellow features. Older OpenSpliceAI output may have reversed donor start/end coordinates; the app handles those using the plotted start coordinate.

Docker's official [Images view guide](https://docs.docker.com/desktop/use-desktop/images/) explains how to pull and run an image and configure its port.

## Next time

1. Open Docker Desktop.
2. In **Containers**, find `openspliceai-lab-app` and select **Start** if it is stopped.
3. Open [http://localhost:8501](http://localhost:8501) in your browser.

To stop the app, select **Stop** for `openspliceai-lab-app` in the **Containers** view. The app image remains on your computer. You do not need to download it again each time. Docker's [Containers view guide](https://docs.docker.com/desktop/use-desktop/container/) describes the controls.

## 4. Predict and plot from a GenBank file
In the Docker app, open the GenBank: plot and annotations tab and upload a GenBank file (.gb, .gbk, or .gbff). Choose whether to plot the full sequence or a coordinate range, adjust the prediction settings if needed, and click Run predictions.
When the run finishes, the app displays splice-site predictions over the sequence annotations. You can download the plot as a PNG, the donor and acceptor predictions as BED files in a ZIP, or an annotated GenBank file.
The plot displays these annotation categories when they are present in the GenBank file:
- promoter — a directional arrow based on the feature’s strand
- terminator
- 5′UTR and 3′UTR
- CDS
- exon
- intron — shown as a line
- other — optional category for anything else you want to visualise that does not belong in any other category; turn on Show other annotations in the prediction settings

Each category has its own color. Features that overlap are arranged on additional rows, and labels are placed above or below the feature shapes.
Annotations that do not match one of these categories are not plotted.
**Categories are simply to facilitate making the plots and do not affect the outcome of the prediction.**

## Predict from a FASTA file or pasted sequence
In the Docker app, open FASTA or paste: BED files. Choose Upload FASTA to provide a .fa, .fasta, .fna, or .fas file, or choose Paste sequence to enter DNA directly. You can paste either a plain sequence or FASTA-formatted text. Multiple FASTA records are supported. Adjust the prediction settings if needed, then click Run predictions and get BED files.
There is no strict minimum sequence length. For a region of interest, aim to include about 10,000 bases of flanking sequence total—roughly 5,000 on each side—when possible. Shorter sequences still run, but predictions near sequence ends have less real context.
Understanding the outputs

**For FASTA or pasted-sequence predictions, the app provides:**
- A donor BED file with predicted donor splice sites.
- An acceptor BED file with predicted acceptor splice sites.
- A ZIP file containing both BED files.
The BED files contain genomic-style coordinates relative to each input sequence, along with the prediction score. You can use them in genome browsers or other compatible tools to view the predicted sites. The app does not create a plot in this workflow.

**For GenBank predictions**, the app also displays a plot and offers a PNG, BED files in a ZIP, and an annotated GenBank file. In the GenBank annotation export, donor sites are forward-strand blue features and acceptor sites are reverse-strand yellow features. Only sites with scores above the prediction threshold are added.

## Troubleshooting

- **Docker cannot find the model:** make sure you have pulled the latest `pelusitoro/anopheles-openspliceai-app` image, which includes `AgamI_model_best.pt`.
- **Port 8501 is busy:** use host port `8502` while leaving container port `8501`, then open `http://localhost:8502`.
- **The app page does not load:** confirm the container is running in Docker Desktop, wait a minute for startup, and reload the page.
- **The image cannot be found:** check the image name above and ensure Docker Desktop has internet access. If the package is private, the lab maintainer must make it public or grant you access.

The app runs predictions on CPU in this draft, so long sequences may take a while. Uploaded GenBank records and intermediate prediction files are temporary and removed after a prediction run.

## OpenSpliceAI paper

Chao K-H, Mao A, Liu A, Pertea M, Salzberg SL. “OpenSpliceAI provides an efficient modular implementation of SpliceAI enabling easy retraining across nonhuman species.” *eLife* 14:RP107454 (2025). [https://doi.org/10.7554/eLife.107454.3](https://doi.org/10.7554/eLife.107454.3)
