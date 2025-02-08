import numpy as np
import faiss


def preprocess(skill):
    """
    Normalize and preprocess a skill string.
    """
    return skill.strip().lower()

def get_embedding(text, nlp):
    """
    Returns the embedding for a word or phrase using SpaCy.
    """
    return nlp(text).vector

def compute_skill_score(cv_skills, job_skills, nlp, threshold=0.6, k=2):
    """
    Compute skill matching score and find missing and overlapping skills.

    Parameters:
        cv_skills (list): List of skills from the CV.
        job_skills (list): List of skills from the job description.
        word2vec: Word embedding model.
        threshold (float): Threshold for cosine similarity to consider a match.
        k (int): Number of closest matches to retrieve for each skill.

    Returns:
        tuple: Match score (percentage), missing skills (list), overlapping skills (list)

    """
    #word2vec = load_word2vec_model()

    cv_skills = list(set(preprocess(skill) for skill in cv_skills))
    job_skills = list(set(preprocess(skill) for skill in job_skills))

    cv_embeddings = np.array([get_embedding(skill, nlp) for skill in cv_skills], dtype=np.float32)
    job_embeddings = np.array([get_embedding(skill, nlp) for skill in job_skills], dtype=np.float32)

    faiss.normalize_L2(cv_embeddings)
    faiss.normalize_L2(job_embeddings)

    # Build FAISS index
    dimension = nlp.vocab.vectors_length  
    faiss_index = faiss.IndexFlatIP(dimension)  
    faiss_index.add(job_embeddings)

    k = 1
    distances, indices = faiss_index.search(cv_embeddings, k)

    # Threshold for similarity (We found 0.5 to be a good threshold)
    threshold = 0.5
    best_matches = {}
    unmatched_cv_skills = []

    for i, (dist, idx) in enumerate(zip(distances, indices)):
        similarity = dist[0]  
        if similarity >= threshold:
            best_matches[cv_skills[i]] = {
                "match": job_skills[idx[0]],
                "similarity": similarity
            }
        else:
            unmatched_cv_skills.append(cv_skills[i])

    average_similarity = (
        sum([match["similarity"] for match in best_matches.values()]) / len(best_matches)
        if best_matches else 0.0
    )

    matched_skills = [match['match'] for match in best_matches.values()]
    unmatched_job_skills = [skill for skill in job_skills if skill not in matched_skills]

    return round(average_similarity * 100, 2), set(unmatched_job_skills), set(matched_skills)