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
