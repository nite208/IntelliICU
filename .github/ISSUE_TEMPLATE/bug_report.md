name: 🐛 Bug Report
description: Report a bug or issue in IntelliICU.
title: "[BUG] <Short description of the bug>"
labels: [bug, unconfirmed]
assignees: []
body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug. Please fill in the details below to help us reproduce and resolve the issue.
  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe the bug clearly and concisely.
      placeholder: What goes wrong?
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Explain the steps to reproduce the behavior.
      placeholder: |
        1. Login as 'Miller' (doctor)
        2. Navigate to 'Patients'
        3. Click on 'ICU-10248'
        4. See error in console
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What did you expect to happen?
      placeholder: Telemetry sparklines should start updating.
    validations:
      required: true
  - type: dropdown
    id: environment
    attributes:
      label: Environment
      options:
        - Local Development (Vite + Uvicorn)
        - Production Deployment (Vercel + Render)
        - Docker Compose Sandbox
    validations:
      required: true
