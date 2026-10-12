# Private illustrative development errors

These eight posts are examples, not an adjudicated review and not a sample for rates. Analyst notes below are readings of the saved text. They do not change `s2_target`, `discussion_type`, or `pred_title_body`, and they are not frequencies.

Predictions are `pred_title_body` in `phase5/expanded_study/results/predictions.jsonl` (inner-threshold title+body model). Text is the matching row in `phase3/reddit_only_sensitivity/development_reddit_only.jsonl`. The scored label is `s2_target`: 1 troubleshooting, 0 other update. `discussion_type` is the stored finer label.

## 1. False negative, empty body, technical wording

- Post ID: `1klgbni` (study id `C2-5BFD498A0B41`)
- Evidence: `title` only. `post_body` is empty. `text_availability` is `title_only`. The whole scored string is: `Issue upgrading Redis cluster from 7.0.9 to 7.2.0: Slaves marked as failed during failover`
- True assigned label: `s2_target` 1, `discussion_type` `technical_troubleshooting`
- Predicted label: 0 (other update)
- Reading: the title names versions, a cluster upgrade, and a failover failure. There is no body with logs or a question. This note does not decide whether the assigned label is right.

## 2. False negative, empty body, short failure wording

- Post ID: `1k75x4h` (study id `C2-13ED8799FC46`)
- Evidence: `title` only. `post_body` is empty. The whole scored string is: `Update wordpress to latest version results in 500 (internal server error)`
- True assigned label: `s2_target` 1, `discussion_type` `technical_troubleshooting`
- Predicted label: 0
- Reading: the title states an update and an HTTP 500. It does not say what was tried or what the server log showed.

## 3. False positive, empty body, update announcement

- Post ID: `1kn7g7m` (study id `C2-5FD6A566F72E`)
- Evidence: `title` only. `post_body` is empty. The whole scored string is: `Gboard's emoji panel is getting a cleaner look in its latest update`
- True assigned label: `s2_target` 0, `discussion_type` `other`
- Predicted label: 1 (troubleshooting)
- Reading: the title describes a visual change in an update. It does not describe a fault or ask for a fix.

## 4. False positive, empty body, update ambiguity

- Post ID: `1mags0w` (study id `C2-BA80419C9808`)
- Evidence: `title` only. `post_body` is empty. The whole scored string is: `Upgrading to 0.11 and fixing everything that broke`
- True assigned label: `s2_target` 0, `discussion_type` `other`
- Predicted label: 1
- Reading: the title mentions breakage and fixing it, but the saved text never says what broke. The assigned label is other update. The title alone can be read either as a repair note or as a problem report.

## 5. False positive, body present, complaint mixed with failure symptoms

- Post ID: `1th5jal` (study id `C2-003FDA27B790`)
- Evidence: `title` plus `post_body` (4,232 characters). `text_availability` is `title_body_comments`; the model input is title and body, not comments.
  - Title: `One UI is Destroying the Experience on My Galaxy A35 5G`
  - Body, opening sentence: overheating, freezing, and poor optimization “ever since a few recent updates,” model `SM-A356E`, suspected around One UI 8.0.
  - Body, later: Play Store installs freeze the phone; the same downloads on other devices at home do not; the writer dates the change to recent updates and asks for a later patch.
- True assigned label: `s2_target` 0, `discussion_type` `general_dissatisfaction`
- Predicted label: 1
- Reading: the body is a complaint and also a symptom report tied to updates. The scored label is other update, via general dissatisfaction, not troubleshooting.

## 6. False positive, body present, update ambiguity

- Post ID: `1swjx2c` (study id `C2-09BAA74D6C53`)
- Evidence: `title` and `post_body` (728 characters). `text_availability` is `title_and_body`.
  - Title: `Any risk updating to Fedora 44 two days early on AMD hardware?`
  - Body: asks whether Gnome 50 on the current Fedora 44 has issues; an attempt two weeks earlier “ran ok” aside from three startup warnings, two about tpm udev rules (`failed to resolve group 'tss'`) and one about Firefox; asks whether to wait or ignore the logs. An image link is in the body and was not opened for this note.
- True assigned label: `s2_target` 0, `discussion_type` `other`
- Predicted label: 1
- Reading: the post asks about risk before release and also reports log lines from an earlier attempt. The assigned label is other update. The text mixes a go/no-go question with warning messages.

## 7. False negative, body present, technical wording

- Post ID: `1secdwj` (study id `C2-0D49D7587A76`)
- Evidence: `title` and `post_body` (505 characters). `text_availability` is `title_and_body`.
  - Title: `Cron auto-update broke OpenClaw: config validation error (cliBackends) → lost connection, manual fix & restart` (stored with `&amp;`)
  - Body: a cron job upgraded the tool; the quoted status line says `agents.defaults.cliBackends is unrecognized` in `~/.openclaw/openclaw.json`; the connection was lost; the writer deleted that section and ran `openclaw gateway restart`.
- True assigned label: `s2_target` 1, `discussion_type` `technical_troubleshooting`
- Predicted label: 0
- Reading: the body includes a configuration error and the commands used after it. It also reads as a completed fix. The scored label remains troubleshooting.

## 8. False negative, body present, complaint mixed with a technical request

- Post ID: `1qobtoo` (study id `C2-46EE10A70640`)
- Evidence: `title` and `post_body` (2,858 characters). `text_availability` is `title_and_body`.
  - Title: `My 3000€ HP ZBook x2 G4 is being bricked by Windows Updates (Stylus BSOD). Downgrade to 22H2 or switch to Linux?`
  - Body, “The Main Problem”: fine on Windows 11 22H2; after newer versions, a Wacom driver memory leak ends in a BSOD and blocks handwritten notes.
  - Body, “My Dilemma”: asks whether to roll back and block updates, dual-boot, or switch to Linux, and lists hardware constraints (mixed DPI, Wacom, biometrics, hybrid graphics).
- True assigned label: `s2_target` 1, `discussion_type` `technical_troubleshooting`
- Predicted label: 0
- Reading: the post reports a crash after updates and also asks which operating system to move to. The scored label is troubleshooting. The advice request is part of the same saved body.
