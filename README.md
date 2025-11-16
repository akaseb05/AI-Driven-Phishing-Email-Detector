# AI-Driven-Phishing-Email-Detector
An intelligent phishing-detection engine that analyzes email content + metadata to estimate risk and explain why.

🔍 Overview

This project is an early-stage prototype of an AI-powered phishing detection system.
It takes in email text + metadata and outputs:

A phishing probability score (0–100%)

A breakdown of factors influencing the score

A short explanation summarizing the reasoning

Right now the project uses rule-based scoring, with plans to integrate:

Large Language Model (LLM) social-engineering detection

Classical ML for link + domain reputation analysis

IMAP/SMTP email ingestion

User-friendly dashboard + API endpoints

This repository is still in development — core features are being added piece by piece.
