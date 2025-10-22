"""
Starlang Turkish Spell Checker Service
FastAPI microservice for ultra-fast Turkish spell checking

Installation:
pip install fastapi uvicorn NlpToolkit-SpellChecker-Py

Run:
uvicorn main:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time

# Starlang Turkish SpellChecker
try:
    from SpellChecker.SimpleSpellChecker import SimpleSpellChecker
    STARLANG_AVAILABLE = True
except ImportError:
    STARLANG_AVAILABLE = False
    print("WARNING: Starlang library not installed. Install with: pip install NlpToolkit-SpellChecker-Py")

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
if STARLANG_AVAILABLE:
    spell_checker = SimpleSpellChecker()
else:
    spell_checker = None

# Request/Response models
class CheckRequest(BaseModel):
    text: str
    max_suggestions: int = 5
    include_morphology: bool = False

class Correction(BaseModel):
    original: str
    corrected: str
    position: int
    type: str  # 'spelling', 'diacritic', 'unknown'
    suggestions: List[str] = []

class CheckResponse(BaseModel):
    original: str
    corrected: str
    corrections: List[Correction]
    confidence: float
    processing_time_ms: float
    words_checked: int
    errors_found: int

@app.get("/")
async def root():
    return {
        "service": "Starlang Turkish Spell Checker",
        "status": "running",
        "starlang_available": STARLANG_AVAILABLE,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "starlang_available": STARLANG_AVAILABLE
    }

@app.post("/check", response_model=CheckResponse)
async def check_spelling(request: CheckRequest):
    """
    Check Turkish spelling and return corrections
    
    Args:
        text: Text to check
        max_suggestions: Maximum number of suggestions per error
        include_morphology: Include morphological analysis (slower)
    
    Returns:
        Corrected text with details
    """
    
    if not STARLANG_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Starlang library not available. Please install NlpToolkit-SpellChecker-Py"
        )
    
    if not request.text or len(request.text) > 10000:
        raise HTTPException(
            status_code=400,
            detail="Text must be between 1 and 10000 characters"
        )
    
    start_time = time.time()
    
    try:
        # Process text
        text = request.text.strip()
        words = text.split()
        
        corrections = []
        corrected_words = []
        errors_found = 0
        
        for i, word in enumerate(words):
            # Clean word (remove punctuation for checking)
            clean_word = ''.join(c for c in word if c.isalpha() or c in 'çÇğĞıİöÖşŞüÜ')
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            # Check spelling
            sentence = Sentence(clean_word)
            corrected_sentence = spell_checker.spellCheck(sentence)
            
            if corrected_sentence:
                corrected_word = str(corrected_sentence)
                
                if corrected_word.lower() != clean_word.lower():
                    # Found correction
                    errors_found += 1
                    
                    # Get suggestions
                    suggestions = get_suggestions(spell_checker, clean_word, request.max_suggestions)
                    
                    corrections.append(Correction(
                        original=clean_word,
                        corrected=corrected_word,
                        position=i,
                        type=determine_error_type(clean_word, corrected_word),
                        suggestions=suggestions
                    ))
                    
                    # Replace in original word (preserve punctuation)
                    corrected_words.append(
                        word.replace(clean_word, corrected_word)
                    )
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        
        # Calculate confidence
        if errors_found == 0:
            confidence = 1.0
        else:
            # Lower confidence if many errors
            confidence = max(0.5, 1.0 - (errors_found / len(words)) * 0.5)
        
        processing_time = (time.time() - start_time) * 1000
        
        return CheckResponse(
            original=request.text,
            corrected=corrected_text,
            corrections=corrections,
            confidence=confidence,
            processing_time_ms=round(processing_time, 2),
            words_checked=len(words),
            errors_found=errors_found
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/check-word")
async def check_word(word: str, max_suggestions: int = 5):
    """
    Check a single word
    
    Args:
        word: Single word to check
        max_suggestions: Maximum suggestions
    
    Returns:
        Correction result for word
    """
    
    if not STARLANG_AVAILABLE:
        raise HTTPException(status_code=503, detail="Starlang not available")
    
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
                "suggestions": get_suggestions(spell_checker, word, max_suggestions) if not is_correct else []
            }
        
        return {
            "original": word,
            "corrected": word,
            "is_correct": True,
            "suggestions": []
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_suggestions(checker, word: str, max_count: int = 5) -> List[str]:
    """
    Get alternative suggestions for a word
    """
    try:
        # Starlang'ın öneri sistemini kullan
        # Bu kısım Starlang API'sine göre ayarlanmalı
        suggestions = []
        
        # Basit edit distance ile alternatifler
        # Gerçek implementasyonda Starlang'ın kendi öneri sistemi kullanılmalı
        
        return suggestions[:max_count]
    except:
        return []

def determine_error_type(original: str, corrected: str) -> str:
    """
    Determine the type of error
    """
    # Türkçe karakterler
    turkish_chars = 'çÇğĞıİöÖşŞüÜ'
    
    # Check if only diacritics differ
    orig_normalized = original.replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i')\
                             .replace('ö', 'o').replace('ş', 's').replace('ü', 'u').lower()
    corr_normalized = corrected.replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i')\
                               .replace('ö', 'o').replace('ş', 's').replace('ü', 'u').lower()
    
    if orig_normalized == corr_normalized:
        return 'diacritic'
    
    # Check length difference
    if abs(len(original) - len(corrected)) > 2:
        return 'spelling'
    
    return 'spelling'

# Mock Sentence class if Starlang not available
if not STARLANG_AVAILABLE:
    class Sentence:
        def __init__(self, text):
            self.text = text
        
        def __str__(self):
            return self.text

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
