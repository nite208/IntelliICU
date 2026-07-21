name: 💡 Feature Request
description: Propose a new feature or enhancement for IntelliICU.
title: "[FEATURE] <Short summary of the feature>"
labels: [enhancement, discussion]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a feature. We design IntelliICU to emulate clinical workflows cleanly.
  - type: textarea
    id: problem
    attributes:
      label: Problem Statement
      description: Is your feature request related to a problem? Please describe.
      placeholder: It's frustrating when we cannot filter alerts by patient name...
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: Describe the solution or enhancement you'd like to see.
      placeholder: Add a Search Patients input box inside the alerts section...
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: Describe any alternative solutions or workarounds you've considered.
      placeholder: Checking patient details separately on the Patients panel.
    validations:
      required: false
