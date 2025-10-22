# Starlang Turkish Spell Checker - Railway Deployment

## 🚂 Railway.app ile Deploy

Railway, Render'dan farklı olarak GitHub repo'larına tam erişebilir.
Starlang kütüphaneleri sorunsuz kurulur!

## 📁 Dosyalar

- `main.py` - FastAPI service
- `requirements.txt` - Starlang + bağımlılıklar
- `Procfile` - Railway start command
- `README.md` - Bu dosya

## 🚀 Hızlı Deploy

### 1. GitHub'a Yükle

Bu dosyaları GitHub repo'na yükle:
```
itektr/gcext
```

### 2. Railway'de Deploy

1. https://railway.app → New Project
2. Deploy from GitHub repo
3. `itektr/gcext` seç
4. Otomatik deploy başlar

### 3. Test Et

```bash
curl https://YOUR-SERVICE.up.railway.app/health
```

## 📖 Detaylı Rehber

Tüm adımlar için:
**RAILWAY-DEPLOYMENT.md** dosyasını oku

## ⚡ Önemli

- ✅ Procfile mutlaka olmalı
- ✅ requirements.txt güncel olmalı
- ✅ Python 3.11 kullan
- ✅ Build süresi: ~5-8 dakika

## 💰 Maliyet

- Free: $5 credit (ilk ay)
- Hobby: $5/ay (production)

## 🎯 Sonuç

Railway URL:
```
https://gcext-production.up.railway.app
```

Bu URL'i Supabase Edge Function'a ekle!
