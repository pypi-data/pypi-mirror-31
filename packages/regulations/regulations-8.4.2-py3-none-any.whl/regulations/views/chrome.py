from collections import namedtuple

from django.views.generic.base import TemplateView

from regulations.generator import generator
from regulations.generator.node_types import label_to_text, type_from_label
from regulations.generator.section_url import SectionUrl
from regulations.generator.sidebar.help import Help as HelpSideBar
from regulations.generator.subterp import filter_by_subterp
from regulations.generator.toc import fetch_toc
from regulations.generator.versions import fetch_grouped_history
from regulations.views import utils
from regulations.views.partial_interp import PartialSubterpView
from regulations.views.reg_landing import regulation_exists, get_versions
from regulations.views.reg_landing import regulation as landing_page
from regulations.views.partial import PartialSectionView
from regulations.views.partial_search import PartialSearch
from regulations.views.sidebar import SideBarView
from regulations.views import error_handling


# type: (date, Optional[date], Timeline)
VersionSpan = namedtuple('VersionSpan', ['start', 'end', 'timeline'])


def version_span(history, effective_date):
    """Derive the start and end dates that would include the requested
    effective date. Also include the past/present/future indication for that
    range."""
    asc_history = list(reversed(history))
    start_dates = [h['by_date'] for h in asc_history]
    end_dates = start_dates[1:] + [None]
    for start, end, version_info in zip(start_dates, end_dates, asc_history):
        if effective_date >= start and end is None or effective_date < end:
            return VersionSpan(start, end, version_info['timeline'])


class ChromeView(TemplateView):
    """ Base class for views which wish to include chrome. """
    template_name = 'regulations/chrome.html'
    #   Which view name to use when switching versions
    version_switch_view = 'chrome_section_view'
    sidebar_components = SideBarView.components
    partial_class = None

    def fill_kwargs(self, kwargs):
        """Entrypoint for subclasses to configure the kwargs that will be
        handed down to get_context_data"""
        return kwargs

    def check_tree(self, context):
        """Throw an exception if the requested section doesn't exist"""
        label_id, version = context['label_id'], context['version']
        relevant_tree = generator.get_tree_paragraph(label_id, version)
        if relevant_tree is None:
            raise error_handling.MissingSectionException(label_id, version,
                                                         context)

    def get(self, request, *args, **kwargs):
        """Override GET so that we can catch and propagate any errors in the
        included partial(s)"""

        try:
            return super(ChromeView, self).get(request, *args, **kwargs)
        except BadComponentException as e:
            return e.response
        except error_handling.MissingSectionException as e:
            return error_handling.handle_missing_section_404(
                request, e.label_id, e.version, e.context)
        except error_handling.MissingContentException as e:
            return error_handling.handle_generic_404(request)

    def _assert_good(self, response):
        if response.status_code != 200:
            raise BadComponentException(response)

    def add_main_content(self, context):
        view = self.partial_class()
        view.request = self.request
        context['main_content_context'] = view.get_context_data(**context)
        context['main_content_template'] = view.template_name

    def diff_redirect_label(self, label_id, toc):
        """We only display diffs for sections and appendices. All other types
        of content must be converted to an appropriate diff label"""
        label_parts = label_id.split('-')
        if len(label_parts) == 1:   # whole CFR part. link to first section
            while toc:
                label_id = toc[0]['section_id']
                toc = toc[0].get('sub_toc')
        # We only show diffs for the whole interpretation at once
        elif 'Interp' in label_parts:
            label_id = label_parts[0] + '-Interp'
        # Non-section paragraph; link to the containing section
        elif len(label_parts) > 2:
            label_id = '-'.join(label_parts[:2])
        return label_id

    def set_chrome_context(self, context, reg_part, version):
        context['reg_part'] = reg_part
        context['history'] = fetch_grouped_history(reg_part)

        toc = fetch_toc(reg_part, version)
        for el in toc:
            el['url'] = SectionUrl().of(
                el['index'], version, self.partial_class.sectional_links)
            for sub in el.get('sub_toc', []):
                sub['url'] = SectionUrl().of(
                    sub['index'], version, self.partial_class.sectional_links)
        context['TOC'] = toc

        context['meta'] = utils.regulation_meta(reg_part, version)

        # Throw 404 if regulation doesn't exist
        if not context['meta']:
            raise error_handling.MissingContentException()

        context['version_span'] = version_span(
            context['history'], context['meta']['effective_date'])
        context['version_switch_view'] = self.version_switch_view
        context['diff_redirect_label'] = self.diff_redirect_label(
            context['label_id'], toc)

    def get_context_data(self, **kwargs):
        kwargs = self.fill_kwargs(kwargs)
        context = super(ChromeView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        version = context['version']
        label_id_list = label_id.split('-')
        reg_part = label_id_list[0]
        context['q'] = self.request.GET.get('q', '')
        context['formatted_id'] = label_to_text(label_id_list, True, True)
        context['node_type'] = type_from_label(label_id_list)

        error_handling.check_regulation(reg_part)
        self.set_chrome_context(context, reg_part, version)

        self.check_tree(context)
        self.add_main_content(context)
        context['sidebar_content'] = self.sidebar(label_id, version)

        return context

    def sidebar(self, label_id, version):
        """Generate the sidebar content for this label_id+version. This
        involves passing through to the SideBarView"""
        sidebar_view = SideBarView.as_view(components=self.sidebar_components)
        response = sidebar_view(self.request, label_id=label_id,
                                version=version)
        self._assert_good(response)
        response.render()
        return response.content


class ChromeSubterpView(ChromeView):
    """Corresponding chrome class for subterp partial view"""
    partial_class = PartialSubterpView
    version_switch_view = 'chrome_subterp_view'

    def check_tree(self, context):
        """We can't defer to Chrome's check because Subterps are constructed
        -site side"""
        version, label_id = context['version'], context['label_id']
        label = label_id.split('-')
        reg_part = label[0]

        interp = generator.get_tree_paragraph(reg_part + '-Interp', version)
        if not interp:
            raise error_handling.MissingSectionException(label_id, version,
                                                         context)

        subterp_sects = filter_by_subterp(interp['children'], label, version)
        if not subterp_sects:
            raise error_handling.MissingSectionException(label_id, version,
                                                         context)


class ChromeSearchView(ChromeView):
    """Search results with chrome"""
    template_name = 'regulations/chrome-search.html'
    partial_class = PartialSearch
    sidebar_components = [HelpSideBar]

    def check_tree(self, context):
        pass    # Search doesn't perform this check

    def fill_kwargs(self, kwargs):
        """Get the version for the chrome context"""
        kwargs['version'] = self.request.GET.get('version', '')
        kwargs['skip_count'] = True
        if not kwargs['version']:
            current, _ = get_versions(kwargs['label_id'])
            kwargs['version'] = current['version']
        kwargs['label_id'] = utils.first_section(kwargs['label_id'],
                                                 kwargs['version'])
        return kwargs

    def add_main_content(self, context):
        """Override this so that we have access to the main content's
        results field"""
        super(ChromeSearchView, self).add_main_content(context)
        context['results'] = context['main_content_context']['results']


class ChromeLandingView(ChromeView):
    """Landing page with chrome"""
    template_name = 'regulations/landing-chrome.html'
    partial_class = PartialSectionView  # Needed to know sectional status

    def check_tree(self, context):
        pass    # Landing page doesn't perform this check

    def sidebar(self, label_id, version):
        """Landing pages don't have a sidebar generated this way"""
        return None

    def add_main_content(self, context):
        """Landing page isn't a TemplateView"""
        response = landing_page(self.request, context['reg_part'])
        self._assert_good(response)
        context['main_content'] = response.content

    def fill_kwargs(self, kwargs):
        """Add the version and replace the label_id for the chrome context"""
        reg_part = kwargs['label_id']
        if not regulation_exists(reg_part):
            raise error_handling.MissingContentException()

        current, _ = get_versions(kwargs['label_id'])
        kwargs['version'] = current['version']
        kwargs['label_id'] = utils.first_section(reg_part, current['version'])
        return kwargs


class BadComponentException(Exception):
    """Allows us to propagate errors in loaded partials"""
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "BadComponentException(response=%s)" % repr(self.response)
