# References and verification record

Single source of truth for every work cited in `docs/project_proposal.md`. Numbering
matches the citation numbers used in that document.

**Verification rule applied.** A source counts as verified only if its full text or
landing page was retrieved and read during preparation. Nothing in this project is cited
from memory or from a title alone, with one declared exception ([8], recorded below as
*secondary*). Sources that could not be retrieved were dropped and are listed in
section 3.

**Verification date:** 8 October 2026.
**Method:** direct HTTP retrieval, with PDFs converted to text and read. The session's
web tooling was unavailable, so retrieval used `curl` and `pdftotext`.

---

## 1. Cited sources

| # | Work | Type | Verified | What was read |
|---|---|---|---|---|
| [1] | Stouffer et al., *Guide to Operational Technology (OT) Security*, NIST SP 800-82 Rev. 3, September 2023. doi:10.6028/NIST.SP.800-82r3 | Standard / guidance | **Yes — primary** | Landing page (title, revision, date, authors, DOI) and the full publication PDF converted to text, 16,224 lines |
| [2] | Chan and Zhou, "Toward Safe Integration of Legacy SCADA Systems in the Smart Grid", arXiv:2107.05863 | Research survey | **Yes — primary** | Full text via ar5iv |
| [3] | Tsang and Smith, "YASIR: A Low-Latency, High-Integrity Security Retrofit for Legacy SCADA Systems", IFIP TC 11 23rd Int. Information Security Conf., vol. 278, Springer, 2008, pp. 445–459 | Research | **Yes — primary** | Full PDF converted to text, 755 lines |
| [4] | Kaniewski, Lohmiller, Menth and Heer, "Securing The Forgotten Link: Selecting and Evaluating Compensating Security Measures for Legacy Device Integration Paths", accepted for ARES, Linköping | Research | **Yes — primary** | Full accepted-manuscript PDF converted to text, 1,196 lines |
| [5] | CISA, *Cyber-Attack Against Ukrainian Critical Infrastructure*, Alert IR-ALERT-H-16-056-01, updated 20 July 2021 | Government incident report | **Yes — primary** | Full alert text, including Summary, Details, Mitigation and Detection sections |
| [6] | IEC TS 62351-1:2007, *Power systems management and associated information exchange — Data and communications security — Part 1* | Standard | **Yes — primary (abstract/scope page)** | IEC webstore page: full title, designation, and the scope statement naming IEC TC 57 protocol families |
| [7] | IEEE Std 1815-2012, *IEEE Standard for Electric Power Systems Communications — Distributed Network Protocol (DNP3)* | Standard | **Yes — primary (landing page)** | IEEE SA page: designation, full title, supersession of 1815-2010. Corroborated by [1] Appendix D |
| [8] | IEEE Std 1711.1 (SSPP) and IEEE Std 1711.2-2019 (SSCP) | Standard | **Secondary only** | Titles and designations read from the standards list in [1], Appendix D. The IEEE pages are JavaScript-rendered and returned no content; the standards are paywalled. See `TODO(team)` T8 |
| [9] | Solomakhin, Tsang and Smith, "Predictive YASIR: High Security with Lower Latency in Legacy SCADA" | Research | **Yes — primary (author-hosted draft)** | Full PDF converted to text, 894 lines. Note: draft version; see `TODO(team)` T13 |
| [10] | U.S. DOE CESER, *Hallmark Cryptographic Serial Communication* fact sheet (SEL, PNNL, CenterPoint Energy) | Government / commercial | **Yes — primary** | Full PDF converted to text, 104 lines |
| [11] | Jackson, "Encryption device planned for legacy SCADA installations", *Washington Technology*, January 2005 | Trade press | **Yes — primary** | Full article text. Note: journalistic announcement, not a datasheet; see `TODO(team)` T11 |
| [12] | Nguyen, Dai, Le, Huynh and Pham, "Embedding the Real-Time AES-128 Encryption into Programmable Logic Controllers for Secure Modbus TCP/IP Communications in Industrial Control Systems", *Int. J. Integrated Engineering*, 17(9), 45–57, 2025 | Research | **Yes — primary (abstract page)** | Journal landing page: full title, authors, volume, issue, pages, publication date, and complete abstract with the reported measurements |
| [13] | Bhamare, Zolanvari, Erbad, Jain, Khan and Meskin, "Cybersecurity for Industrial Control Systems: A Survey", arXiv:2002.04124, 10 February 2020 | Research survey | **Yes — primary (abstract page)** | arXiv abstract page: title, all six authors, submission date, complete abstract |
| [14] | DNP Users Group, *Overview of DNP3 Protocol* and *Features of DNP3* | Standards body page | **Yes — primary** | Both pages: DNP3 origin, transfer to the DNP Users Group in November 1993, adoption as IEEE Std 1815 in 2010, the documentation set including secure authentication, and the published feature list (which does not name message encryption) |
| [15] | NIST, *Advanced Encryption Standard (AES)*, FIPS 197, 26 November 2001, updated 9 May 2023 | Standard | **Yes — primary (abstract/metadata page)** | CSRC page: title, designation, publication and update dates, author (NIST), abstract describing selection of the Rijndael family |
| [16] | M. Dworkin, *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*, NIST SP 800-38D, November 2007 | Standard | **Yes — primary** | CSRC page (title, date, author Morris Dworkin, abstract) **and the full publication PDF**, specifically Sec. 5.2.1.1 on the 96-bit IV recommendation, Sec. 8 on the uniqueness requirement, and the caution in Sec. 3 |

### Links

| # | URL |
|---|---|
| [1] | https://csrc.nist.gov/pubs/sp/800/82/r3/final — PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf |
| [2] | https://ar5iv.arxiv.org/html/2107.05863 |
| [3] | https://www.cs.dartmouth.edu/~sws/pubs/yasir-sec08.pdf |
| [4] | https://atlas.cs.uni-tuebingen.de/~menth/papers/Menth26i.pdf |
| [5] | https://www.cisa.gov/news-events/ics-alerts/ir-alert-h-16-056-01 |
| [6] | https://webstore.iec.ch/publication/6903 |
| [7] | https://standards.ieee.org/ieee/1815/5414/ |
| [8] | Via [1], Appendix D. IEEE pages: https://standards.ieee.org/ieee/1711.2/6321/ (no readable content) |
| [9] | https://cs.dartmouth.edu/~sws/pubs/sts10-draft.pdf |
| [10] | https://www.energy.gov/documents/hallmark-cryptographic-serial-communication-schweitzer-engineering-laboratories |
| [11] | https://washingtontechnology.com/2005/01/encryption-device-planned-for-legacy-scada-installations/328769 |
| [12] | https://journal.uthm.edu.my/index.php/ijie/article/view/22589 |
| [13] | https://arxiv.org/abs/2002.04124 |
| [14] | https://www.dnp.org/About/Overview-of-DNP3-Protocol and https://www.dnp.org/About/Features-of-DNP3 |
| [15] | https://csrc.nist.gov/pubs/fips/197/final |
| [16] | https://csrc.nist.gov/pubs/sp/800/38/d/final — PDF: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf |

---

## 2. Corrections made to the project brief during verification

The brief in `README_to snd.md` listed starting sources to verify. Four descriptions
needed correcting once the documents were opened.

| Item as given in the brief | Correction after reading the source |
|---|---|
| "Evaluating Compensating Security Measures for Legacy Device Integration Paths (Univ. of Tübingen)" | Full title is "Securing The Forgotten Link: Selecting and Evaluating Compensating Security Measures for Legacy Device Integration Paths". Three of the four authors are at Esslingen University; Menth is at Tübingen [4] |
| "IEEE 1711" as a single standard | A family. IEEE Std 1711.1 is the Substation Serial Protection Protocol (SSPP); IEEE Std 1711.2-2019 is the Secure SCADA Communications Protocol (SSCP) [1], [8] |
| "IEC 62351" as applicable to Modbus and DNP3 | The series targets protocols defined by IEC TC 57 — the IEC 60870-5, 60870-6, 61850, 61970 and 61968 series. **Modbus is not in that scope** [6] |
| "Hallmark Project and SEL-3025 link module" | Correct, and the fact sheet additionally names the SEL-3045 cryptographic card and identifies SSCP as the protocol, which connects this product line to IEEE Std 1711.2 [10] |

The brief also named **Stuxnet (2010)** as an incident to cite. It is **not cited**. No
primary source was retrievable, and its mechanism — manipulation of PLC logic via
engineering workstations — is not the telemetry-interception problem this project
studies. Recorded as `TODO(team)` T4.

---

## 3. Sources dropped: could not be opened

Per the project rule that nothing unverified may be cited, the following are absent from
the proposal entirely.

| Work | Source given | Result | Consequence |
|---|---|---|---|
| "Securing Modbus in legacy ICS using proxies" (University of Messina) | https://iris.unime.it/handle/11570/3339492 | **HTTP 403 Forbidden**, including after disabling TLS revocation checking | The proxy-based category in B.3 rests on an analysis [4] rather than an implementation. `TODO(team)` T10 |
| Modbus/TCP Security specification (Modbus Organization) | https://modbus.org/docs/MB-TCP-Security-v21_2018-07-24.pdf | **HTTP 404**, on both the bare and `www` hosts. The specification index at https://modbus.org/specifications/ returns HTTP 200 but is JavaScript-rendered and exposes no retrievable document link; https://modbus.org/tech.php returns HTTP 403 | The claim that Modbus carries no security rests on secondary sources [1], [2], [3] rather than the specification. `TODO(team)` T3 |
| IEEE Std 1711.1 and 1711.2-2019, full text | https://standards.ieee.org/ieee/1711.2/6321/ and /1711.2/7174/ | Pages are JavaScript-rendered; raw retrieval returned unrelated catalogue text about ISO/IEC/IEEE 15288 and 12207. Standards themselves are paywalled | Cited at title level via [1] only, and marked "not verified in this review" in the B.5 comparison table. `TODO(team)` T8 |
| Maroochy Shire incident report (MITRE) | https://www.mitre.org/sites/default/files/pdf/08_1145.pdf | **Access Denied** at the CDN | The 2001 Australian sewage incident is cited instead through [3], which reports it directly |

---

## 4. Additional source added beyond the brief

The brief asked for at least two further verified sources, preferably one standard and
one recent survey.

| Work | Category | Why added |
|---|---|---|
| [13] Bhamare et al., "Cybersecurity for Industrial Control Systems: A Survey", 2020 | Recent survey | Satisfies the requirement for a survey from 2020 or later that was actually opened. Located through the arXiv API and read in full abstract form. Corroborates the isolation-to-convergence trend in A.1.5 |
| [14] DNP Users Group, *Overview of DNP3 Protocol* | Standards body | Confirms DNP3's adoption as IEEE Std 1815 and the existence of secure authentication in the DNP3 documentation set, which the IEEE page alone did not establish |

Note on counting: [6] IEC TS 62351-1, [7] IEEE 1815 and [14] are standards-side sources
added and verified beyond the brief's research list; [13] is the recent survey.
