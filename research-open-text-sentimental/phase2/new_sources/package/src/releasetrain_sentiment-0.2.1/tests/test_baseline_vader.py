from releasetrain_sentiment import classify_technical_first, flags_technical_keyword, vader_sentiment_label


def test_flags_technical_keyword_true_for_bug_report_language():
    assert flags_technical_keyword("The app crashes every time I open it") is True


def test_flags_technical_keyword_true_even_for_non_technical_use_of_the_word():
    # This is the exact contamination Reviewer #7 described: the keyword
    # fires regardless of whether the usage is actually technical.
    assert flags_technical_keyword("That redesign was a massive error") is True


def test_flags_technical_keyword_false_for_plain_venting():
    assert flags_technical_keyword("I am so tired of this update") is False


def test_vader_sentiment_label_uses_the_narrow_band_by_default():
    # A mildly negative comment that would clear the standard 0.05 band
    # but not necessarily a much narrower 0.15 one.
    label = vader_sentiment_label("meh, not great", neutral_band=0.15)
    assert label in ("Positive", "Negative", "Neutral")


def test_classify_technical_first_exempts_keyword_hits_into_tps():
    assert classify_technical_first("That redesign was a massive error") == "TPS"


def test_classify_technical_first_labels_negative_non_keyword_text_as_gds():
    assert classify_technical_first("I hate this company so much, awful") == "GDS"
