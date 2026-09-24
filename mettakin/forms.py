class PlainLabels:
    """Labels without Django's trailing colon, so they read as sentences."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super().__init__(*args, **kwargs)
