# Resume Skills Matching App

This repository includes an application that extracts skills from a PDF resume and compares them with a provided job description. The objective is to highlight matching skills as well as any missing skills relevant to the job.


Before running the app, make sure to have the packages in `requirements.txt` installed and both models downloaded: the fine-tuned NER one in the folder and the one from SpaCy.
To download the SpaCy model run: 
```
python -m spacy download en_core_web_lg.
```

The fine-tuned NER model is used for skills extraction whereas the SpaCy one generates the embeddings and is used by the SkillNer library. 

> **Important Note**:  
> Remember to update the path to the **NER model** in the `load_ner_model` function of the `skills_extractor`.  
> Set the path to point to the folder where your model is located, for instance:  
> `../Models/model-best`

To start the app, run the following command in the terminal:
```
streamlit run app.py
```


The folder contains the following files:

- **`pdf_parser.py`**:  
  Contains functions to parse resumes in PDF format using [pdfplumber](https://github.com/jsvine/pdfplumber).  
  - Extracts and formats the PDF content into sections.  
  - Identifies education details, primarily using regular expressions for better accuracy.  

- **`skills_extractor.py`**:  
  Extracts skills from the resume and job description using a fine-tuned SpaCy NLP model.  
  - **Skills Extraction**: Uses a Named Entity Recognition (NER) model fine-tuned on tech-sector job description data, annotated and available [here](https://drive.google.com/file/d/1QBJWfjQ3sdHdeBVDD6WvqtbfEZyzxpYR/view?usp=drive_link).  
  - **Training Details**: The model was fine-tuned using the SpaCy training pipeline, which can be found [here](https://spacy.io/usage/training).  
  - For skill extraction, different approaches are employed for CVs and Job Descriptions to balance breadth and precision:

    - For CV, skills are extracted using a combination of our fine-tuned NER model and the [SkillNER](https://github.com/AnasAito/SkillNER) library, which relies on a skills database and allows it to retrieve a broader set of skills, including partial matches. This ensures higher recall, which is desirable for CVs where gathering a comprehensive list of potential skills is valuable, even if some have slightly lower relevance.

    - For job descriptions, skills are extracted solely using the fine-tuned model, in this way we make sure to extract highly relevant skills with greater precision so that the results are more focused and reliable. Since ultimately we are comparing skills in the CV against the ones in the job description and not the other way around.

- **`faiss_handler.py`**:  
  Performs matching searches between skills extracted from the resume and the job description using [FAISS](https://github.com/facebookresearch/faiss).  
  - **Indexing**: Job skills are stored in a FAISS index for efficient querying.  
  - **Matching**: Finds the best match for each skill in the resume with a threshold of **0.5**, which we found provided a good balance between skills inclusion and alignment quality.  

- **`app.py`**:  
  The main application interface for users.  
  - Allows users to **upload a PDF resume**.  
  - Accepts **copy-pasted job descriptions** in a dedicated section.  
  - Parses and analyzes both inputs to **output matching and missing skills**.


