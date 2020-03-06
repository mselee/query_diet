from django.dispatch import Signal

from query_diet import context

pre_track = Signal(providing_args=["tracker"])
post_track = Signal(providing_args=["tracker"])


class TrackerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with context.tracker.scoped() as tracker:
            pre_track.send(sender=self.__class__, tracker=tracker)
            response = self.get_response(request)
            post_track.send(sender=self.__class__, tracker=tracker)

        return response
