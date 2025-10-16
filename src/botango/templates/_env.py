from jinja2 import Template

from botango.schemas.template_class import ManagerTemplate
from .enviroment_jinja import ENV

ENV_TEMPLATE = ENV.from_string("""# BOT_DATA 
BOT_TOKEN={{ token }}

{% if mode.type == 'webhook' %}
# WEBHOOK_DATA
WEBHOOK_URL={{ mode.data.host }}
WEBHOOK_PORT={{ mode.data.port }}
WEBHOOK_PATH={{ mode.data.url_path }}
WEBHOOK_SECRET={{ mode.data.webhook_secret }}

{% endif %}
{% if database.name == 'postgresql' %}
# DATABASE_DATA
POSTGRES_HOST={{ database.host }}
POSTGRES_PORT={{ database.port }}
POSTGRES_USER={{ database.user }}
POSTGRES_PASSWORD={{ database.password }}
POSTGRES_NAME={{ database.name_db }}

{% endif %}
{% if database.name == 'aiosqlite' %}
# DATABASE_DATA
NAME_DATABASE={{ database.name_db }}

{% endif %}
""")

class EnvTemplate(ManagerTemplate):
    filename: str = ".env"
    template: Template = ENV_TEMPLATE

