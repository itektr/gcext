# Starlang Turkish Spell Checker - Render.com Deployment

## 📁 Dosyalar

Bu klasörde Render.com'a deploy etmek için gereken tüm dosyalar var:

- `main.py` - FastAPI uygulaması (Starlang spell checker service)
- `requirements.txt` - Python bağımlılıkları
- `render.yaml` - Render.com konfigürasyonu (opsiyonel)

## 🚀 Render.com'a Deploy Etme

### Adım 1: GitHub Repo Oluştur

1. GitHub'a git: https://github.com
2. "New repository" tıkla
3. Repository adı: `starlang-turkish-checker`
4. Public veya Private seç
5. "Create repository"

### Adım 2: Dosyaları GitHub'a Yükle

```bash
# Terminalde bu klasöre git
cd starlang-deployment

# Git başlat
git init

# Dosyaları ekle
git add .

# Commit et
git commit -m "Initial commit: Starlang Turkish spell checker service"

# GitHub'a bağla (kendi repo URL'in ile değiştir)
git remote add origin https://github.com/KULLANICI_ADIN/starlang-turkish-checker.git

# Push et
git branch -M main
git push -u origin main
```

### Adım 3: Render.com'da Deploy Et

1. https://render.com'a git
2. Sign up / Log in (GitHub ile giriş yapabilirsin)
3. Dashboard'da "New +" butonuna tıkla
4. "Web Service" seç
5. GitHub repo'nu bağla
6. Repo'yu seç: `starlang-turkish-checker`
7. Ayarları kontrol et:
   - **Name**: starlang-turkish-checker
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (başlangıç için)
8. "Create Web Service" tıkla
9. Deploy başlayacak (3-5 dakika)
10. Deploy bitince URL'i kopyala: `https://starlang-turkish-checker.onrender.com`

## ✅ Test Et

Deploy bittikten sonra:

```bash
# Health check
curl https://starlang-turkish-checker.onrender.com/health

# Test spell check
curl -X POST https://starlang-turkish-checker.onrender.com/check \
  -H "Content-Type: application/json" \
  -d '{"text": "kardesim nasılsın"}'
```

## 📝 Notlar

- **Free plan**: 15 dakika inactivity sonrası sleep mode'a girer
- **Paid plan ($7/ay)**: Always on, daha hızlı
- İlk istekler yavaş olabilir (cold start)
- Sonraki istekler hızlı olur

## 🔗 Sonraki Adım

Bu URL'i Supabase Edge Function'da kullan:

```typescript
const STARLANG_SERVICE_URL = "https://starlang-turkish-checker.onrender.com";
```
