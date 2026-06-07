---
name: Bug Report
about: Something broke
labels: bug
---

**Which module?**
[ ] Module A (Analyzer) [ ] Module B (Advisor) [ ] Module C (Knowledge) [ ] Sandbox

**Endpoint**
e.g. POST /v1/analyze/full

**Request body (redact any real images)**
```json

---

**File: `.github/ISSUE_TEMPLATE/feature_request.md`**
```markdown
---
name: Feature Request
about: New capability or improvement
labels: enhancement
---

**Which module does this affect?**
[ ] Module A [ ] Module B [ ] Module C [ ] Sandbox [ ] New module

**What problem does this solve?**

**Proposed solution**

**Does this require exposing any engine rendering logic?**
If yes, this request will be declined — the API boundary is fixed.

**Would you like to implement this yourself?**
[ ] Yes, I'll open a PR [ ] No, requesting for someone else
