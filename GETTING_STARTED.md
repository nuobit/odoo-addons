# Getting Started with This Odoo Addons Repository

## What is this repository?

This is a **NuoBiT Solutions SL** Odoo addons repository configured for **Odoo 18.0**. It follows the OCA (Odoo Community Association) standards and best practices for developing and maintaining Odoo modules.

## Current State

The repository is currently **empty of modules** but fully configured with:
- ✅ OCA-compliant project template
- ✅ Pre-commit hooks for code quality
- ✅ GitHub Actions workflows for CI/CD
- ✅ Linting and formatting tools (pylint, ruff, eslint, prettier)
- ✅ Code quality checks and test automation
- ✅ Codecov integration for test coverage

## What Can You Do Here?

### 1. **Create New Odoo Modules**

This repository is ready for you to develop custom Odoo modules. Each module should be created as a subdirectory with the standard Odoo module structure:

```
my_module_name/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── data/
│   └── my_model_data.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       ├── css/
│       └── xml/
└── README.rst
```

### 2. **Types of Modules You Can Develop**

- **Business Logic Modules**: Custom workflows, business rules, and processes
- **Integration Modules**: Connect Odoo with external systems (APIs, ERPs, etc.)
- **Localization Modules**: Country-specific adaptations (prefix with `l10n_es_`, etc.)
- **Extension Modules**: Enhance existing Odoo modules
- **Base Modules**: Foundation modules for other modules (prefix with `base_`)
- **Industry-Specific Modules**: Modules tailored for specific industries

### 3. **Development Workflow**

1. **Create a new module**:
   ```bash
   mkdir my_new_module
   cd my_new_module
   # Create __manifest__.py and other required files
   ```

2. **Follow OCA Guidelines**:
   - Use singular module names (e.g., `sale_order_extension`, not `sale_orders_extension`)
   - Follow Python naming conventions (CamelCase for classes, snake_case for variables)
   - Use English for all code, comments, and commit messages
   - Write meaningful commit messages with appropriate tags: `[ADD]`, `[FIX]`, `[IMP]`, etc.

3. **Code Quality Assurance**:
   ```bash
   # Run pre-commit checks locally
   pre-commit run --all-files
   
   # Run specific linters
   ruff check .
   pylint your_module/
   ```

4. **Testing**:
   - Write unit tests in `tests/` directory of your module
   - Tests are automatically run by GitHub Actions
   - Coverage reports are sent to Codecov

### 4. **Available Tools and Commands**

The repository includes several configured tools:

- **Ruff**: Fast Python linter and formatter
- **Pylint**: Python code analysis
- **ESLint**: JavaScript linting
- **Prettier**: Code formatting for web files
- **Pre-commit**: Automated code quality checks
- **Manifestoo**: Odoo manifest validation

### 5. **CI/CD Pipeline**

The repository has GitHub Actions workflows that will:
- ✅ Run pre-commit checks on every PR
- ✅ Test modules against Odoo and OCB (Odoo Community Backports)
- ✅ Check licenses and development status
- ✅ Generate code coverage reports
- ✅ Update translation files (.pot files)
- ✅ Handle stale issues and PRs

### 6. **Example Module Creation**

Here's what you could create as a first module:

```python
# Example: hello_world/__manifest__.py
{
    'name': 'Hello World',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'A simple hello world module',
    'author': 'NuoBiT Solutions SL',
    'website': 'https://github.com/NuoBiT/odoo-addons',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/hello_world_views.xml',
    ],
    'demo': [
        'demo/hello_world_demo.xml',
    ],
}
```

### 7. **Next Steps**

1. **Plan your modules**: Identify what business needs you want to solve
2. **Study existing modules**: Look at other OCA repositories for inspiration
3. **Start small**: Begin with a simple module to familiarize yourself with the workflow
4. **Follow the guidelines**: Use the copilot-instructions.md for detailed coding standards
5. **Test thoroughly**: Write tests and ensure they pass
6. **Document well**: Create proper README.rst files for each module

## Resources

- [OCA Development Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo Development Documentation](https://www.odoo.com/documentation/18.0/developer.html)
- [This repository's coding guidelines](.github/copilot-instructions.md)

## Need Help?

- Check the GitHub Issues for any ongoing discussions
- Review the OCA guidelines linked above
- Study existing modules in other OCA repositories
- Follow the Odoo development patterns and conventions

This repository is your canvas for creating powerful Odoo addons following industry best practices!