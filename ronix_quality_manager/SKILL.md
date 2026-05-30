---
name: ronix-quality-manager-addon
description: Use when developing, extending, debugging, or reviewing the ronix_quality_manager Odoo 18 addon. Covers this module's real architecture, model/view/controller/security map, and a token-efficient workflow for making fast, safe changes with minimal back-and-forth.
---

# Ronix Quality Manager Addon

## Purpose

Work inside `ronix_quality_manager` with minimal token usage and minimal re-discovery.
Do not re-scan the whole addon unless the task touches a new area.

## Fast Start

1. Read `__manifest__.py`.
2. Open only the files in the touched flow:
   - model: `models/*.py`
   - backend view/action/menu: `views/*.xml`
   - security: `security/*.xml`, `security/ir.model.access.csv`
   - website/public route: `controllers/*.py`, `views/ronix_quality_website_pages.xml`, `views/snippets/*.xml`
   - report: `report/*.xml`
   - frontend asset: `static/src/js/*`, `static/src/scss/*`
3. Change the smallest set of files possible.
4. Re-check manifest load order only if new XML/data/security/report files are added.

## Module Architecture

This addon is a multi-feature quality portal built on `base` + `website`.
It has 4 main layers:

1. Backend management models and forms
2. Website/public pages and attachment delivery
3. Mobile-app style JSON/http endpoints
4. One printable operational nonconformity report

## Canonical File Map

### Core Python models

- `models/ronix_quality_location.py`: location master data and manager scoping anchor
- `models/ronix_quality_button.py`: mobile menu buttons tied to locations
- `models/ronix_quality_information.py`: information records and attachments
- `models/ronix_quality_announcement.py`: announcements
- `models/ronix_quality_training.py`: trainings and attachments
- `models/ronix_quality_audit_checklist.py`: audit groups and items
- `models/ronix_quality_operational_nonconformity.py`: operational nonconformity records and report helpers

### Controllers

- `controllers/mobile_app.py`: public mobile JSON endpoints and icon delivery
- `controllers/information.py`: public information attachment/file access
- `controllers/announcement.py`: public announcement detail route
- `controllers/training.py`: public training attachment download/preview

### XML/UI

- `views/menus.xml`: root menu and feature entry points
- `views/ronix_quality_*_views.xml`: backend list/form/search/action definitions per feature
- `views/ronix_quality_website_pages.xml`: website pages
- `views/snippets/*.xml`: website builder snippets
- `views/ronix_quality_vapi_templates.xml`: template layer for VAPI-related UI

### Security

- `security/ronix_quality_security.xml`: groups and record rules
- `security/ir.model.access.csv`: ACLs for every model

### Report

- `report/ronix_quality_operational_nonconformity_report.xml`: QWeb report for nonconformity records

## Domain Rules To Preserve

- Security is location-centric. If a feature belongs to a location flow, check whether `manager_ids`-based scoping must propagate.
- Public controllers use `sudo()` deliberately. Keep returned data narrow and explicit.
- Backend features follow one file pair per domain concept: Python model + XML view file.
- Attachment-style features usually need both backend management and public/website delivery behavior.
- Existing labels mix Turkish and English. Preserve the language pattern already used in the touched file instead of normalizing globally.
- The nonconformity model already contains text sanitizing/mojibake repair logic. Do not bypass it when adding new write/create text paths.

## Change Routing Rules

If the request is about:

- field/business logic: edit the model first, then matching view/search/action if needed
- menu visibility or permissions: inspect both `menus.xml` and security files
- public page content: inspect controller + website page/template together
- mobile app payload/API: inspect `controllers/mobile_app.py` and the source models together
- printed output: inspect model helper methods and report XML together
- frontend behavior: inspect manifest asset bundle and the matching JS/SCSS/XML template together

## Token-Efficient Workflow

Use this decision order:

1. Identify the feature bucket:
   - location/button
   - information
   - announcement
   - training
   - audit checklist
   - operational nonconformity
   - website/snippet/mobile API
2. Read only that bucket's model/view/controller/security files.
3. Avoid opening unrelated feature files.
4. Patch first, broaden scope only if a dependency is proven.

## Implementation Preferences

- Prefer extending existing domain files over introducing new cross-cutting helpers.
- Keep Odoo patterns straightforward: `fields`, `api`, constraints, helpers, and narrow overrides.
- Use `@api.model_create_multi` for create overrides.
- Keep XML IDs stable.
- Prefer additive view inheritance only if editing an external module. Inside this addon, editing the owning view file directly is usually clearer.
- When adding a new model, wire all 5 layers consciously if needed:
  `models/__init__.py`, access CSV, optional security rule, view XML, menu/action.

## Safety Checklist

Before finalizing, mentally check:

- Does this need ACL or record rule changes?
- Does this need manifest `data` ordering changes?
- Does a public route expose too much data?
- Does a website-facing attachment require `website_published` and `active` checks?
- Does a new field need to appear in list, form, search, and report/template?
- Does the change break current Turkish labels or encoding cleanup behavior?

## Common Task Recipes

### Add field to an existing feature

1. Edit the feature model.
2. Edit its `views/ronix_quality_*_views.xml`.
3. If searchable/filterable, update search view.
4. If public/mobile/report output uses it, update controller/template/report too.

### Add a new backend feature

1. Create model file.
2. Import it in `models/__init__.py`.
3. Add ACL rows.
4. Add security rule if location/user scoping is needed.
5. Create view/action.
6. Add menu entry.
7. Add manifest data entry in the correct order.

### Extend a public attachment flow

1. Update model and attachment model.
2. Keep route checks strict: existence, active state, publication state, datas presence.
3. Return proper mimetype/disposition headers only.

### Extend operational nonconformity

1. Update `models/ronix_quality_operational_nonconformity.py`.
2. Update `views/ronix_quality_operational_nonconformity_views.xml`.
3. Update `report/ronix_quality_operational_nonconformity_report.xml` if printed output changes.
4. Preserve `_repair_mojibake_text()` usage for user-visible text in report paths.

## What To Avoid

- Do not move multiple features into shared abstractions unless duplication is clearly harmful.
- Do not widen `sudo()` controller responses casually.
- Do not add files to manifest blindly without checking load order.
- Do not change security groups/rules as a side effect of a UI-only task.
- Do not refactor unrelated feature buckets during a focused request.

## Working Style For Future Tasks

When asked to work in this addon:

1. Name the feature bucket immediately.
2. Open only the files in that bucket.
3. State assumptions briefly.
4. Implement the smallest safe patch.
5. Verify impact on security, website/public exposure, and manifest wiring.
