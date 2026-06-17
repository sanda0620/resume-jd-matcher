import nltk

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

SKILL_PHRASES = {
    'power bi': 'powerbi',
    'machine learning': 'machinelearning',
    'random forest': 'randomforest',
    'spring boot': 'springboot',
    'spring security': 'springsecurity',
    'real time': 'realtime',
    'data science': 'datascience',
    'data analyst': 'dataanalyst',
    'sql server': 'sqlserver',
}

KNOWN_SKILLS = {
    'python', 'sql', 'java', 'javascript',
    'panda', 'numpy', 'scikitlearn', 'machinelearning', 'randomforest',
    'regression', 'classification', 'matplotlib', 'seaborn', 'visualization',
    'datascience', 'dataanalyst', 'eda',
    'powerbi', 'excel', 'tableau', 'dashboard',
    'docker', 'kafka', 'realtime', 'pipeline', 'postgresql', 'mongodb',
    'sqlserver', 'cloud', 'aws', 'azure', 'gcp',
    'springboot', 'springsecurity', 'react', 'nodejs', 'api',
    'communication', 'collaboration', 'agile', 'leadership',
}


def protect_phrases(text):
    text = text.lower()
    text = text.replace('-', ' ')
    for phrase, token in SKILL_PHRASES.items():
        text = text.replace(phrase, token)
    return text


def clean_text(text):
    text = protect_phrases(text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 1]
    words = [lemmatizer.lemmatize(w) for w in words]
    return ' '.join(words)


def extract_skills(word_set, whitelist=KNOWN_SKILLS):
    return word_set & whitelist


def expand_implied_skills(skill_set):
    expanded = set(skill_set)
    if 'sqlserver' in expanded:
        expanded.add('sql')
    if 'randomforest' in expanded:
        expanded.add('machinelearning')
    return expanded


def match_resume_to_jd(jd_text, cv_text):
    cleaned_jd = clean_text(jd_text)
    cleaned_cv = clean_text(cv_text)

    docs = [cleaned_jd, cleaned_cv]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(docs)
    similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]

    jd_words = set(cleaned_jd.split())
    cv_words = set(cleaned_cv.split())

    jd_skills = extract_skills(jd_words)
    cv_skills = expand_implied_skills(extract_skills(cv_words))

    matched = jd_skills & cv_skills
    missing = jd_skills - cv_skills

    skill_coverage = len(matched) / len(jd_skills) if jd_skills else 0
    final_score = round((similarity * 0.4 + skill_coverage * 0.6) * 100, 1)

    return {
        'final_score': final_score,
        'tfidf_similarity': round(similarity * 100, 1),
        'skill_coverage': round(skill_coverage * 100, 1),
        'matched_skills': sorted(matched),
        'missing_skills': sorted(missing),
        'total_jd_skills': len(jd_skills)
    }


import PyPDF2
from docx import Document


def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "
    return text


def extract_text_from_docx(uploaded_file):
    doc = Document(uploaded_file)
    text = " ".join([para.text for para in doc.paragraphs])
    return text


def extract_text_from_file(uploaded_file):
    """
    Detects file type by extension and extracts text accordingly.
    """
    filename = uploaded_file.name.lower()

    if filename.endswith('.pdf'):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(uploaded_file)
    else:
        return None