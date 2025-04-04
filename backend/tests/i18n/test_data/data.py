from utils.common.i18n import gettext_lazy as _

# Add domain to all translations
hello_world = _("Hello World", domain="test_i18n")
hello_john = _("Hello {name}", domain="test_i18n", name="John")
hello_zhang = _("Hello {name}", domain="test_i18n", name="张三")
