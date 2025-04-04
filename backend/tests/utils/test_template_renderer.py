import pytest

from utils.notification import EmailTemplateRenderer


@pytest.fixture
def template_dir(tmp_path):
    # Create a temporary template directory
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    
    # Create a test template file
    test_template = template_dir / "test.html"
    test_template.write_text("Hello {{ name }}!")
    
    return template_dir


def test_render_template(template_dir):
    renderer = EmailTemplateRenderer(template_dir)
    result = renderer.render("test.html", name="World")
    assert result == "Hello World!"


def test_render_string():
    renderer = EmailTemplateRenderer("templates")  # Directory doesn't matter for string rendering
    template_string = "Value is {{ value }}"
    result = renderer.render_string(template_string, value=42)
    assert result == "Value is 42"


def test_template_not_found(template_dir):
    renderer = EmailTemplateRenderer(template_dir)
    with pytest.raises(FileNotFoundError):
        renderer.render("nonexistent.html")


def test_invalid_template_syntax(template_dir):
    renderer = EmailTemplateRenderer(template_dir)
    with pytest.raises(RuntimeError):
        renderer.render_string("{% invalid syntax %}") 