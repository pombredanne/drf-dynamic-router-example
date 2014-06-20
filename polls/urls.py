from django.conf.urls import url, patterns, include
from rest_framework import viewsets
from views import PollViewSet, ChoiceViewSet

from rest_framework import routers
import inspect
class DynamicRouter(routers.DefaultRouter):
    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.

        Returns a list of the Route namedtuple.
        """

        known_actions = routers.flatten([route.mapping.values() for route in self.routes])

        # Determine any `@action` or `@link` decorated methods on the viewset
        dynamic_route_mappings = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @action or @link decorator on '
                                               'method "%s" as it is an existing route' % methodname)
                httpmethods = [method.lower() for method in httpmethods]
                dynamic_route_mappings.append((httpmethods, methodname))


        dynamic_routes = []
        standard_routes = []
        dyn_url_pattern = r'^{prefix}/{methodname}{trailing_slash}$'
        for route in self.routes:
            if route.mapping == {'{httpmethod}': '{methodname}'}:
                # Dynamic routes (@link or @action decorator)
                for httpmethods, methodname in dynamic_route_mappings:
                    initkwargs = route.initkwargs.copy()
                    view_fn = getattr(viewset, methodname)
                    initkwargs.update(view_fn.kwargs)

                    # Does the dynamic route have a pk argument?
                    pk_in_args = 'pk' in inspect.getargspec(view_fn).args

                    if pk_in_args:
                        # Default DRF behavior: prefix/pk/methodname
                        dynamic_routes.append(routers.Route(
                            url=routers.replace_methodname(route.url, methodname),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=routers.replace_methodname(route.name, methodname),
                            initkwargs=initkwargs,
                        ))
                    else:
                        # No pk? Then map to prefix/methodname
                        dynamic_routes.append(routers.Route(
                            url=routers.replace_methodname(dyn_url_pattern, methodname),
                            mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                            name=routers.replace_methodname('{basename}-{methodname}', methodname),
                            initkwargs=initkwargs,
                        ))
            else:
                # Standard route
                standard_routes.append(route)

        return dynamic_routes + standard_routes

router = DynamicRouter()
router.register(r'polls', PollViewSet)
router.register(r'choices', ChoiceViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
