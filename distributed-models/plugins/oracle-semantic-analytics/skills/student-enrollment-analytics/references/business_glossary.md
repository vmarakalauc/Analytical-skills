# Student Enrollment Business Glossary

## Student count
Distinct count of students, normally `COUNT(DISTINCT SCHOLAR_WID)`.

## Active enrollment
Enrollment records with:
- `DELETE_FLG = 'N'`
- `X_TERM_ENROLLED_FLAG = 'Y'`

## Academic program
The student's academic program for grouping enrollment metrics.

## Term
Academic term. Clarify ambiguous references such as "current term" or "this term."
