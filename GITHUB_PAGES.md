# نشر الموقع على GitHub Pages (github.io)

## 1) تثبيت Git (مرة واحدة)

حمّل **Git for Windows** : https://git-scm.com/download/win  
ثم أعد فتح Cursor / Terminal.

## 2) إنشاء مستودع على GitHub

1. ادخل https://github.com/new  
2. اسم المستودع مثلاً : `nephro-qcm` (أو أي اسم)  
3. **Public** (Pages مجاني للم repos العامة)  
4. لا تضف README إذا سترفع المشروع من جهازك  

## 3) رفع المشروع من PowerShell

```powershell
cd C:\Users\AymenZ97\Desktop\QCMapp
git init -b main
git add .
git commit -m "Néphro QCM Coach — PWA + banque QCM"
git remote add origin https://github.com/VOTRE_USER/nephro-qcm.git
git push -u origin main
```

(استبدل `VOTRE_USER` واسم الم repo.)

## 4) تفعيل GitHub Pages

1. Repo → **Settings** → **Pages**  
2. **Build and deployment** → Source : **GitHub Actions**  
3. بعد أول `push`، workflow **Deploy to GitHub Pages** يعمل تلقائياً  
4. انتظر 1–3 دقائق → الرابط يظهر في **Settings → Pages**

## الرابط على الهاتف

```
https://ChihabZeroual.github.io/nephro-qcm/
```

(إذا اسم الم repo مختلف، غيّر `nephro-qcm`.)

## تثبيت كتطبيق على الهاتف

Safari / Chrome → **Ajouter à l'écran d'accueil** (PWA).

## ملاحظات

- التقدم (localStorage) يبقى **على كل جهاز** منفصلاً.  
- الملف `app/data/questions.json` (~2.5 Mo) يُرفع مع المشروع.  
- الـ PDFs في المجلد الرئيسي **اختيارية** للموقع (الموقع يعمل بدونها).
