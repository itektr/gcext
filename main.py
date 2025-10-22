"""
Starlang Turkish Spell Checker Service
FastAPI microservice for ultra-fast Turkish spell checking

Installation:
pip install -r requirements.txt

Run:
uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

# Starlang Turkish SpellChecker - GitHub'dan yüklenmiş
try:
    from SpellChecker.SimpleSpellChecker import SimpleSpellChecker
    from Corpus.Sentence import Sentence
    STARLANG_AVAILABLE = True
    print("✅ Starlang kütüphanesi yüklendi")
except ImportError as e:
    STARLANG_AVAILABLE = False
    print(f"⚠️ Starlang kütüphanesi yüklenemedi: {e}")
    print("Service basit mod ile çalışacak (AI entegrasyonu için)")

app = FastAPI(
    title="Starlang Turkish Spell Checker Service",
    description="Ultra-fast Turkish spell checking using Starlang NLP Toolkit",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize spell checker
spell_checker = None
if STARLANG_AVAILABLE:
    try:
        spell_checker = SimpleSpellChecker()
        print("✅ Spell checker başlatıldı")
    except Exception as e:
        print(f"⚠️ Spell checker başlatılamadı: {e}")
        STARLANG_AVAILABLE = False

# Request/Response models
class CheckRequest(BaseModel):
    text: str
    max_suggestions: int = 5
    include_morphology: bool = False

class Correction(BaseModel):
    original: str
    corrected: str
    position: int
    type: str
    suggestions: List[str] = []

class CheckResponse(BaseModel):
    original: str
    corrected: str
    corrections: List[Correction]
    confidence: float
    processing_time_ms: float
    words_checked: int
    errors_found: int
    starlang_available: bool

@app.get("/")
async def root():
    return {
        "service": "Starlang Turkish Spell Checker",
        "status": "running",
        "starlang_available": STARLANG_AVAILABLE,
        "version": "1.0.0",
        "message": "POST /check ile yazım kontrolü yapın" if STARLANG_AVAILABLE else "Starlang yüklü değil - sadece API endpoint aktif"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "starlang_available": STARLANG_AVAILABLE,
        "ready": True
    }

@app.post("/check", response_model=CheckResponse)
async def check_spelling(request: CheckRequest):
    """
    Check Turkish spelling and return corrections
    """
    
    if not STARLANG_AVAILABLE:
        # Starlang yok, basit yanıt dön
        return CheckResponse(
            original=request.text,
            corrected=request.text,
            corrections=[],
            confidence=0.0,
            processing_time_ms=0.0,
            words_checked=0,
            errors_found=0,
            starlang_available=False
        )
    
    if not request.text or len(request.text) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Text must be between 1 and 10000 characters"
        )
    
    start_time = time.time()
    
    try:
        text = request.text.strip()
        words = text.split()
        
        corrections = []
        corrected_words = []
        errors_found = 0
        
        for i, word in enumerate(words):
            # Temiz kelime (noktalama işaretlerini çıkar)
            clean_word = ''.join(c for c in word if c.isalpha() or c in 'çÇğĞıİöÖşŞüÜ')
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            try:
                # Starlang ile kontrol
                sentence = Sentence(clean_word)
                corrected_sentence = spell_checker.spellCheck(sentence)
                
                if corrected_sentence:
                    corrected_word = str(corrected_sentence)
                    
                    if corrected_word.lower() != clean_word.lower():
                        errors_found += 1
                        
                        corrections.append(Correction(
                            original=clean_word,
                            corrected=corrected_word,
                            position=i,
                            type=determine_error_type(clean_word, corrected_word),
                            suggestions=[]
                        ))
                        
                        corrected_words.append(
                            word.replace(clean_word, corrected_word)
                        )
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)
                    
            except Exception as e:
                print(f"Kelime işlenirken hata: {word} - {e}")
                corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        
        # Güven hesapla
        if errors_found == 0:
            confidence = 1.0
        else:
            confidence = max(0.5, 1.0 - (errors_found / len(words)) * 0.5)
        
        processing_time = (time.time() - start_time) * 1000
        
        return CheckResponse(
            original=request.text,
            corrected=corrected_text,
            corrections=corrections,
            confidence=confidence,
            processing_time_ms=round(processing_time, 2),
            words_checked=len(words),
            errors_found=errors_found,
            starlang_available=True
        )
    
    except Exception as e:
        print(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/check-word")
async def check_word(word: str, max_suggestions: int = 5):
    """Check a single word"""
    
    if not STARLANG_AVAILABLE:
        return {
            "original": word,
            "corrected": word,
            "is_correct": False,
            "suggestions": [],
            "starlang_available": False
        }
    
    if not word or len(word) > 100:
        raise HTTPException(status_code=400, detail="Invalid word")
    
    try:
        sentence = Sentence(word)
        corrected = spell_checker.spellCheck(sentence)
        
        if corrected:
            corrected_word = str(corrected)
            is_correct = corrected_word.lower() == word.lower()
            
            return {
                "original": word,
                "corrected": corrected_word,
                "is_correct": is_correct,
                "suggestions": [],
                "starlang_available": True
            }
        
        return {
            "original": word,
            "corrected": word,
            "is_correct": True,
            "suggestions": [],
            "starlang_available": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def determine_error_type(original: str, corrected: str) -> str:
    """Determine the type of error"""
    turkish_chars = 'çÇğĞıİöÖşŞüÜ'
    
    # Sadece Türkçe karakterler farklı mı?
    orig_normalized = original.replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i')\
                             .replace('ö', 'o').replace('ş', 's').replace('ü', 'u').lower()
    corr_normalized = corrected.replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i')\
                               .replace('ö', 'o').replace('ş', 's').replace('ü', 'u').lower()
    
    if orig_normalized == corr_normalized:
        return 'diacritic'
    
    if abs(len(original) - len(corrected)) > 2:
        return 'spelling'
    
    return 'spelling'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
