# Run Anopheles OpenSpliceAI with Docker Desktop

This version uses a prebuilt app image published to Docker Hub (and GitHub Container Registry). Lab members do not need to install Git, Python, Conda, or build the Docker image. Docker Desktop runs OpenSpliceAI inside the container; you interact with it in your web browser.

## One-time publishing setup for the repository maintainer

These steps are only needed once by the person maintaining the lab repository. Lab members can skip this section.

1. In Docker Hub, create a **Public** repository named `anopheles-openspliceai-app` under the `pelusitoro` account. The image name will be `pelusitoro/anopheles-openspliceai-app`.
2. In Docker Hub account settings, create a personal access token with read/write permissions. Copy it somewhere safe; do not put it in the repository or send it in chat.
3. On GitHub, open the `Anopheles-OpenSpliceAI` repository and go to **Settings → Secrets and variables → Actions**. Select **New repository secret** and add:
   - `DOCKERHUB_USERNAME` with the Docker Hub username `pelusitoro`.
   - `DOCKERHUB_TOKEN` with the access token from Docker Hub.
4. Push the publishing workflow in `.github/workflows/publish-docker-image.yml` to the `main` branch. GitHub Actions will build and push both `linux/amd64` and `linux/arm64` images to Docker Hub and GHCR.

GitHub Actions requires these secrets to publish the image. They are used only by the publishing workflow; the token is not included in the image.

## What you need

- Docker Desktop for Mac or Windows.
- The lab repository ZIP, which includes the trained `model_best.pt` file. If your lab distributes the model separately, use that copy instead.
- An internet connection for the first image download.

## 1. Download the model file

1. Open the lab repository page: <https://github.com/pelusitoro/Anopheles-OpenSpliceAI>.
2. Select **Code → Download ZIP**.
3. When the download completes, open the ZIP in Finder (Mac) or File Explorer (Windows) to extract it.
4. Locate `model_best.pt` inside the extracted `Anopheles-OpenSpliceAI` folder. Keep this folder somewhere easy to find. You will choose the model file in Docker Desktop in a later step.

You do not need GitHub Desktop to download the ZIP. If you prefer cloning and updating the repository with a graphical app, you can install [GitHub Desktop](https://desktop.github.com/download/); command-line Git is not required.

## 2. Install and open Docker Desktop

### Mac

1. Open the official [Docker Desktop for Mac installation guide](https://docs.docker.com/desktop/setup/install/mac-install/) and download the version for your Mac (Apple silicon or Intel).
2. Open the installer and follow its prompts to move Docker Desktop into Applications.
3. Open Docker Desktop from Applications, accept the agreement, and wait until it reports that Docker is running.

### Windows

1. Open the official [Docker Desktop for Windows installation guide](https://docs.docker.com/desktop/setup/install/windows-install/) and download Docker Desktop.
2. Run the installer and follow its prompts. If asked, enable the WSL 2 backend. Restart Windows if requested.
3. Open Docker Desktop from the Start menu, accept the agreement, and wait until it reports that Docker is running.

If Docker Desktop or WSL is blocked by your institution's computer settings, ask your IT administrator to install or enable it.

## 3. Download the app image in Docker Desktop

1. In Docker Desktop, open **Images**.
2. Select **Search images to run** (or use the search bar at the top of Docker Desktop).
3. Search for:

   ```text
   ghcr.io/pelusitoro/anopheles-openspliceai-app:latest
   ```

4. Select `pelusitoro/anopheles-openspliceai-app` and choose **Pull**. Wait for the download to finish. This only needs to be done once, unless the lab publishes an updated version.

## 4. Start the app and connect the model

1. In Docker Desktop's **Images** view, find `pelusitoro/anopheles-openspliceai-app` and select **Run**.
2. Expand **Optional settings** and enter the following values (wording can vary slightly by Docker Desktop version):

   | Setting | Value |
   | --- | --- |
   | Container name | `openspliceai-lab-app` |
   | Host port | `8501` |
   | Container port | `8501` |
   | Environment variable name | `OPENSPLICEAI_MODEL` |
   | Environment variable value | `/models/model_best.pt` |
   | Host path in volume/bind mount | The full path to your `model_best.pt` file |
   | Container path in volume/bind mount | `/models/model_best.pt` |

   Select the `model_best.pt` file itself as the host path, not just its parent folder. Examples:

   - Mac: `/Users/yourname/Downloads/Anopheles-OpenSpliceAI/model_best.pt`
   - Windows: `C:\Users\YourName\Downloads\Anopheles-OpenSpliceAI\model_best.pt`

   Mark the model mount read-only if Docker Desktop provides that option.

3. Select **Run**. Docker Desktop starts the container and shows its logs.
4. Open [http://localhost:8501](http://localhost:8501) in your web browser. Upload a GenBank `.gb` or `.gbk` file, adjust the prediction and plot settings, and click **Run predictions**. Download the plot, BED files, or annotated GenBank file from the app when the run finishes. The annotated GenBank file preserves input annotations and adds one-base donor/acceptor features at the plotted BED position, with scores strictly above the prediction threshold; the plot score cutoff does not affect the export. Donors are forward-strand blue features, and acceptors are reverse-strand yellow features. Older OpenSpliceAI output may have reversed donor start/end coordinates; the app handles those using the plotted start coordinate.

Docker's official [Images view guide](https://docs.docker.com/desktop/use-desktop/images/) explains how to pull and run an image and configure port, volume, and environment settings.

## OpenSpliceAI paper

Chao K-H, Mao A, Liu A, Pertea M, Salzberg SL. “OpenSpliceAI provides an efficient modular implementation of SpliceAI enabling easy retraining across nonhuman species.” *eLife* 14:RP107454 (2025). [https://doi.org/10.7554/eLife.107454.3](https://doi.org/10.7554/eLife.107454.3)

## Next time

1. Open Docker Desktop.
2. In **Containers**, find `openspliceai-lab-app` and select **Start** if it is stopped.
3. Open [http://localhost:8501](http://localhost:8501) in your browser.

To stop the app, select **Stop** for `openspliceai-lab-app` in the **Containers** view. The app image remains on your computer. You do not need to download it again each time. Docker's [Containers view guide](https://docs.docker.com/desktop/use-desktop/container/) describes the controls.

## Troubleshooting

- **Docker cannot find the model:** make sure the volume maps the actual host file `model_best.pt` to `/models/model_best.pt` in the container, and that the environment variable is set to `/models/model_best.pt`.
- **Port 8501 is busy:** use host port `8502` while leaving container port `8501`, then open `http://localhost:8502`.
- **The app page does not load:** confirm the container is running in Docker Desktop, wait a minute for startup, and reload the page.
- **The image cannot be found:** check the image name above and ensure Docker Desktop has internet access. If the package is private, the lab maintainer must make it public or grant you access.

The app runs predictions on CPU in this draft, so long sequences may take a while. Uploaded GenBank records and intermediate prediction files are temporary and removed after a prediction run.
