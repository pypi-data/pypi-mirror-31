from django.http import Http404

from regulations.generator import generator, node_types
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.generator.subterp import filter_by_subterp
from regulations.views.partial import PartialSectionView, PartialView


class PartialInterpView(PartialView):
    """ Interpretation of a reg text section/paragraph or appendix. Used for
    in-line interpretations"""

    template_name = "regulations/interpretations.html"
    inline = False
    layers = []

    @staticmethod
    def mk_layers(root_label, version):
        """Function to generate a shared set of layers"""
        return generator.layers(
            ['terms', 'internal', 'keyterms', 'paragraph'], 'cfr', root_label,
            sectional=True, version=version)

    def determine_layers(self, label_id, version):
        """Don't generate new appliers"""
        return self.layers

    def transform_context(self, context, builder):
        context['inline'] = self.inline
        context['c'] = {'node_type': node_types.INTERP,
                        'children': [builder.tree]}
        return context


class PartialSubterpView(PartialSectionView):
    """View of subterps - interpretations of whole subparts, regtext, or
    appendices"""
    def get_context_data(self, **kwargs):
        #   skip our parent
        context = super(PartialView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        label = label_id.split('-')
        reg_part = label[0]
        version = context['version']

        context['navigation'] = self.section_navigation(label_id, version)

        interp = generator.get_tree_paragraph(reg_part + '-Interp', version)
        if not interp:
            raise Http404

        subterp_sects = filter_by_subterp(interp['children'], label, version)
        if not subterp_sects:
            raise Http404

        context['markup_page_type'] = 'reg-section'
        html_label = node_types.to_markup_id(label_id.split('-'))
        interp['children'] = subterp_sects

        # interp['label] is defined so that the template receives the
        # appropriate markup ID, matching the rendered subterp and not
        # the parent node in the tree
        interp['label'] = label
        layers = list(self.determine_layers(reg_part + '-Interp', version))
        builder = CFRHTMLBuilder(layers)
        builder.tree = interp
        builder.generate_html()
        interp = builder.tree
        interp['html_label'] = html_label
        context['tree'] = {'children': [interp]}
        return context
