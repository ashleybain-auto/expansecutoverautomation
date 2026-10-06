# Expanse Cutover Automation - CNET - UPDATED Canvas App Shell

**Source configuration:** `No CNET-specific source workbook supplied`
**Status:** shell prepared; CNET schema/config source not included in attached zips

## 1. What changed in this shell

- App title and domain/module text are set for **Expanse Cutover Automation - CNET**.
- Header shows configured source areas: **Schema binding required**.
- Search and facility filtering are part of the shell.
- Current/Proposed configuration, Action To Take, Save, Cancel, unsaved-change indicator, Target Match/Sync Check, and ECCS lineage are retained.
- The shell contains no CSV or source business-data rows.

## 2. Install the .msapp in DevelopmentAuto

1. Open the Power Apps maker portal and select the **DevelopmentAuto** environment.
2. Go to **Apps** and use **Import app > From file (.msapp)**.
3. Select the `.msapp` in this package.
4. After Studio loads the app, use **File > Save as** and retain the exact app name shown in `app-config.json`.
5. Open **Data** and remove/replace the starter `Accommodation Data Clone` source with the real domain Dataverse table/view.
6. Rebind the facility Combo box, gallery, Current Configuration fields, Proposed Configuration fields, Target Match, Action To Take, and ECCS lineage fields using `field-mapping-template.json`.
7. Update the `Patch()` object in the Save Configuration button to the real entity and Dataverse field types.
8. Test one record end-to-end, then run App Checker, Save, and Publish.

## 3. Attached-source configuration

- No app-specific worksheet was supplied for this module in the attached zips. Use the shell and complete schema binding when the module source is available.

## 4. Functional build formulas

### Facility Items

```powerfx
Replace FacilityMnem_Source with the domain facility field.
```

### Gallery Items

```powerfx
Replace the starter Accommodation Data Clone source with the domain table and apply the domain field mapping from this package.
```

### Save/Patch pattern

```powerfx
Patch the mapped target columns and Action To Take field using the real Dataverse type.
```

### Target Match / Sync rule

```powerfx
No target-match field was supplied; add the domain match field before enabling sync confirmation.
```

## 5. Acceptance checks

- Correct application title and module/domain.
- Correct facility list and filtering after real source rebinding.
- Search finds records by source mnemonic/name.
- Source values are read-only; proposed values are editable.
- Action To Take is selectable and persists with the record.
- Save marks the record updated and refreshes the gallery.
- Cancel restores the last committed values and clears the unsaved indicator.
- NO MATCH is red/bold and dated LIVE/TEST/ZCON matches invoke the synchronization prompt.
- ECCS lineage is traceable.
- App Checker has no new blocking errors.


## 6. Hub linkage artifacts
Use these files to connect this shell to the Registration POC hub and other modules:

- `canvas/module-registry.json` (central module registry with visibility rules and targets)
- `canvas/navigation-context.json` (shared launch payload + return path pattern)
- `canvas/MODULE-LINKAGE-MATRIX.md` (hub-to-module linkage matrix and test workflow)

For final integration, populate each module app ID through the referenced environment variables (for example `ECCS_APPID_CNET`) or replace `app_id_env_var` mappings with resolved app IDs, then complete Dataverse rebind checks before publishing.
