class Corpus:
    def __init__(self, transcript: str, segments: str, wav_scp: str, utt2spk: str, spk2utt: str) -> None:
        super().__init__()
