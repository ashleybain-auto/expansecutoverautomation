# ECCS Hub Module Linkage Matrix

Hub app: `canvas/ECCS - Registration POC.msapp`
Hub screen: `scrModuleHub`

| Module key | Module name | Launch mode | Hub target | Landing screen | Required params |
| --- | --- | --- | --- | --- | --- |
| registration_core | Registration Core | Screen (same app) | `scrRegistrationCore` | `scrRegistrationCore` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| cnet | CNET | App deep link | `ECCS_APPID_CNET` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| emergency_department | Emergency Department | App deep link | `ECCS_APPID_EMERGENCY_DEPARTMENT` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| mis_provider | MIS Provider | App deep link | `ECCS_APPID_MIS_PROVIDER` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_consults | Non-Med Consults | App deep link | `ECCS_APPID_NON_MED_CONSULTS` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_diet | Non-Med Diet | App deep link | `ECCS_APPID_NON_MED_DIET` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_ekg | Non-Med EKG | App deep link | `ECCS_APPID_NON_MED_EKG` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_level_of_care | Non-Med Level of Care | App deep link | `ECCS_APPID_NON_MED_LEVEL_OF_CARE` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_nursing | Non-Med Nursing | App deep link | `ECCS_APPID_NON_MED_NURSING` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_oe | Non-Med OE | App deep link | `ECCS_APPID_NON_MED_OE` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_rad | Non-Med RAD | App deep link | `ECCS_APPID_NON_MED_RAD` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| non_med_rt_pt_ot | Non-Med RT/PT/OT | App deep link | `ECCS_APPID_NON_MED_RT_PT_OT` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |
| registration_ptac | Registration PTAC | App deep link | `ECCS_APPID_REGISTRATION_PTAC` | `scrModuleMain` | targetModuleKey, facility, recordKey, targetEnvironment, sourceScreen, searchText |

## Return path standard

- In-app modules: `Navigate(hubScreenObject, ScreenTransition.None, varNavContext)` to guarantee return to hub with preserved context.
- External modules: return with a launch URL to the hub app and include `hubScreen=scrModuleHub`, `targetModuleKey`, `facility`, `recordKey`, `targetEnvironment`, `sourceScreen`, `searchText`, and optional `returnRecordKey` (override key), `returnToast`, `moduleScreen`, and `launchUtc` query parameters.
- Hydration entry point: App `OnStart` parses params into `varNavContext`; `scrModuleHub.OnVisible` reapplies facility filter, selected record, and search text.

## Validation execution log template

Run one pass for each module:

1. Select a facility and search value on `scrModuleHub`.
2. Launch module target from registry-driven control.
3. Confirm landing screen and context hydration.
4. Modify one record and save against module Dataverse table.
5. Return to hub and confirm facility/search/record state are preserved.
6. Record result as PASS/FAIL with notes.
