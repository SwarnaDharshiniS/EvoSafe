# R2 Safety Independence Check

Dataset hash: `c40f92f8c0b49732a045469c1091bccf32d5d14360234456edc8fb7218680082`
Verified implementation fingerprint: `72e0dd15c716bd8162203c34e66e61b86c90f4fed119c86ce26e42bf15fa21df`

Compared the current fingerprint-matched implementation on every locked source with EA inference disabled and enabled; safety verdict was read from the same Safety IR result in both modes. No source program was executed.

- Programs tested: 936
- Matching verdicts: 936
- Mismatches: 0
- Experiment errors: 0

| Ground-truth subset | Tested | Matching | Mismatches |
|---|---:|---:|---:|
| SAFE EA | 17 | 17 | 0 |
| UNSAFE EA | 24 | 24 | 0 |
| SAFE non-EA | 18 | 18 | 0 |
| UNSAFE non-EA | 43 | 43 | 0 |

Cases with `CONDITIONALLY_SAFE` or `UNKNOWN` safety truth are not included in the four requested SAFE/UNSAFE EA/non-EA subtotals; they were included in the full 936-program equality test.
