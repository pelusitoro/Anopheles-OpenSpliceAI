"""Streamlit front end for the Anopheles OpenSpliceAI model."""

from __future__ import annotations

import csv
import copy
import io
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from Bio.SeqFeature import FeatureLocation, SeqFeature

import matplotlib.pyplot as plt
import streamlit as st
from Bio import SeqIO
from matplotlib.patches import FancyArrow, Patch, Rectangle
from matplotlib.lines import Line2D


st.set_page_config(page_title="Anopheles SpliceAI", page_icon="🧬", layout="wide")
st.title("Anopheles OpenSpliceAI")
st.write("Upload a GenBank file, choose prediction and plot settings, and download the plot, BED predictions, or an annotated GenBank file.")

def find_default_model() -> str:
    configured = os.environ.get("OPENSPLICEAI_MODEL")
    candidates = [Path(configured).expanduser()] if configured else []
    candidates.extend([Path.cwd() / "model_best.pt", Path(__file__).resolve().parent / "model_best.pt"])
    for parent in Path(__file__).resolve().parents:
        candidates.extend([parent / "model_best.pt", parent / "Anopheles-OpenSpliceAI" / "model_best.pt"])
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return configured or "model_best.pt"


default_model = find_default_model()
with st.sidebar:
    st.header("Prediction settings")
    model_path = st.text_input("Model file (.pt)", value=default_model)
    flanking_size = st.number_input("Flanking size", min_value=0, max_value=100000, value=10000, step=1000)
    threshold = st.number_input("Prediction threshold", min_value=0.0, max_value=1.0, value=0.0001, format="%.5f")
    score_cutoff = st.slider("Minimum score shown in plot", 0.0, 1.0, 0.01, 0.01)
    show_misc = st.checkbox("Show other annotations", value=False)
    st.caption("The model and openspliceai command must be installed on the computer running this app.")

uploaded = st.file_uploader("GenBank file", type=["gb", "gbk", "gbff"])
region_col, _ = st.columns([1, 2])
with region_col:
    region_mode = st.radio("Plot range", ["Full sequence", "Choose coordinates"], horizontal=True)


def read_bed(path: Path):
    results = []
    with path.open() as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) < 5:
                continue
            try:
                results.append((int(float(row[1])), float(row[4])))
            except (ValueError, IndexError):
                continue
    return results


def add_splice_features(record, bed_path: Path, site_type: str, threshold: float) -> int:
    """Append BED sites above the prediction threshold as GenBank misc_features."""
    added = 0
    with bed_path.open() as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if len(row) < 6:
                continue
            try:
                start, end = int(row[1]), int(row[2])
                score = float(row[4])
            except (ValueError, IndexError):
                continue
            if score <= threshold or start < 0 or end <= start or end > len(record.seq):
                continue
            strand = {"+": 1, "-": -1}.get(row[5])
            record.features.append(SeqFeature(
                FeatureLocation(start, end, strand=strand),
                type="misc_feature",
                qualifiers={
                    "label": [f"SpliceAI {site_type} (score {score:.6g})"],
                    "note": [f"Predicted {site_type} splice site; OpenSpliceAI score={score:.6g}; prediction threshold={threshold:.6g}"],
                    "source": ["OpenSpliceAI"],
                },
            ))
            added += 1
    return added


def genbank_bytes(record) -> bytes:
    output = io.StringIO()
    SeqIO.write(record, output, "genbank")
    return output.getvalue().encode("utf-8")


ANNOTATION_COLORS = {
    "promoter": "#A6A6A6",       # gray
    "terminator": "#FDBF6F",     # pastel orange
    "5'UTR": "#B2DF8A",          # pastel green
    "3'UTR": "#CAB2D6",          # pastel purple
    "CDS": "#FB9A99",            # pastel red
    "exon": "#C6DBEF",           # pale sky blue
    "intron": "#777777",         # neutral gray line
    "other": "#FFFFB3",          # pastel yellow
}


def annotation_category(feature) -> str | None:
    """Map GenBank feature types to the requested display categories."""
    if "translation" in feature.qualifiers:
        return None
    kind = feature.type.lower().replace("_", " ").strip()
    if kind in {"promoter", "terminator", "cds", "exon", "intron"}:
        return {"cds": "CDS", "exon": "exon", "intron": "intron"}.get(kind, kind)
    if kind in {"5'utr", "5 utr", "5utr", "five_prime_utr", "five prime utr"}:
        return "5'UTR"
    if kind in {"3'utr", "3 utr", "3utr", "three_prime_utr", "three prime utr"}:
        return "3'UTR"
    if kind in {"other", "miscellaneous"}:
        return "other"
    return None


def make_plot(record, donor, acceptor, start, end, cutoff, show_other):
    fig, (features_ax, score_ax) = plt.subplots(
        2, 1, figsize=(15, 7), sharex=True, gridspec_kw={"height_ratios": [1.35, 3]}
    )
    visible_features = []
    for feature in record.features:
        category = annotation_category(feature)
        if category is None or (category == "other" and not show_other):
            continue
        left, right = int(feature.location.start), int(feature.location.end)
        if right < start or left > end:
            continue
        left, right = max(left, start), min(right, end)
        label = next(iter(feature.qualifiers.get("gene", feature.qualifiers.get("label", [feature.type]))), feature.type)
        visible_features.append((left, right, category, label, feature.location.strand))

    # Greedily pack each feature into the first row whose previous feature ends
    # before this one starts. GenBank features are sorted by start coordinate.
    visible_features.sort(key=lambda item: (item[0], item[1]))
    rows = []
    placed = []
    for left, right, category, label, strand in visible_features:
        row_index = next((i for i, row_end in enumerate(rows) if row_end <= left), len(rows))
        if row_index == len(rows):
            rows.append(right)
        else:
            rows[row_index] = right
        placed.append((left, right, category, label, row_index, strand))

    row_height = 0.68
    block_height = 0.32
    label_lanes = []
    label_gap = max((end - start) * 0.025, 20)
    for left, right, category, label, row_index, strand in placed:
        color = ANNOTATION_COLORS[category]
        y = row_index * row_height
        if category == "promoter":
            direction = 1 if strand != -1 else -1
            feature_length = max(right - left, 1)
            head_length = min(max(feature_length * 0.22, 1), feature_length * 0.45)
            features_ax.add_patch(FancyArrow(
                left if direction > 0 else right, y + block_height / 2,
                feature_length * direction, 0,
                width=block_height * 0.55, head_width=block_height,
                head_length=head_length,
                length_includes_head=True, facecolor=color, edgecolor="#333333", linewidth=0.45,
            ))
        elif category == "intron":
            features_ax.hlines(y + block_height / 2, left, right, color=color, linewidth=3.0)
        else:
            features_ax.add_patch(Rectangle((left, y), max(right-left, 1), block_height, facecolor=color, edgecolor="#333333", linewidth=0.45))
        if category != "intron":
            center = (left + right) / 2
            text_width = min(max(len(label) * label_gap * 0.22, label_gap), max(end - start, label_gap))
            label_left, label_right = center - text_width / 2, center + text_width / 2
            # Assign labels to the first non-overlapping lane and alternate the
            # lanes above and below each feature row.
            lane = next((i for i, lane_end in enumerate(label_lanes) if lane_end <= label_left), len(label_lanes))
            if lane == len(label_lanes):
                label_lanes.append(label_right + label_gap)
            else:
                label_lanes[lane] = label_right + label_gap
            offset = lane // 2 + 1
            label_y = y + block_height + 0.035 + (offset - 1) * 0.16 if lane % 2 == 0 else y - 0.035 - (offset - 1) * 0.16
            features_ax.text(center, label_y, label, ha="center",
                             va="bottom" if lane % 2 == 0 else "top", fontsize=7, clip_on=True)
    label_extra = max(0, (len(label_lanes) + 1) // 2) * 0.16 + 0.12
    features_ax.set_ylim(-label_extra, max(0.65, len(rows) * row_height) + label_extra)
    features_ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        features_ax.spines[side].set_visible(False)
    features_ax.tick_params(axis="x", bottom=False, labelbottom=False)
    category_handles = [
        Line2D([0], [0], color=ANNOTATION_COLORS[name], linewidth=1.6, label=name)
        if name == "intron" else Patch(facecolor=ANNOTATION_COLORS[name], edgecolor="#333333", label=name)
        for name in ANNOTATION_COLORS
    ]
    if category_handles:
        features_ax.legend(handles=category_handles, title="GenBank annotations", loc="upper left",
                           bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=8, title_fontsize=9)
    for values, color, label in ((donor, "#2563eb", "Donor"), (acceptor, "#f28e2b", "Acceptor")):
        values = [(x, score) for x, score in values if start <= x <= end and score > cutoff]
        if values:
            xs, ys = zip(*values)
            score_ax.vlines(xs, 0, ys, color=color, alpha=0.75, label=label)
        else:
            score_ax.plot([], [], color=color, label=label)
    score_ax.set_xlim(start, end)
    score_ax.set_ylim(0, 1.05)
    score_ax.set_ylabel("SpliceAI score")
    score_ax.set_xlabel("GenBank sequence position (0-based)")
    score_ax.grid(True, linestyle="--", alpha=0.25)
    score_ax.legend(loc="upper right")
    fig.suptitle(f"{record.id} — splice site scores")
    fig.tight_layout(rect=(0, 0, 0.82, 1))
    return fig


if uploaded:
    try:
        raw = uploaded.getvalue()
        record = SeqIO.read(io.StringIO(raw.decode("utf-8")), "genbank")
    except Exception as exc:
        st.error(f"Could not read this as a single-record GenBank file: {exc}")
        st.stop()
    length = len(record.seq)
    st.caption(f"Sequence: {record.id} · {length:,} bp · {len(record.features)} annotated features")
    if region_mode == "Choose coordinates":
        c1, c2 = st.columns(2)
        with c1:
            x_start = st.number_input("Start (0-based, inclusive)", min_value=0, max_value=max(length - 1, 0), value=0)
        with c2:
            x_end = st.number_input("End (exclusive)", min_value=1, max_value=max(length, 1), value=length)
    else:
        x_start, x_end = 0, length

    if x_end <= x_start:
        st.warning("End must be greater than start.")
    elif st.button("Run predictions", type="primary", use_container_width=True):
        model = Path(model_path).expanduser()
        executable = shutil.which("openspliceai")
        if not model.is_file():
            st.error(f"Model file not found: {model}")
        elif not executable:
            st.error("Could not find `openspliceai` on the app's PATH. Activate the OpenSpliceAI environment and relaunch the app.")
        else:
            with st.spinner("Running OpenSpliceAI predictions…"):
                work = tempfile.TemporaryDirectory(prefix="openspliceai-")
                root = Path(work.name)
                gb_path, fasta_path, output = root / "input.gb", root / "input.fasta", root / "predictions"
                gb_path.write_bytes(raw)
                SeqIO.convert(str(gb_path), "genbank", str(fasta_path), "fasta")
                cmd = [executable, "predict", "--model", str(model), "--input-sequence", str(fasta_path),
                       "--flanking-size", str(int(flanking_size)), "--threshold", str(threshold), "--predict-all", "--output-dir", str(output)]
                try:
                    run = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    if run.returncode:
                        st.error("Prediction command failed.")
                        st.code((run.stderr or run.stdout)[-6000:])
                    else:
                        beds = list(output.glob("**/donor_predictions.bed")), list(output.glob("**/acceptor_predictions.bed"))
                        if not beds[0] or not beds[1]:
                            st.error("Prediction completed, but expected donor/acceptor BED files were not found.")
                            st.code(run.stdout[-3000:])
                        else:
                            donor, acceptor = read_bed(beds[0][0]), read_bed(beds[1][0])
                            fig = make_plot(record, donor, acceptor, int(x_start), int(x_end), score_cutoff, show_misc)
                            st.pyplot(fig, use_container_width=True)
                            png = io.BytesIO(); fig.savefig(png, format="png", dpi=180, bbox_inches="tight"); plt.close(fig)
                            st.download_button("Download plot (PNG)", png.getvalue(), f"{Path(uploaded.name).stem}_spliceai.png", "image/png")
                            bundle = io.BytesIO()
                            with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
                                archive.write(beds[0][0], "donor_predictions.bed")
                                archive.write(beds[1][0], "acceptor_predictions.bed")
                            st.download_button("Download prediction BED files (ZIP)", bundle.getvalue(), f"{Path(uploaded.name).stem}_predictions.zip", "application/zip")
                            annotated_record = copy.deepcopy(record)
                            donor_count = add_splice_features(annotated_record, beds[0][0], "donor", threshold)
                            acceptor_count = add_splice_features(annotated_record, beds[1][0], "acceptor", threshold)
                            st.caption(f"Annotated GenBank export: {donor_count + acceptor_count:,} splice sites above threshold {threshold:g} ({donor_count:,} donors, {acceptor_count:,} acceptors).")
                            st.download_button("Download annotated GenBank", genbank_bytes(annotated_record), f"{Path(uploaded.name).stem}_spliceai_annotated.gb", "text/plain")
                except OSError as exc:
                    st.error(f"Could not start OpenSpliceAI: {exc}")
                finally:
                    work.cleanup()
else:
    st.info("Upload a GenBank (.gb/.gbk) file to get started.")

st.divider()
st.caption(
    'OpenSpliceAI method: Chao K-H, Mao A, Liu A, Pertea M, Salzberg SL. '
    '“OpenSpliceAI provides an efficient modular implementation of SpliceAI enabling easy retraining across nonhuman species.” '
    '[eLife 14:RP107454 (2025)](https://doi.org/10.7554/eLife.107454.3).'
)
