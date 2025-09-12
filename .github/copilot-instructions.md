# NuoBiT Odoo Addons Repository

NuoBiT Odoo Addons is a collection of 206 custom Odoo 14.0 modules developed by NuoBiT Solutions, S.L. These addons extend Odoo functionality across accounting, inventory, sales, connectors, and localization for Spanish businesses.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Repository Setup
- Clone and navigate to repository:
  ```bash
  cd /path/to/odoo-addons
  ```

### Bootstrap Development Environment
- Install Python dependencies:
  ```bash
  pip3 install --user manifestoo pre-commit black flake8 isort
  pip3 install -r requirements.txt  # Takes 30 seconds
  ```

### Essential Tools and Commands
- **Lint entire repository** (FAST - takes 2 seconds, NEVER CANCEL):
  ```bash
  export PATH=$HOME/.local/bin:$PATH
  flake8 --config=.flake8 .
  ```
- **Format code with black** (FAST - takes 3 seconds):
  ```bash
  black --check .  # Check only
  black .          # Apply formatting
  ```
- **Check import sorting** (FAST - takes 2 seconds):
  ```bash
  isort --check-only .  # Check only
  isort .               # Apply sorting
  ```
- **Validate addon manifests** (FAST - takes 1 second):
  ```bash
  manifestoo -d . list | head -10  # List first 10 addons
  manifestoo -d . check-licenses   # Requires Odoo (fails locally - use CI)
  ```

### Pre-commit Setup (Optional - Network Dependent)
- Install hooks (MAY FAIL due to network timeouts - this is normal):
  ```bash
  pre-commit install --install-hooks  # Timeout expected: 10+ minutes
  ```
- If pre-commit installation fails due to network issues, skip it. The CI will validate using the same rules.

## Development Workflow

### Working with Individual Addons
- Each directory is an independent Odoo addon with standard structure:
  ```
  addon_name/
  ├── __manifest__.py    # Addon metadata and dependencies
  ├── __init__.py       # Python module initialization
  ├── models/           # Business logic (Python)
  ├── views/           # User interface (XML)
  ├── data/            # Default data (XML)
  ├── security/        # Access permissions (XML/CSV)
  └── tests/           # Unit tests (Python)
  ```

### Addon Dependencies
- **OCA Dependencies**: Listed in `oca_dependencies.txt` - includes account-invoicing, connector, l10n-spain, etc.
- **Python Dependencies**: Auto-generated in `requirements.txt` from addon manifests
- **External Dependencies**: Some addons require external services (SQL Server, MySQL, web services)

### Code Quality Standards
- **Always run linting before committing**:
  ```bash
  flake8 --config=.flake8 addon_name/  # Lint specific addon (< 1 second)
  black --check addon_name/            # Check formatting (< 1 second)  
  isort --check-only addon_name/       # Check imports (< 1 second)
  ```
- **Fix common linting issues**:
  ```bash
  black addon_name/     # Auto-fix formatting
  isort addon_name/     # Auto-fix imports
  ```

## Testing and Validation

### Local Testing Limitations
- **CANNOT run Odoo tests locally** - requires full Odoo installation with dependencies
- **CAN validate**: Code syntax, linting, manifest structure, Python imports
- **CI is authoritative** - GitHub Actions provides the definitive test environment

### Manual Validation Steps
- **Verify addon structure**:
  ```bash
  find addon_name/ -name "*.py" -exec python3 -m py_compile {} \;  # Check Python syntax
  manifestoo -d . --select-include=addon_name list                 # Verify manifest
  ```
- **Check dependencies exist**:
  ```bash
  grep -r "depends.*:" addon_name/__manifest__.py  # List addon dependencies
  ```
- **Validate Python imports** (test basic imports work):
  ```bash
  cd addon_name && python3 -c "import models" 2>/dev/null && echo "Import OK" || echo "Import failed"
  ```

### GitHub Actions CI
- **NEVER CANCEL CI builds** - Full CI takes 15-30 minutes including:
  - Container setup with `ghcr.io/oca/oca-ci/py3.6-odoo14.0:latest`
  - `oca_install_addons` - Installs OCA dependencies (10+ minutes)
  - `oca_init_test_database` - Sets up PostgreSQL test database (2-5 minutes)  
  - `oca_run_tests` - Runs all addon tests (5-15 minutes)
  - License and development status validation
- **CI Commands** (only work in OCA containers):
  ```bash
  oca_install_addons     # Install dependencies - DO NOT RUN LOCALLY
  oca_init_test_database # Setup test DB - DO NOT RUN LOCALLY  
  oca_run_tests         # Run tests - DO NOT RUN LOCALLY
  ```

### Test Structure
- Tests use Odoo's testing framework (`from odoo.tests import common`)
- Common base class: `TestCommon(common.SavepointCase)`
- Test files in `addon_name/tests/test_*.py`
- Example test validation:
  ```python
  def test_feature(self):
      # ARRANGE - Set up test data
      record = self.env['model.name'].create({...})
      # ACT - Perform action  
      record.method_to_test()
      # ASSERT - Verify results
      self.assertTrue(record.expected_field)
  ```

## Project Structure and Navigation

### Key Addon Categories
- **Accounting**: `account_*` - Spanish accounting, invoicing, financial reporting
- **Stock/Inventory**: `stock_*` - Warehouse management, barcodes, tracking  
- **Sales**: `sale_*` - Sales orders, pricing, customer management
- **Connectors**: `connector_*` - External system integrations (Ambugest, Sage, etc.)
- **Localization**: `l10n_es_*` - Spanish tax, legal, and regulatory compliance
- **Website**: `website_*` - E-commerce and portal extensions

### Common File Locations
- **Manifest files**: `*/__manifest__.py` - Addon metadata and dependencies
- **Requirements**: `requirements.txt`, `test-requirements.txt`, `oca_dependencies.txt`
- **Configuration**: `.flake8`, `.pylintrc`, `.pre-commit-config.yaml`
- **CI Configuration**: `.github/workflows/test.yml`
- **Setup files**: `setup/*/setup.py` - PyPI packaging (auto-generated)

### Important Commands Reference
```bash
# Repository analysis (FAST commands)
manifestoo -d . list | wc -l                    # Count addons (206 expected)
find . -name "__manifest__.py" | wc -l          # Alternative addon count
grep -r "version.*14.0" */\__manifest__.py | wc -l  # Verify Odoo 14.0 version

# Quality checks (FAST - run before every commit)
flake8 --config=.flake8 .                       # Full repository lint (2 seconds)
black --check .                                 # Check code formatting (3 seconds)
isort --check-only .                            # Check import sorting (2 seconds)

# Individual addon work (VERY FAST)
flake8 --config=.flake8 addon_name/             # Lint single addon (< 1 second)
python3 -m py_compile addon_name/models/*.py    # Syntax check Python files
```

## Troubleshooting

### Network and Timeout Issues
- **Pre-commit installation may fail** - Network timeouts are common, use CI for validation
- **OCA tool installation requires specific environment** - Only works in OCA containers
- **pip timeouts**: Use `--timeout=300` flag for slower connections

### Common Development Issues  
- **Import errors**: Verify addon dependencies in `__manifest__.py`
- **Linting failures**: Run `black addon_name/` and `isort addon_name/` to auto-fix
- **Manifest issues**: Use `manifestoo -d . --select-include=addon_name check-licenses`
- **Missing dependencies**: Check `oca_dependencies.txt` and CI logs

### When CI Fails
- **Check GitHub Actions logs** - Look for specific addon test failures
- **Verify local linting passes** - `flake8 --config=.flake8 .` must be clean
- **Check manifest validity** - Use manifestoo commands
- **Review dependency changes** - Ensure required addons are available

## Development Best Practices

### Before Making Changes
1. **Always run local linting** - Takes < 5 seconds total
2. **Understand addon dependencies** - Check `__manifest__.py` 
3. **Review existing tests** - Look in `addon_name/tests/` directory

### While Developing  
1. **Make minimal changes** - Follow Odoo and OCA conventions
2. **Test imports work** - Verify Python syntax after changes
3. **Respect OCA standards** - Code will be validated against strict rules

### Before Committing
1. **MANDATORY linting** - All these must pass:
   ```bash
   flake8 --config=.flake8 .      # Must show no errors
   black --check .                # Must show "would be left unchanged"  
   isort --check-only .           # Must show no changes needed
   ```
2. **Verify addon structure** - Ensure `__manifest__.py` is valid
3. **Test basic imports** - Check Python files compile successfully

Remember: This is an addon collection, not a standalone application. Focus on addon-level validation and rely on CI for comprehensive Odoo testing.