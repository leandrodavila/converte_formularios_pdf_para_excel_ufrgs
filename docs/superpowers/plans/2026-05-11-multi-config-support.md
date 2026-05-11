# Multi-Configuration Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable support for multiple PDF form types through separate YAML configuration files organized in a `configs/` directory.

**Architecture:** File reorganization only - move existing config.yaml to configs/ancestralidades.yaml, create symlink for backward compatibility, add template and documentation files. No Python code changes required.

**Tech Stack:** YAML configuration files, Git symlinks, Markdown documentation

---

## Task 1: Create configs Directory and Move Existing Config

**Files:**
- Create: `configs/` directory
- Move: `config.yaml` → `configs/ancestralidades.yaml`
- Create: `config.yaml` symlink → `configs/ancestralidades.yaml`

- [ ] **Step 1: Create configs directory**

```bash
mkdir configs
```

Expected: Directory created successfully

- [ ] **Step 2: Move existing config to configs directory**

```bash
git mv config.yaml configs/ancestralidades.yaml
```

Expected: File moved and staged in git

- [ ] **Step 3: Create symlink for backward compatibility (Windows)**

```bash
# Using Git Bash or PowerShell (as administrator)
cmd //c mklink config.yaml configs\ancestralidades.yaml
```

Expected: Symlink created: `config.yaml -> configs/ancestralidades.yaml`

Note: On Linux/Mac use: `ln -s configs/ancestralidades.yaml config.yaml`

- [ ] **Step 4: Verify symlink works**

```bash
python -m src.main --help
```

Expected: Help message displays without errors

- [ ] **Step 5: Commit the reorganization**

```bash
git add configs/ancestralidades.yaml config.yaml
git commit -m "refactor: move config to configs directory with backward-compat symlink"
```

---

## Task 2: Create Template Configuration File

**Files:**
- Create: `configs/template.yaml`

- [ ] **Step 1: Create template.yaml with full structure**

```yaml
# ============================================================================
# PDF Form Extractor - Configuration Template
# ============================================================================
# 
# Copy this file to create a new form type configuration:
#   cp configs/template.yaml configs/my-form-type.yaml
#
# Then customize the sections below for your specific form.
#

# ----------------------------------------------------------------------------
# SAP AI Hub Configuration
# ----------------------------------------------------------------------------
sap:
  model_name: "anthropic--claude-4.5-sonnet"
  auth_method: "env"  # "env" uses ANTHROPIC_API_KEY env var, "config" uses api_key below
  # api_key: "your-key-here"  # Only needed if auth_method: "config"
  max_tokens: 2000    # Increase if forms are very complex (max 4096)
  temperature: 0      # Keep at 0 for consistent extraction

# ----------------------------------------------------------------------------
# Extraction Behavior
# ----------------------------------------------------------------------------
extraction:
  retry_attempts: 3              # Number of retries on API failures
  retry_delay_seconds: 2         # Initial delay between retries
  backoff_multiplier: 2          # Exponential backoff multiplier (2 = 2s, 4s, 8s)
  rate_limit_delay: 1            # Delay between successful requests (avoid rate limits)

# ----------------------------------------------------------------------------
# Output Configuration
# ----------------------------------------------------------------------------
output:
  directory: "output"                    # Base output directory
  excel_filename: "results_my_form.xlsx" # CHANGE THIS for your form type
  log_filename: "extraction.log"

# ----------------------------------------------------------------------------
# Form Field Definitions
# ----------------------------------------------------------------------------
# Define ALL fields you want to extract from the PDF.
# Use snake_case for field names (e.g., patient_id, blood_pressure)
#
# NOTE: 'quilombo' and 'arquivo' are automatically added as the first two columns.
#
form_fields:
  - field_name_1
  - field_name_2
  - field_name_3
  - field_name_4
  - field_name_5
  # Add more fields as needed

# ----------------------------------------------------------------------------
# Excel Column Headers
# ----------------------------------------------------------------------------
# Map each field to a human-readable Excel column header.
# 
# REQUIRED: Always include quilombo and arquivo mappings
# REQUIRED: Include all fields from form_fields above
#
field_headers:
  quilombo: "Source Location"     # Column name for quilombo/clinic/site
  arquivo: "PDF Filename"          # Column name for source file
  field_name_1: "Display Name 1"
  field_name_2: "Display Name 2"
  field_name_3: "Display Name 3"
  field_name_4: "Display Name 4"
  field_name_5: "Display Name 5"
  # Add headers for all fields

# ----------------------------------------------------------------------------
# Excel Column Widths (Optional)
# ----------------------------------------------------------------------------
# Set custom widths for columns with long content.
# Units are approximate character widths in Excel.
# 
# Fields not listed here use the 'default' width.
#
column_widths:
  quilombo: 20
  arquivo: 15
  field_name_1: 30    # Example: wider column for long text
  field_name_3: 40    # Example: even wider for very long text
  default: 18         # Default width for all other columns

# ----------------------------------------------------------------------------
# Extraction System Prompt
# ----------------------------------------------------------------------------
# Customize this prompt for your specific form type.
# 
# REQUIRED: Include {fields_json} placeholder - it will be replaced with the field schema
# IMPORTANT: Emphasize "return ONLY JSON" to avoid markdown wrappers
#
system_prompt: |
  You are extracting data from [DESCRIBE YOUR FORM TYPE HERE] forms.
  Extract EXACTLY the fields listed below from the form and return ONLY valid JSON.
  
  Do not include markdown formatting, explanatory text, or any content other than the JSON object.
  
  Required fields:
  {fields_json}
  
  Extraction rules:
  - For checkbox fields with multiple selections, list items separated by " | "
  - For date fields, preserve the format shown in the form
  - For numeric fields, extract only the number without units
  - If a field is blank, illegible, or not applicable, use an empty string ""
  - Return ONLY the JSON object, nothing else
```

- [ ] **Step 2: Verify YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('configs/template.yaml'))"
```

Expected: No output (valid YAML)

- [ ] **Step 3: Commit template**

```bash
git add configs/template.yaml
git commit -m "docs: add configuration template for new form types"
```

---

## Task 3: Create Example Medical Configuration

**Files:**
- Create: `configs/example-medical.yaml`

- [ ] **Step 1: Create example medical intake form config**

```yaml
# Medical Intake Form Configuration
# Example configuration for medical clinic intake forms

sap:
  model_name: "anthropic--claude-4.5-sonnet"
  auth_method: "env"
  max_tokens: 2000
  temperature: 0

extraction:
  retry_attempts: 3
  retry_delay_seconds: 2
  backoff_multiplier: 2
  rate_limit_delay: 1

output:
  directory: "output"
  excel_filename: "results_medical_intake.xlsx"
  log_filename: "extraction.log"

form_fields:
  - patient_id
  - visit_date
  - chief_complaint
  - symptoms
  - allergies
  - current_medications
  - blood_pressure
  - temperature
  - clinical_notes

field_headers:
  quilombo: "Clinic"
  arquivo: "Form File"
  patient_id: "Patient ID"
  visit_date: "Visit Date"
  chief_complaint: "Chief Complaint"
  symptoms: "Symptoms"
  allergies: "Known Allergies"
  current_medications: "Current Medications"
  blood_pressure: "BP (mmHg)"
  temperature: "Temp (°C)"
  clinical_notes: "Clinical Notes"

column_widths:
  quilombo: 20
  arquivo: 15
  chief_complaint: 35
  symptoms: 40
  allergies: 30
  current_medications: 45
  clinical_notes: 50
  default: 18

system_prompt: |
  You are extracting data from medical clinic intake forms.
  Extract EXACTLY the fields below from the form and return ONLY valid JSON.
  
  Do not include markdown formatting, explanatory text, or any other content.
  
  Required fields:
  {fields_json}
  
  Extraction rules:
  - For chief_complaint and symptoms, extract the complete text
  - For allergies, list all mentioned allergies separated by " | "
  - For current_medications, list medication names separated by " | "
  - For blood_pressure, format as "systolic/diastolic" (e.g., "120/80")
  - For temperature, extract the number only (e.g., "37.2")
  - For dates, use the format shown in the form
  - If a field is blank or not applicable, use ""
  - Return ONLY the JSON object, nothing else
```

- [ ] **Step 2: Verify YAML syntax**

```bash
python -c "import yaml; yaml.safe_load(open('configs/example-medical.yaml'))"
```

Expected: No output (valid YAML)

- [ ] **Step 3: Commit example config**

```bash
git add configs/example-medical.yaml
git commit -m "docs: add example medical intake form configuration"
```

---

## Task 4: Create Configuration Guide README

**Files:**
- Create: `configs/README.md`

- [ ] **Step 1: Create comprehensive README**

Create `configs/README.md` with the following content:

```markdown
# Form Configuration Guide

This directory contains configuration files for different PDF form types supported by the extractor.

## Quick Start

**Use an existing configuration:**
```bash
# Default (ancestralidades)
python -m src.main path/to/pdfs

# Specific form type
python -m src.main path/to/pdfs --config configs/medical-intake.yaml
```

**Create a new configuration:**
```bash
# 1. Copy the template
cp configs/template.yaml configs/my-form-type.yaml

# 2. Edit with your fields and headers
nano configs/my-form-type.yaml

# 3. Test it
python -m src.main path/to/sample-pdfs --config configs/my-form-type.yaml --verbose
```

## Available Configurations

| Config File | Form Type | Fields | Description |
|------------|-----------|--------|-------------|
| `ancestralidades.yaml` | Research forms | 40 | Quilombo ancestralidades research project |
| `example-medical.yaml` | Medical intake | 9 | Example medical clinic intake forms |
| `template.yaml` | N/A | Template | Starting point for new configs |

## Creating a New Form Configuration

### Step 1: Copy Template

```bash
cp configs/template.yaml configs/your-form-name.yaml
```

### Step 2: Define Form Fields

List all fields you want to extract in `form_fields`:

```yaml
form_fields:
  - patient_id
  - visit_date
  - chief_complaint
  - blood_pressure
  - temperature
```

**Field Naming Rules:**
- Use lowercase with underscores (snake_case)
- Be descriptive but concise
- Avoid special characters (except underscore)

### Step 3: Map to Excel Headers

Provide human-readable headers in `field_headers`:

```yaml
field_headers:
  quilombo: "Clinic"              # Always required
  arquivo: "Form File"             # Always required
  patient_id: "Patient ID"
  visit_date: "Visit Date"
  chief_complaint: "Chief Complaint"
  blood_pressure: "BP (mmHg)"
  temperature: "Temp (°C)"
```

### Step 4: Set Column Widths

For fields with long text content:

```yaml
column_widths:
  chief_complaint: 40    # Wider for long text
  notes: 50              # Even wider
  default: 18            # All other columns
```

### Step 5: Customize Extraction Prompt

Tailor the `system_prompt` to your form type:

```yaml
system_prompt: |
  You are extracting data from medical intake forms.
  Extract EXACTLY the fields below and return ONLY valid JSON.
  
  Required fields:
  {fields_json}
  
  Rules:
  - For blood pressure, format as "systolic/diastolic" (e.g., "120/80")
  - For dates, use YYYY-MM-DD format
  - For empty fields, use ""
  - Return ONLY JSON, nothing else
```

**Important:**
- Keep `{fields_json}` placeholder - it's replaced at runtime
- Emphasize "ONLY valid JSON" to avoid markdown wrappers
- Include field-specific formatting rules

### Step 6: Update Output Filename

Change the Excel filename to match your form type:

```yaml
output:
  excel_filename: "results_medical_intake.xlsx"
```

### Step 7: Test Your Configuration

```bash
# Test with verbose logging
python -m src.main path/to/test-pdfs --config configs/your-form-name.yaml --verbose

# Check the output
ls output/run_*/
cat output/run_*/logs/*.log
```

## Reserved Fields

These fields are automatically added and should NOT be included in `form_fields`:

- **quilombo** - Source location (from `--quilombo` flag or folder name)
- **arquivo** - PDF filename

Always include them in `field_headers`:

```yaml
field_headers:
  quilombo: "Location"  # Customize the header text
  arquivo: "Filename"   # Customize the header text
```

## Common Patterns

### Checkbox Fields

For fields where multiple items can be selected:

```yaml
# In system_prompt:
# - For checkbox fields, list selected items separated by " | "

# Example extracted value: "Diabetes | Hypertension | Asthma"
```

### Date Fields

```yaml
# In system_prompt:
# - For dates, preserve the format shown in the form
# OR
# - For dates, use YYYY-MM-DD format
```

### Numeric Fields

```yaml
# In system_prompt:
# - For numeric fields, extract only the number without units
# - For weight in kg, extract "75.5" not "75.5 kg"
```

### Multi-line Text

```yaml
# In system_prompt:
# - For multi-line fields, preserve line breaks with newline characters

# In column_widths:
clinical_notes: 50  # Wide column
```

## Usage Examples

### Basic Usage

```bash
# Use default configuration
python -m src.main /data/pdfs/

# Use specific configuration
python -m src.main /data/pdfs/ --config configs/medical-intake.yaml
```

### With Quilombo/Location Override

```bash
# Override location name
python -m src.main /data/pdfs/ --quilombo "Clinic A" --config configs/medical-intake.yaml
```

### Verbose Logging

```bash
# See detailed extraction logs
python -m src.main /data/pdfs/ --config configs/survey.yaml --verbose
```

### Windows Paths

```bash
# Windows example
python -m src.main C:\data\forms --config configs\medical-intake.yaml
```

## Troubleshooting

### Problem: "Missing required field" errors

**Cause:** Field defined in `form_fields` but not in `field_headers`, or vice versa.

**Solution:** Ensure every field in `form_fields` has a corresponding entry in `field_headers`.

### Problem: Empty extraction results

**Possible causes:**
1. PDF image quality too low
2. `max_tokens` too low for complex forms
3. System prompt not clear enough

**Solutions:**
- Increase `max_tokens` to 3000-4000
- Enhance system prompt with more specific instructions
- Check PDF quality (should be readable when opened)

### Problem: JSON parsing errors

**Cause:** Model returns markdown-wrapped JSON (```json ... ```)

**Solution:** Emphasize in `system_prompt`:
```yaml
system_prompt: |
  Return ONLY valid JSON, without markdown code blocks or any other formatting.
```

### Problem: Rate limiting

**Cause:** Processing too many PDFs too quickly

**Solution:** Increase `rate_limit_delay`:
```yaml
extraction:
  rate_limit_delay: 2  # Increase from 1 to 2 seconds
```

## Field Count Considerations

- **Small forms (5-15 fields):** Use default settings
- **Medium forms (15-30 fields):** Consider `max_tokens: 3000`
- **Large forms (30+ fields):** Use `max_tokens: 4000` and test thoroughly

## Best Practices

1. **Start small:** Test with 2-3 sample PDFs before batch processing
2. **Use verbose mode:** Always test new configs with `--verbose` flag
3. **Check logs:** Review extraction logs for parsing issues
4. **Iterate prompts:** Refine system prompt based on extraction quality
5. **Document fields:** Add comments in your config explaining non-obvious fields
6. **Version control:** Commit config changes with descriptive messages

## Getting Help

1. Check logs in `output/run_*/logs/` for detailed error messages
2. Review this README for configuration guidelines
3. Compare your config to `ancestralidades.yaml` for reference
4. Test with `--verbose` flag to see full extraction details
```

- [ ] **Step 2: Verify README renders correctly**

Preview the markdown in your editor or:
```bash
cat configs/README.md
```

Expected: Well-formatted markdown with clear sections

- [ ] **Step 3: Commit README**

```bash
git add configs/README.md
git commit -m "docs: add comprehensive configuration guide for configs directory"
```

---

## Task 5: Update Main README with Multi-Config Section

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add multi-configuration section after Configuration section**

Add the following section after the existing "Configuration" section in README.md (around line 100):

```markdown
### 3. Working with Multiple Form Types

The application supports multiple PDF form types through separate configuration files in the `configs/` directory.

**Using different form types:**

```bash
# Use default form type (ancestralidades)
python -m src.main path/to/pdfs

# Use medical intake forms
python -m src.main path/to/pdfs --config configs/example-medical.yaml

# Use custom form configuration
python -m src.main path/to/pdfs --config configs/my-custom-form.yaml
```

**Available configurations:**
- `configs/ancestralidades.yaml` - Ancestralidades research forms (40 fields) [DEFAULT]
- `configs/example-medical.yaml` - Medical clinic intake forms (9 fields)
- `configs/template.yaml` - Template for creating new form types

**Creating a new form type:**

1. Copy the template:
   ```bash
   cp configs/template.yaml configs/my-form.yaml
   ```

2. Edit `configs/my-form.yaml`:
   - Define your `form_fields`
   - Map fields to `field_headers`
   - Customize `system_prompt`
   - Update `excel_filename`

3. Test with sample PDFs:
   ```bash
   python -m src.main samples/ --config configs/my-form.yaml --verbose
   ```

See `configs/README.md` for detailed instructions on creating new configurations.
```

- [ ] **Step 2: Update usage examples to show config selection**

Update the "Advanced Options" section (around line 118) to include config examples:

```markdown
**Use custom configuration file**:
```bash
# Linux/Mac
python -m src.main path/to/pdfs --config configs/medical-intake.yaml

# Windows
python -m src.main C:\Users\YourName\Documents\pdfs --config configs\example-medical.yaml
```
```

- [ ] **Step 3: Verify README renders correctly**

```bash
cat README.md | head -150
```

Expected: New section appears after Configuration, examples updated

- [ ] **Step 4: Commit README updates**

```bash
git add README.md
git commit -m "docs: add multi-configuration support to README"
```

---

## Task 6: Test Backward Compatibility

**Files:**
- Test: All existing functionality with symlinked config

- [ ] **Step 1: Test default config usage (symlink)**

```bash
# Should use config.yaml -> configs/ancestralidades.yaml
python -m src.main --help
```

Expected: Help message displays without errors

- [ ] **Step 2: Verify config loads correctly**

```bash
python -c "from src.config import load_config; c = load_config(); print(f'Loaded {len(c.form_fields)} fields')"
```

Expected: Output shows "Loaded 40 fields"

- [ ] **Step 3: Test with sample PDF if available**

If you have sample PDFs:
```bash
python -m src.main path/to/sample/pdfs --verbose
```

Expected: Extraction runs without config errors

If no sample PDFs available, skip this step.

- [ ] **Step 4: Verify no Python code changes needed**

```bash
git status
```

Expected: Only config files and docs modified, no .py files changed

- [ ] **Step 5: Document successful backward compatibility test**

Add to git log:
```bash
# No commit needed, just verify no .py files changed
```

---

## Task 7: Test Multi-Config Selection

**Files:**
- Test: Config selection via --config flag

- [ ] **Step 1: Test loading ancestralidades explicitly**

```bash
python -c "from src.config import load_config; from pathlib import Path; c = load_config(Path('configs/ancestralidades.yaml')); print(f'{len(c.form_fields)} fields, output: {c.output.excel_filename}')"
```

Expected: Output shows "40 fields, output: resultados_ancestralidades.xlsx"

- [ ] **Step 2: Test loading example medical config**

```bash
python -c "from src.config import load_config; from pathlib import Path; c = load_config(Path('configs/example-medical.yaml')); print(f'{len(c.form_fields)} fields, output: {c.output.excel_filename}')"
```

Expected: Output shows "9 fields, output: results_medical_intake.xlsx"

- [ ] **Step 3: Test loading template config**

```bash
python -c "from src.config import load_config; from pathlib import Path; c = load_config(Path('configs/template.yaml')); print(f'{len(c.form_fields)} fields')"
```

Expected: Output shows "5 fields" (template has 5 placeholder fields)

- [ ] **Step 4: Verify CLI --config flag works**

```bash
python -m src.main --config configs/example-medical.yaml --help
```

Expected: Help message displays without errors

- [ ] **Step 5: Document successful multi-config test**

No commit needed, tests pass.

---

## Task 8: Create Final Summary Commit

**Files:**
- All previous changes

- [ ] **Step 1: Review all changes**

```bash
git log --oneline -8
```

Expected: Shows all commits from previous tasks

- [ ] **Step 2: Verify git status is clean**

```bash
git status
```

Expected: "nothing to commit, working tree clean"

- [ ] **Step 3: Create summary of changes**

Document what was added:
- ✅ `configs/` directory structure created
- ✅ Existing config moved to `configs/ancestralidades.yaml`
- ✅ Symlink `config.yaml` for backward compatibility
- ✅ `configs/template.yaml` with inline comments
- ✅ `configs/example-medical.yaml` as concrete example
- ✅ `configs/README.md` with comprehensive guide
- ✅ Main `README.md` updated with multi-config section
- ✅ Backward compatibility tested
- ✅ Multi-config selection tested
- ✅ No Python code changes required

- [ ] **Step 4: Push changes if desired**

```bash
# Optional: push to remote
git push origin main
```

---

## Success Criteria

All tasks completed when:

- [x] `configs/` directory exists with all files
- [x] `config.yaml` symlink points to `configs/ancestralidades.yaml`
- [x] Default behavior unchanged (backward compatible)
- [x] Explicit config selection works via `--config` flag
- [x] Template config has comprehensive inline comments
- [x] Example medical config demonstrates different field structure
- [x] `configs/README.md` provides step-by-step guide
- [x] Main `README.md` updated with multi-config examples
- [x] All tests pass (no Python code changes)
- [x] Git history clean with descriptive commits

## Notes for Implementation

**Windows Symlink Creation:**
- Use Git Bash: `ln -s configs/ancestralidades.yaml config.yaml`
- OR use PowerShell (admin): `cmd /c mklink config.yaml configs\ancestralidades.yaml`
- OR use PowerShell: `New-Item -ItemType SymbolicLink -Path config.yaml -Target configs\ancestralidades.yaml`

**Testing Without Sample PDFs:**
- Config loading can be tested via Python import
- Full extraction testing requires actual PDF files
- Skip PDF-dependent tests if no samples available

**No Code Changes Required:**
- Existing `--config` flag in `src/main.py` already works with any path
- `load_config()` in `src/config.py` already accepts Path parameter
- `form_fields` already loaded dynamically from config
- All modules already use `config.form_fields` at runtime
