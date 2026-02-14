IRCTC Conversational IVR Modernization Framework

Project Overview
This repository serves as the central hub for the modernization of the Indian Railways (IRCTC) Interactive Voice Response (IVR) system. The project focuses on transitioning from legacy, hardware-dependent telephony into a cloud-native, AI-driven conversational experience.
The framework replaces rigid, DTMF-based "Press-1" menus with a fluid, intent-driven Natural Language Understanding (NLU) interface powered by Amazon Connect Streams (ACS) and BAP AI.

Repository Structure
This repository is organized into modular directories to track the project's evolution from analysis to deployment:

Milestone 1/: Legacy System Analysis, Requirements Gathering, and Integration Strategy.

README.md: Project overview and documentation guide (this file).

MIT Licence.txt

Technology Stack (Subject to Change)
The project bridges the gap between traditional telecommunication standards and modern cloud architecture:

Legacy Infrastructure: Dialogic Telephony Cards, E1/PRI interfaces, VoiceXML (VXML) 2.0, EJB/JSP.

Modern Cloud Stack: Amazon Connect (ACS), BAP AI / Amazon Lex (NLU), AWS Lambda.

Security & Connectivity: VPC PrivateLink, PII Redaction, and Encrypted VPN Tunnels.

Strategic Goals
Elastic Scalability: Replacing hardware-capped physical ports with virtual cloud capacity to handle high-concurrency "Tatkal" booking surges.

Logic Translation: Moving from "Hard Logic" state machines to dynamic intent recognition that understands natural human speech.

Data Sovereignty: Preventing the leakage of sensitive Passenger Name Record (PNR) data through secure hybrid cloud integration.

Sentiment Awareness: Utilizing AI to identify frustrated callers and providing automated escalation to human agents.

Documentation Highlights
The documentation included in this framework covers:

Current State Assessment: An audit of the "Exit System" architecture and its performance limitations.

Integration Strategy: A detailed look at the modern workflow replacement of the "Convolutional Loop."

Gap Analysis: Identification of technical hazards and the custom development needed to resolve them.
