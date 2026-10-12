# Public paraphrase table of eight development errors

Illustrative only. These rows are not a rated sample, and the paraphrases are not new labels. Each paraphrase was checked against the saved title and body for that post. Names, handles, dates, prices, model numbers, version strings, file paths, and image links from the source text are omitted. No post identifier is included. The private note is `PRIVATE_CASE_EXAMPLES.md`.

The scored label is the development target: troubleshooting, or other update. Where the stored finer label is general dissatisfaction, the scored target is still other update. The prediction is the inner-threshold title+body model.

| Case | Direction | Saved text, paraphrased | Assigned label | Predicted label |
| --- | --- | --- | --- | --- |
| A | False negative | Title only. A database cluster upgrade left replica nodes marked failed during failover. | Troubleshooting | Other update |
| B | False negative | Title only. Updating site software to the current version returned an internal server error. | Troubleshooting | Other update |
| C | False positive | Title only. A phone keyboard’s emoji panel is described as looking cleaner after an update. | Other update | Troubleshooting |
| D | False positive | Title only. The writer is upgrading to a numbered release and fixing what broke. The body does not say what broke. | Other update | Troubleshooting |
| E | False positive | A long complaint that one phone overheats and freezes during ordinary use and while installing apps, tied by the writer to recent interface updates, while other phones nearby do not. | Other update (stored as general dissatisfaction) | Troubleshooting |
| F | False positive | A question about installing a distribution update before release day. An earlier attempt mostly ran, with startup log warnings the writer asks about ignoring. | Other update | Troubleshooting |
| G | False negative | An automatic upgrade reported an unrecognized configuration key, the connection dropped, and the writer removed that key and restarted the service. | Troubleshooting | Other update |
| H | False negative | A frustrated report that system updates made a pen-enabled laptop crash, followed by a request for advice on rolling back, dual-booting, or changing operating systems. | Troubleshooting | Other update |

Check against the saved text: A is the cluster-upgrade title and nothing else. B is the update-plus-server-error title and nothing else. C is the emoji-panel title and nothing else. D is only the upgrade-and-fixing title. E matches the phone complaint’s symptoms and the comparison with other devices, without the model name or purchase date. F matches the early-update question and the log-warning question, without the distribution name or the image link. G matches the failed automatic upgrade, the unrecognized key, and the manual restart. H matches the crash-after-update report and the three-way operating-system question, without the price or the hardware inventory.
