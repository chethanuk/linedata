import json
import multiprocessing
import os
import traceback
from pathlib import Path
from typing import List

import pandas as pd
import sympy
from PIL import Image
from tqdm import tqdm


def extract_lines(file_path: Path) -> List[str]:
    with file_path.open(mode='r') as f:
        lines = f.readlines()
    return lines


def main():
    project_root = (Path(__file__).parent / "..").absolute()
    output_dir = project_root / "out" / "corpus"
    output_dir.mkdir(exist_ok=True, parents=True)

    file_paths = [
        project_root / "corpus/google_drive" / "high_school.norm (1).txt",
        # project_root / "corpus/google_drive" / "inhouse_QA.norm.txt",
        # project_root / "corpus/google_drive" / "Math.norm.txt"
    ]

    for p in tqdm(file_paths):
        lines = extract_lines(p)
        clean_lines = [l.strip() for l in lines]
        latex_lines = ["".join(['$$', l, '$$']) for l in clean_lines]
        configs = [
            {
                'output_path': str(output_dir / f'{p.stem}_{idx}.png'),
                'content': latext_line
            }
            for idx, latext_line in enumerate(latex_lines)
        ]
        # print(len(latex_lines))
        with multiprocessing.Pool(int(os.cpu_count())) as p:
            target_file_path_sets = [e for e in tqdm(p.imap(render_latex, configs), total=len(configs))]
        # for idx, latex_line in tqdm(enumerate(latex_lines)):


def build_df():
    project_root = (Path(__file__).parent / "..").absolute()
    directory_path: Path = project_root / "out" / "corpus"
    rows = []
    for png_path in tqdm(directory_path.glob('*.png')):
        parts = (png_path.stem.split('_'))
        file_name = '_'.join(parts[:-1])
        index = int(parts[-1])
        im = Image.open(str(png_path))
        w, h = im.size
        rows.append([file_name, index, w, h])
    df = pd.DataFrame(rows, columns=['file_name', 'line_index', 'width', 'height'])
    df['ratio'] = df['width'] / df['height']
    print(df.describe())
    output_dir = project_root / "out" / "dataframes"
    output_dir.mkdir(exist_ok=True, parents=True)
    df.to_csv(output_dir / "out.csv")


def build_corpus_json():
    project_root = (Path(__file__).parent / "..").absolute()
    output_root_dir: Path = project_root / "out"

    csv_path = project_root / 'out' / 'dataframes' / 'out.csv'
    df = pd.read_csv(str(csv_path))
    line_index_to_keep = set(df['line_index'])
    # load the corpus
    file_path = project_root / "corpus/google_drive" / "high_school.norm (1).txt"
    lines = extract_lines(file_path)
    # filter lines
    clean_lines = [l.strip() for line_idx, l in enumerate(lines) if line_idx in line_index_to_keep]
    # output json
    output_dir = output_root_dir / "cleaned_corpus"
    output_dir.mkdir(exist_ok=True, parents=True)
    output_path = output_dir / 'math.json'
    with output_path.open(mode='w') as f:
        output_json = {
            "corpusVersion": 1,
            "language": "math",
            "corpus": clean_lines
        }
        json.dump(output_json, f)


def render_latex(input_config: dict):
    try:
        file_path: Path = input_config['output_path']
        latext: str = input_config['content']
        sympy.preview(latext, viewer='file', filename=str(file_path), euler=False)
    except Exception as e:
        traceback.format_exc()


if __name__ == '__main__':
    build_df()
