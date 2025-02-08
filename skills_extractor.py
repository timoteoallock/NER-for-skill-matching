# Description: This file contains the function to extract skills from the input text using the skill extractor and NER model.

import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from collections import defaultdict


ner_model = None

def load_ner_model():
    global ner_model
    if ner_model is None:
        ner_model_path = "path/to/ner_model"
    

        ner_model = spacy.load(ner_model_path)
    return ner_model

def extract_skills_from_text(text: str, type: str, nlp) -> set:
    """
    Extracts skills from the input text using the skill extractor and NER model.
    """

    if type == 'cv':
        #nlp = spacy.load("en_core_web_lg")
        skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
    model = load_ner_model()
    skills_general = model(text)

    entities_by_label = defaultdict(set)
    for ent in skills_general.ents:
        entities_by_label[ent.label_].add(ent.text)

    skills_general = list(entities_by_label.get('SKILLS', []))

    if type == 'cv':
        cv_skills = skills_general
        annotations = skill_extractor.annotate(text)

        # Extract full matches
        full_matches = set(
            [annotations['results']['full_matches'][i]['doc_node_value'] 
            for i in range(len(annotations['results']['full_matches']))]
        )


        partial_matches = set(
            [annotations['results']['ngram_scored'][i]['doc_node_value'] 
            for i in range(len(annotations['results']['ngram_scored']))]
        )

        combined_cv_skills = set(cv_skills)  
        combined_cv_skills.update(full_matches) 
        combined_cv_skills.update(partial_matches)
        return combined_cv_skills
    else:
        return skills_general