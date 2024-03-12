from jinja2_fragments.litestar import HTMXBlockTemplate
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from .config import TEMPLATE_DIR

htmx_template = HTMXBlockTemplate

template_config = TemplateConfig(
    directory=TEMPLATE_DIR,
    engine=JinjaTemplateEngine,
)
