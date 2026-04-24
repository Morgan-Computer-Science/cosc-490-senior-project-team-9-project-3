# OCR Workflow Design

## Goal
Build a reusable OCR and document-understanding workflow that makes uploaded transcripts, degree audits, schedules, and screenshots more reliable and useful across both the profile import flow and advisor chat.

## Scope
This phase covers:
- shared backend document classification and extraction flow
- stronger OCR handling for images and scanned PDFs
- structured document result fields instead of ad hoc text-only handling
- frontend OCR preview in the profile/import workflow
- better chat grounding from the same structured document result

This phase does not cover:
- live Canvas or WebSIS integration
- perfect support for every document layout
- a full redesign of unrelated chat or profile logic

## Current State
The app already supports uploaded files in both advising chat and profile import. It can:
- extract text from plain text files
- extract text from some PDFs locally
- use Gemini for multimodal image/PDF handling
- infer course codes and some planning signals from extracted text

The main gaps are:
- document extraction logic is still spread across multiple flows
- OCR results are not exposed as one shared structured document model
- scanned PDFs and screenshots need a stronger, more explicit processing path
- the frontend import flow shows useful preview data, but it is not clearly framed as a document-analysis result with confidence and extraction status

## Architecture
Use one shared document-processing pipeline with three stages:

### 1. Classify
Given an uploaded file and any nearby question/source label, determine the likely document type:
- transcript
- degree audit
- schedule
- academic form
- screenshot/image
- generic document fallback

This should remain heuristic-driven for now, with Gemini-based help used in extraction rather than trying to solve classification with a separate model.

### 2. Extract
Run extraction in a layered order:
- plain text files: local decode first
- text-based PDFs: local PDF extraction first
- scanned PDFs and images: Gemini OCR / multimodal extraction fallback
- if extraction is weak, preserve that explicitly rather than pretending confidence

Extraction should return both raw text and metadata about how the text was obtained.

### 3. Interpret
Convert extracted text into advising-relevant structure:
- completed courses
n- planned/current courses
- remaining/needed courses
- document summary
- confidence / ambiguity note
- matched Morgan course codes
- unmatched course-like codes

This structured result becomes the shared contract used by profile import and chat.

## Shared Backend Result Model
Introduce a shared document analysis result that contains:
- detected document type
- extraction method used
- extracted text
- summary text for UI/chat context
- completed course codes
- planned/current course codes
- remaining/needed course codes
- matched Morgan course codes
- unknown/unmatched course codes
- confidence or extraction-status note

This model should sit beneath both:
- completed-course import preview
- chat attachment reasoning

That keeps document interpretation consistent across the product.

## Profile / Import Flow
The profile import workflow should use the shared document result directly.

Behavior:
- upload or paste source
- show detected type
- show extraction summary
- show confidence / ambiguity note if needed
- separate preview buckets:
  - completed
  - planned/current
  - remaining/needed
- only completed courses can be applied into tracked history

This keeps the import workflow trustworthy and easy to understand.

## Chat Flow
The chat workflow should use the same structured document result rather than only passing raw extracted text.

Behavior:
- uploaded document contributes extracted text plus structured advising signals
- advisor can answer questions about a transcript, degree audit, or schedule using the same interpretation logic as the profile flow
- if extraction is weak, the reply should say that clearly

This improves reliability and reduces duplicated logic.

## UI Expectations
The UI should feel like a product workflow, not a debug panel.

In the import flow, show:
- detected document type
- concise extraction summary
- confidence note only when relevant
- completed / planned / remaining buckets
- clear apply and clear actions

In chat, keep the conversation clean.
- do not expose internal debug metadata under every message
- attachment-specific guidance should happen before send or inside the advisor’s actual response

## Error Handling
The OCR workflow should be explicit when it is uncertain.

Expected behavior:
- unsupported files are rejected cleanly
- unclear OCR results produce a confidence note or warning
- low-confidence extraction should not auto-claim academic facts
- the system should guide the student to verify key requirements when the document is unclear

## Success Criteria
This phase is successful when:
- document extraction is handled through one shared backend workflow
- screenshots and scanned PDFs have a stronger OCR path
- profile import preview is driven by the shared structured document result
- chat uses the same structured document interpretation
- the app clearly communicates when OCR/document interpretation is uncertain
