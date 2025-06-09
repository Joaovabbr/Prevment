from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

MODEL_NAME = "EdsonMorro/analise-sentimento"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def word_analyser(texto):
    """
    Analisa o sentimento de um texto usando um modelo de análise de sentimentos.
    
    :param texto: Texto a ser analisado.
    :return: Resultado da análise de sentimento.
    """
    resultado = sentiment_pipeline(texto)
    return resultado

