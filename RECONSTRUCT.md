# Reconstructing binary artefacts

The specification PDFs and database are stored as base64 in the `specs/` directory
(when pushed). To reconstruct:

```bash
for f in specs/*.b64; do
  base64 -d "$f" > "${f%.b64}"
done
```

Files:
- 6185-Core-Execution-Specification-v0.1.pdf
- 6185-EBNF-Grammar-v0.1.pdf
- 6185-EBNF-Parsed-Examples.pdf
- 6185-Hash-Shape-Volume-Descriptor.pdf
- CAL-KEN-CONST-001-Constitutional-Baseline.pdf
- CAL-KEN-Specification-v8.0.pdf
- CAL-KEN-Governance-as-Data.pdf
- CAL-KEN-Programme-Transition.pdf
- HRS-6185-Railcart-Model.pdf
- HRS-6185-Comparative-Witness-Rail.pdf
- HRS-6185-Descriptor-Convergence.pdf
- HRS-6185-Yiddish-Component.pdf
- HRS-6185-Hebrew-Glyphs.pdf
- HRS-6185-Signing-Documentation.pdf
- 6185-Code-Construct-Hash-Pool.db

All source and rules are already in `engine/`.
