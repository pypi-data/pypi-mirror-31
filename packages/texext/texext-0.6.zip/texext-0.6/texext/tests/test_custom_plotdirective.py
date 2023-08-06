""" Tests for plotdirective build using sphinx extensions

Test ability to combine plot_directive with mathcode
"""

from os.path import dirname, join as pjoin
import re

from sphinxtesters import ModifiedPageBuilder

PAGES = pjoin(dirname(__file__), 'plotdirective')


class TestCustomPlotDirective(ModifiedPageBuilder):
    # Test build and output of custom_plotdirective project
    page_source_template = PAGES

    @classmethod
    def modify_pages(cls):
        conf_fname = pjoin(cls.page_source, 'conf.py')
        with open(conf_fname, 'rt') as fobj:
            contents = fobj.read()
        contents = contents.replace(
            "'matplotlib.sphinxext.plot_directive'",
            '"plot_directive"')
        contents += """
< # Use custom plot_directive
< sys.path.insert(0, abspath(pjoin('.')))
< import plot_directive
< mathcode_plot_directive = plot_directive
"""
        with open(conf_fname, 'wt') as fobj:
            fobj.write(contents)

    def test_plot_and_math(self):
        doctree = self.get_doctree('plot_and_math')
        assert len(doctree.document) == 1
        tree_str = self.doctree2str(doctree)
        # Sphinx by 1.3 adds "highlight_args={}", Sphinx at 1.1.3 does not
        assert re.compile(
            '<title>Plot directive with mathcode</title>\n'
            '<paragraph>Some text</paragraph>\n'
            r'<literal_block (highlight_args="{}"\s*)?language="python" '
            'linenos="False" xml:space="preserve">a = 101</literal_block>\n'
            '<only expr="html"/>\n'
            '<only expr="latex"/>\n'
            '<only expr="texinfo"/>\n'
            '<paragraph>More text</paragraph>\n'
            '<displaymath docname="plot_and_math" label="None" '
            'latex="101" nowrap="False"( number="None")?/>'
        ).search(tree_str)
