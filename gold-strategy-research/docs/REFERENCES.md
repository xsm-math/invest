# References and provenance

Reviewed on 28 September 2026. Commit identifiers and inspected files are recorded in `reference_manifest.json`.

| Repository | Reviewed material | Methodological reference |
|---|---|---|
| [lucienismael/algorithmic-trading-backtester](https://github.com/lucienismael/algorithmic-trading-backtester) | README, strategy.py, walk_forward.py | Modular strategy evaluation, moving-average and z-score rules, sequential parameter selection |
| [codewithpom/GOLD-START](https://github.com/codewithpom/GOLD-START) | README, data_prep.py | Explicit temporal folds, experiment configuration, reproducible reporting |

These repositories informed project organization and methodological comparison. Their source code was not copied, and their reported performance was not adopted. GitHub did not identify licenses for either repository at the time of review. The methods themselves are standard research techniques; these citations do not imply original authorship of the underlying concepts.

Product information: [SPDR Gold Shares](https://www.spdrgoldshares.com/usa/gld/). Prices were retrieved through Yahoo Finance's public historical chart endpoint; see `data/README.md` and the run manifest. Workflow configuration follows [GitHub's Python documentation](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).
