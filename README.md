# Resume ↔ Job Description Matcher

A deployed NLP tool that scores how well a CV matches a job description, 
identifies missing skill keywords, and helps tailor applications before submitting them.

**Live app:** https://resume-jd-matcher-taqqfpncrhrruv9m34wety.streamlit.app/

## How It Works

1. Paste a job description and upload a CV (PDF/DOCX) or paste text directly
2. Both texts are cleaned — lowercased, stopwords removed, lemmatized, with multi-word 
   technical terms (e.g. "Power BI", "Machine Learning") protected from being split apart
3. TF-IDF vectorization converts both texts into numerical vectors
4. Cosine similarity measures overall text alignment
5. A curated skills whitelist extracts and compares actual technical keywords
6. A blended score (40% text similarity, 60% skill coverage) gives the final match percentage

## Key Design Decisions

- **Curated skills whitelist over pure NLP extraction** — more transparent, predictable, 
  and easy to extend than relying on named entity recognition or pretrained models
- **Weighted blended scoring** — raw TF-IDF similarity is sensitive to document length and 
  dilutes with longer, more varied CVs; blending with explicit skill coverage corrects for this
- **Implied skill expansion** — e.g. "SQL Server" implies "SQL" — multi-word phrase protection 
  can hide component skills, so an explicit expansion step recovers them

## Known Limitations

Keyword matching tests vocabulary overlap, not actual competence. A candidate could have 
genuine deep experience in a skill without using its exact keyword phrasing in their CV. 
This is a known, widely discussed limitation in real-world ATS (Applicant Tracking System) 
software — this project deliberately makes that limitation visible and explainable rather 
than hiding it.

## Tech Stack

Python · Streamlit · scikit-learn (TF-IDF, cosine similarity) · NLTK · PyPDF2 · python-docx

## Run Locally

```bash
git clone https://github.com/sanda0620/resume-jd-matcher.git
cd resume-jd-matcher
pip install -r requirements.txt
streamlit run app.py
```