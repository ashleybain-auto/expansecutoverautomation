# Functional Build - Expanse Cutover Automation - CNET

Source: `No CNET-specific source workbook supplied`

## Common functions

- single-select facility filtering
- text search against source mnemonic and source description/name
- results gallery with selected-record state
- current source configuration display
- proposed target configuration using Classic/TextInput@2.3.2
- Action To Take selector
- unsaved-change detection, Save and Cancel/Revert workflow
- Patch + Refresh save pattern with update user/date-time capture
- Target Match NO MATCH red/bold warning treatment
- active-environment sync confirmation for LIVE/TEST/ZCON dated matches
- ECCS lineage display retained from the Registration POC shell

## Source-specific configuration

- Schema-specific source not supplied; bind when available.


## Hub linkage behavior
- Module launch controls should bind to `canvas/module-registry.json` for target routing.
- Launch payload should follow `canvas/navigation-context.json` required fields.
- Return-to-hub path must preserve facility/search/record selection state.
