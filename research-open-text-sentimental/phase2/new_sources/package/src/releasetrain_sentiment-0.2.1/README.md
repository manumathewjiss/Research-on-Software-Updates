# releasetrain-sentiment

Scores sentiment per comment in a Reddit discussion thread, flagging author
replies vs. community responses, to measure sentiment divergence over time.

Main developer: [manumathewjiss](https://github.com/manumathewjiss)

## Install

```
pip install releasetrain-sentiment
```

Two optional extras:

```
pip install releasetrain-sentiment[classify]   # TPS/GDS classifier (scikit-learn)
pip install releasetrain-sentiment[fetch]      # live ReleaseTrain API wrapper (requests)
```

## Quickstart: scoring a thread

```python
from releasetrain_sentiment import score_post, trajectory_summary

post = {
    "title": "Update broke my build",
    "description": "Nothing compiles since 3.2.0",
    "comments": [
        {"text": "Known issue, fix coming soon", "author": "dev1", "is_author": True},
        {"text": "Same here, very annoying", "author": "user2", "is_author": False},
        {"text": "Thanks for the heads up", "author": "dev1", "is_author": True},
    ],
}

results = score_post(post)
# results[0] is the post itself (source="post", index=-1)
# results[1:] is one entry per comment, same order as the input,
# each with compound/pos/neu/neg/label and is_author

summary = trajectory_summary(results)
# {"author_avg": ..., "community_avg": ..., "author_shift": ..., "community_shift": ...}
```

`score_posts(list_of_posts)` runs the same thing over a batch, returning
one results array per input post, same order.

## Command-line interface

Installed alongside the library as the `releasetrain-sentiment` command
(also runnable as `python -m releasetrain_sentiment`). Each subcommand is a
thin wrapper around the same function shown above, one-to-one, so the CLI
and the Python API never drift in behavior from each other.

```
releasetrain-sentiment --help
```

Score a post, reading JSON from a file:

```
releasetrain-sentiment score --input thread.json --pretty
```

...or piped in from stdin (a JSON array of posts also works, and prints
one `{"items": ..., "trajectory": ...}` object per post):

```
echo '{"title": "Update broke my build", "description": "Nothing compiles since 3.2.0", "comments": [{"text": "Known issue, fix coming soon", "author": "dev1", "is_author": true}, {"text": "Same here, very annoying", "author": "user2", "is_author": false}]}' | releasetrain-sentiment score
```

Check the keyword-contamination issue Reviewer #7 described, directly
from the command line:

```
releasetrain-sentiment keyword-check "That redesign was a massive error" "I am so tired of this update"
# True    That redesign was a massive error
# False   I am so tired of this update
```

Print both the standard VADER label and the `technical_first` baseline
label for one or more texts:

```
releasetrain-sentiment label "I am so tired of this update"
# I am so tired of this update
#   vader=Negative  technical_first=GDS
```

Classify text(s) with a model you've already trained and saved with
`save_classifier()` (requires `pip install releasetrain-sentiment[classify]`):

```
releasetrain-sentiment classify --model tps_gds_model.joblib "the app crashed again"
```

Pull recent posts from a live ReleaseTrain instance and convert them to
this package's scoreable shape in one step (requires
`pip install releasetrain-sentiment[fetch]`):

```
releasetrain-sentiment fetch --limit 20 --out posts.json
releasetrain-sentiment score --input posts.json --pretty
```

## Modules

- `score.py`: the scorer above. Pure function, no network calls, no
  ReleaseTrain coupling. Standard VADER thresholds (compound >= 0.05
  positive, <= -0.05 negative).
- `baseline_vader.py`: a reconstruction of the paper's "technical_first"
  VADER baseline described in Reviewer #7's feedback (a keyword
  exemption plus a narrower +/- 0.15 neutral band). This is a
  reconstruction from the reviewer's written description, not the
  original experiment code, which was not available when this package
  was built. See the module docstring before citing it as a faithful
  reproduction.
- `classify.py`: a trainable TF-IDF + Multinomial Naive Bayes pipeline
  (Reviewer #9: "Multinomial Naive Bayes achieves the best balance in
  identifying the minority TPS class"). No pretrained model ships with
  this package; train it on your own labeled data.
- `corpus.py`: the corpus and labeling documentation reviewers #4, #7,
  and #9 each independently asked for (which subreddits/timeframes, what
  API, how labeled). `ENHANCED_AUTOMATED_CORPUS` is filled in from real,
  verified data; `TPSGDS542_CORPUS` has placeholder fields that need the
  actual gold-dataset values filled in before citing it in the paper.
- `evaluate.py`: `sample_high_divergence()` implements Reviewer #4's
  suggested audit (30 high-divergence TPS threads vs. 30 high-divergence
  GDS threads); `evaluate_predictions()` is a small precision/recall/F1
  harness for testing the "helps developers find useful reports" claim
  against a labeled ground truth, however small.
- `fetch.py`: an optional thin wrapper around ReleaseTrain's
  `/api/reddit` endpoint, isolated from every other module so none of
  them need network access to run or be tested.
- `cli.py`: the `releasetrain-sentiment` console script (see "Command-line
  interface" above). Argument parsing and JSON I/O only, no logic of its
  own - every subcommand calls straight into one of the modules above.

## Example: the keyword-contamination check

```python
from releasetrain_sentiment import flags_technical_keyword

flags_technical_keyword("That redesign was a massive error")  # True
flags_technical_keyword("I am so tired of this update")       # False
```

The first example is the exact contamination Reviewer #7 describes: the
keyword fires regardless of whether the comment is actually a bug report.

## Example: training a classifier

```python
from releasetrain_sentiment import train_classifier, classify, save_classifier

texts = ["crash on launch every time", "app freezes after the update",
         "I'm so tired of this update", "another pointless update, ugh"]
labels = ["TPS", "TPS", "GDS", "GDS"]

pipe = train_classifier(texts, labels)
classify(pipe, ["the app crashed again"])  # ["TPS"]
save_classifier(pipe, "tps_gds_model.joblib")
```

## Known limitations

- No pretrained TPS/GDS classifier ships with this package. The original
  542-post gold-labeled dataset was not available when it was built.
- `baseline_vader.py` is a best-effort reconstruction of a described
  flaw, not a verified reproduction of the original experiment code.
- `TPSGDS542_CORPUS` in `corpus.py` has unfilled fields (subreddit list,
  date range, labeling process) that need the real dataset to complete.

## Releasing to PyPI

Publishing uses PyPI's Trusted Publishing: no API token is stored in this
repo or anywhere else. One-time setup, done once by whoever owns the
`sberhe-se4cps` PyPI account:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new pending publisher with:
   - PyPI project name: `releasetrain-sentiment`
   - Owner: `SE4CPS`
   - Repository name: `releasetrain-sentiment`
   - Workflow name: `publish.yml`
   - Environment name: `pypi`
3. Save it. This registers the project on PyPI without uploading
   anything yet.

After that, every GitHub Release published from this repo (tag it
`v0.1.0`, draft a release from that tag) automatically builds and
publishes to PyPI via `.github/workflows/publish.yml`. No further manual
steps or secrets needed.

## License

MIT
