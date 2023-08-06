from itertools import dropwhile, takewhile

from regulations.generator.toc import fetch_toc


def filter_by_subterp(nodes, subterp_label, version):
    """Given an interp node (e.g. a node with label ['1005', 'Interp']),
    remove all irrelevant sub-nodes. Note that stripping out nodes is more
    efficient than compiling nodes when API calls are involved. We use
    takewhile and dropwhile in case extra, non-node interpretations are in
    the range"""

    def is_section(n):
        return n['label'][1].isdigit()

    def not_section(n):
        return not is_section(n)

    if subterp_label[1:] == ['Subpart', 'Interp']:      # Empty part
        skip_intros = dropwhile(not_section, nodes)
        sections = takewhile(is_section, skip_intros)
        return list(sections)
    elif subterp_label[1:] == ['Appendices', 'Interp']:  # Appendices
        skip_intros = dropwhile(not_section, nodes)
        skip_sections = dropwhile(is_section, skip_intros)
        return list(skip_sections)
    else:   # A Subpart. Most costly as we need to know the toc
        subpart_label = subterp_label[:-1]
        toc = fetch_toc(subterp_label[0], version)
        toc = list(dropwhile(
            lambda el: el['index'] != subpart_label,    # not subpart
            toc))
        if toc:
            sections = set(tuple(el['index'] + ['Interp'])
                           for el in toc[0]['sub_toc'])
            relevant_interps = dropwhile(
                lambda el: tuple(el['label']) not in sections,   # not relevant
                nodes)

            other_sections = set()
            for el in toc[1:]:
                other_sections.add(tuple(el['index'] + ['Interp']))
                for sub in el.get('sub_toc', []):
                    other_sections.add(tuple(sub['index'] + ['Interp']))
            relevant_interps = takewhile(
                lambda n: tuple(n['label']) not in other_sections,  # relevant
                relevant_interps)

            return list(relevant_interps)
    # Couldn't find the subpart - wrong label? - implicit return None
