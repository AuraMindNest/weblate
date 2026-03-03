# Weblate Automation Scripts

**Testing and development only — not for production use.**

Automate Weblate project setup and translation management via REST API.

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `add-or-update.sh` | Development — CI trigger for add-or-update API | `./add-or-update.sh` |
| `setup_project.py` | Bulk: scan repo, generate configs, create components | `python3 setup_project.py --config project_config.json [--create-components]` |
| `create_component_and_add_translation.py` | Create component + add translations | `python3 create_component_and_add_translation.py --config setup.json` |
| `create_component.py` | Create project and component | `python3 create_component.py --config component.json --web-config web.json` |
| `add_translation.py` | Add languages to component | `python3 add_translation.py --web-config web.json --project X --component Y --language fr,de` |
| `delete_all_components.py` | Delete projects/components (use with caution) | `python3 delete_all_components.py --project X --yes` |
| `upload_translations.py` | List components, upload PO files | `python3 upload_translations.py --project X [--upload --language zh_Hans]` |
| `upload_all_components.sh` | Upload for all components in project | `./upload_all_components.sh` |
| `generate_boost_project_configs.py` | Generate project configs from Boost list | `python3 generate_boost_project_configs.py --list list.txt` |
| `collect_boost_libraries_extensions.py` | Fetch Boost metadata, output extensions | `python3 collect_boost_libraries_extensions.py --version boost-1.90.0 -o list.txt` |

Run any script with `--help` for options.

## Setup

1. `pip install requests`
2. Create `web.json` in this directory:
   ```json
   {"weblate_url": "http://localhost:8080", "api_token": "wlu_YOUR_TOKEN"}
   ```
   Keep it private (gitignored).
3. Create component/project JSON config. See `quickbook-test-component-configs/setup.json` or `boost-submodule-component-configs/` for examples.

