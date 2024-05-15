import sacrebleu

def compute_bleu(reference_texts, candidate_text):
    # The reference_texts must be a list of strings (one or more reference translations)
    # The candidate_text is a single string of the translated text to evaluate

    # Wrap the candidate text in a list
    candidate = [candidate_text]

    # Compute BLEU score
    bleu_score = sacrebleu.corpus_bleu(candidate, [reference_texts])
    
    # Print detailed BLEU score information
    print("BLEU Score:", bleu_score.score)
    print("Detailed Score:", bleu_score.format())
    return bleu_score

ref_verse = [' نكين بولوس، نّا ئختار ربي س لموراض نّس، حما أد ݣخ امازان ن عيسى لمسيح. ؤريخ-تابرات-اد نكّين د سوستانوس، ؤماتنخ ݣ ليمان،']
             
cand_verse = 'ثابراتّ أد زّيݣي نكّين بولوس، ئݣان أمازان ن ـ سيدنا عيسى لماسيح س ـ ثانباطّ ن ـ ربّي، د زݣ ثماتنخ ن ـ ثيموثاوس.'

score = compute_bleu(ref_verse, cand_verse)
print(f"BLEU score: {score}")
