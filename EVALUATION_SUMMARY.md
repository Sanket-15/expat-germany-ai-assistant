# Evaluation Summary

## Goal

The goal of this evaluation is to test whether the Expat Germany AI Assistant gives useful, grounded, multilingual, and safe answers for common expat questions in Germany.

## What Was Tested

The evaluation covers:

- EU Blue Card and residence permit questions
- Anmeldung and Tax ID questions
- housing and renting questions
- health insurance and Kindergeld questions
- German-to-English translation
- polite German reply drafting
- live/current-data questions such as weather
- high-risk legal and financial questions

## Evaluation Checks

`eval_runner.py` checks:

- whether an answer was generated
- whether factual RAG questions include sources
- whether translation and drafting tasks bypass RAG
- whether unsupported or high-risk questions trigger safe fallback responses
- whether answer language matches the user query
- whether possible hallucination risk is detected

## Improvements Made

Based on evaluation results, the assistant was improved to:

- answer English questions in English and German questions in German
- bypass RAG for translation, short explanation, greetings, and drafting tasks
- show sources only for factual RAG answers
- improve fallback responses for legal, financial, and live/current-data questions
- capture evaluation results in a CSV file

## Result

The assistant now handles factual Germany-related questions with source-grounded answers, avoids unnecessary retrieval for translation and drafting, and gives safer fallback responses for unsupported or high-risk questions.

## How to Run Evaluation

```bash
python eval_runner.py
```
