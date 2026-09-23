# Unit 3: System Requirements and Design

## Architecture

Three layers, four modules. See `design/figure1-system-architecture.png`.

- **Presentation layer**, participant interface and administrator interface.
- **Application layer**, M1 Training Delivery, M2 Assessment Collection, M4 Analysis and
  Reporting.
- **Data layer**, M3 Data Storage and Security, holding the content repository and the
  assessment data store.

Security and privacy controls apply across all three layers rather than inside one module,
because consent, participant IDs, encryption, and least privilege each apply at a
different point in the flow (Letaw, 2024).

## Module specifications

| Module | Input | Output | Method |
| --- | --- | --- | --- |
| M1 Training Delivery | Training content and mock email examples | Completed session and completion record | Worked examples of the five indicators, then verification and reporting |
| M2 Assessment Collection | Assessment items and participant answers | Scored records tagged by item and indicator | Matched 20-item pre- and post-test, half knowledge and half scenario |
| M3 Data Storage and Security | Response records from M2, content files | Encrypted, ID-keyed records for M4 | ID substitution, encrypted storage, least-privilege access |
| M4 Analysis and Reporting | Paired pre- and post-test records | Six metrics, charts, final report | Score comparison, per-indicator accuracy, false alarm rate |

## Functional requirements

1. **FR1** Assign each participant a numeric ID at enrolment and record consent before any
   assessment item is shown.
2. **FR2** Deliver a 20-item pre-training assessment of 10 knowledge and 10 scenario
   questions.
3. **FR3** Present a training module covering all five indicators plus verification and
   reporting steps.
4. **FR4** Deliver a post-training assessment matching the pre-test in length, difficulty,
   and indicator coverage.
5. **FR5** Record, for every scenario item, both the classification chosen and the action
   selected.
6. **FR6** Key all responses by participant ID and reject any response file containing a
   name or email address.
7. **FR7** Calculate the six evaluation metrics and compare them against the success
   criteria.
8. **FR8** Produce a results summary with charts reporting accuracy for each indicator.

FR5 is separate from FR2 because a participant can correctly identify a message as
phishing and still choose an unsafe action with it.

## Non-functional requirements

Categories follow ISO/IEC 25010 (International Organization for Standardization, 2023).

| ID | Category | Requirement |
| --- | --- | --- |
| NFR1 | Security | Encrypted storage, least-privilege access per NIST SP 800-53 |
| NFR2 | Privacy | No name stored with any score; all data deleted after the final report |
| NFR3 | Usability | About 30 minutes, usable with no security background |
| NFR4 | Reliability | Same input returns the same result; covered by automated tests |
| NFR5 | Safety | No working link, live attachment, or credential form in any mock message |
| NFR6 | Scalability | Supports a larger group without redesign |

NFR5 is a safety requirement rather than a security requirement because the risk it
controls is harm to the participant during the training itself.

## Data flow

See `design/figure2-data-flow-diagram.png`. The order is fixed: enrolment, pre-assessment,
training, post-assessment, analysis. The pre-test must be completed before any training
content is shown, or the baseline is lost.
