# **AI-Driven Phishing Email Detector (WIP)**

### **Status:** 🚧 *In Development*

### **Goal:** Build an intelligent phishing-detection engine that analyzes email content and metadata to estimate risk and explain why.

---

## 🔍 **Overview**

This project is an early-stage prototype of an **AI-powered phishing detection system**. It accepts email text + metadata and outputs:

* A **phishing probability score** (0–100%)
* A factor breakdown (sender, CC list, language, links)
* A clear explanation summarizing why the email looks suspicious or safe

Right now, the system uses rule-based analysis. The plan is to integrate:

* LLM-based social-engineering detection
* ML classification for domain/link patterns
* IMAP integration to scan real inboxes
* A dashboard for end-users

This repo reflects ongoing development.

---

## ✨ **What’s Working Right Now**

* FastAPI backend with one endpoint: `/classify-email`
* Rule-based scoring system:

  * Sender domain consistency
  * Suspicious CC domain spread
  * Content-based red flags
  * URL and link analysis
* Automatic probability calculation and explanation text

---

## 🧠 **How the Current Engine Works**

The system calculates four main scores:

**1. Sender Score**
Checks how trustworthy the sender domain looks relative to recipients.

**2. Link Score**
Flags risky URLs, IP-based links, unusual structures.

**3. CC Anomaly Score**
Detects weird CC patterns (domains that shouldn’t be there, too many unrelated domains).

**4. Content Score**
Analyzes urgency markers, scam phrases, excessive caps, suspicious language.

Scores are weighted and combined into a final phishing probability.

---

## 🚀 **Run Locally**

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open:

```
http://127.0.0.1:8000/docs
```

Use the built-in API Explorer to test emails.

---

## 📌 **Why This Project Matters**

Phishing is still the #1 cybersecurity attack vector.

Most tools only check technical indicators.
This project focuses on **behavioral + linguistic patterns**, combining:

* NLP
* Email protocol handling
* Security threat modeling
* AI risk scoring

---
