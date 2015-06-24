## Semantic Tagger for Japanese Functional Expressions (FEs)
Assign semantic labels to each FEs in the input sentence.

## Usage
`echo "*sentence*" | bash run_tagger.sh`

## Components
- **run_tagger.sh** - Main file.
- **unit_sent_feature.py** - Script for extracting features.
- **output.py** - Script for displaying the result.
- **1627.m** - Model file trained with 1,627 texts in the OC category.
- sentence.cabocha - Artifact (result from cabocha).
- sentence.f - Artifact (features).
- sentence.tagged - Artifact (list of tagged labels).
- README.md - This file.

## Required
- [CaboCha](http://taku910.github.io/cabocha/)
- [CRFSuite](http://www.chokkan.org/software/crfsuite/)
