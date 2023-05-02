from pathlib import Path


def main():
    corpus_json = {
        "corpusVersion": 1
    }
    corpus = [f"x^2+{i}" for i in range(300000)]
    corpus_json["corpus"] = corpus
    import json

    output_file = Path(__file__).parent / "fake_corpus.json"
    with output_file.open(mode="w") as f:
        json.dump(corpus_json, f)


if __name__ == '__main__':
    main()
