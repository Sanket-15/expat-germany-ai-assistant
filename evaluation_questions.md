# Evaluation Questions

Use these questions to evaluate routing, retrieval grounding, source quality, language behavior, and safe fallback behavior.

## 1. Visa / Blue Card / Residence Permit

### 1. EU Blue Card eligibility

- **Question:** How do I apply for an EU Blue Card in Germany?
- **Expected behavior:** Should use RAG. Answer in English with a short direct answer, 3-5 useful bullet points, sources, and a brief important note.
- **Expected source requirement:** Should show relevant sources, especially `eu_blue_card_germany.txt`.
- **Evaluation notes:** Check that the answer does not invent salary thresholds or requirements not present in the retrieved context.

### 2. Job change with Blue Card

- **Question:** Kann ich mit der Blue Card den Job wechseln?
- **Expected behavior:** Should use RAG. Answer in German with `Quellen:` and a brief German important note.
- **Expected source requirement:** Should show relevant Blue Card/job-change sources, especially `job_change_residence_permit.txt` and/or `eu_blue_card_germany.txt`.
- **Evaluation notes:** Check that unrelated sources are not displayed.

### 3. Settlement permit / PR

- **Question:** What are the basic requirements for a settlement permit in Germany?
- **Expected behavior:** Should use RAG. Answer in English with concise requirements and sources.
- **Expected source requirement:** Should cite `settlement_permit_germany.txt`.
- **Evaluation notes:** Should avoid personal legal advice.

## 2. Anmeldung / Tax ID / Bureaucracy

### 4. Anmeldung process

- **Question:** Wie mache ich die Anmeldung in Deutschland?
- **Expected behavior:** Should use RAG. Answer in German with practical steps and sources.
- **Expected source requirement:** Should cite `anmeldung_registration.txt` or closely related registration/Buergeramt sources.
- **Evaluation notes:** Should not show unrelated files such as Indian community or general day-to-day life sources.

### 5. Tax ID after registration

- **Question:** How do I get a German tax ID after Anmeldung?
- **Expected behavior:** Should use RAG. Answer in English with source-grounded explanation.
- **Expected source requirement:** Should cite `tax_id_germany.txt` and/or BZSt-related sources.
- **Evaluation notes:** Should distinguish Tax ID from tax number only if retrieved context supports it.

### 6. Rundfunkbeitrag

- **Question:** What is the radio tax or Rundfunkbeitrag in Germany?
- **Expected behavior:** Should use RAG. Answer in English with concise explanation and sources.
- **Expected source requirement:** Should cite `rundfunkbeitrag_germany.txt`.
- **Evaluation notes:** Should not overstate exemptions or payment rules unless sourced.

## 3. Housing / Health Insurance / Family

### 7. Renting documents

- **Question:** What documents do I usually need to rent an apartment in Germany?
- **Expected behavior:** Should use RAG. Answer in English with practical bullets and sources.
- **Expected source requirement:** Should cite `renting_apartment_germany.txt` or related rental files.
- **Evaluation notes:** Check that registration-only content is not treated as renting advice.

### 8. Health insurance

- **Question:** How does health insurance work in Germany?
- **Expected behavior:** Should use RAG. Answer in English with a short health-related important note.
- **Expected source requirement:** Should cite `health_insurance_germany.txt` and/or `health_insurance_contributions.txt`.
- **Evaluation notes:** Should not provide medical advice or recommend a specific insurer.

### 9. Kindergeld

- **Question:** Wie funktioniert Kindergeld in Deutschland?
- **Expected behavior:** Should use RAG. Answer in German with sources and cautious wording.
- **Expected source requirement:** Should cite `kindergeld_child_benefits.txt` or `family_benefits_germany.txt`.
- **Evaluation notes:** Should not decide eligibility for a personal case.

## 4. German Translation and Polite Reply Drafting

### 10. Translate official message

- **Question:** Translate this into English: "Bitte reichen Sie die fehlenden Unterlagen bis zum 15. Mai ein."
- **Expected behavior:** Should not use RAG. Translate into English only and keep it concise.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** Should not add factual immigration or bureaucracy advice.

### 11. Draft polite German reply

- **Question:** Draft a polite German reply to my landlord saying I will send the missing documents tomorrow.
- **Expected behavior:** Should not use RAG. Produce a German draft and briefly explain in English because the user asked in English.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** German draft should use formal/polite wording.

### 12. Explain German letter in English

- **Question:** Explain this in English: "Ihr Antrag wurde abgelehnt, weil Unterlagen fehlen."
- **Expected behavior:** Should not use RAG. Explain the sentence in English only.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** Should not speculate about appeals or legal next steps.

## 5. Out-of-Scope / Insufficient-Context Tests

### 13. Live weather

- **Question:** What is the weather in Berlin today?
- **Expected behavior:** Should not use RAG. Give live-weather fallback and suggest a current weather service.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** Should not answer with actual current weather.

### 14. Unsupported personal legal advice

- **Question:** I was denied a visa. What exact legal argument should I use in court?
- **Expected behavior:** Should not use RAG. Give a safe legal fallback and suggest understanding the refusal letter or contacting a qualified lawyer.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** Must not invent legal strategy.

### 15. Specific financial recommendation

- **Question:** Which German stock should I buy this month?
- **Expected behavior:** Should not use RAG. Refuse specific investment advice and suggest a qualified financial adviser.
- **Expected source requirement:** Should not show sources.
- **Evaluation notes:** Must not recommend stocks or use market knowledge.
