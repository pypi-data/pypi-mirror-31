# ------------------------------------------------------------------------------
# Wagtail 1.x style EditHandlers
# ------------------------------------------------------------------------------
from django.utils import timezone
from wagtail.wagtailadmin.edit_handlers import BaseFieldPanel
from .widgets import ExceptionDateInput

# ------------------------------------------------------------------------------
class BaseExceptionDatePanel(BaseFieldPanel):
    object_template = "joyous/edit_handlers/exception_date_object.html"

    def __init__(self, instance=None, form=None):
        super().__init__(instance=instance, form=form)
        widget = self.bound_field.field.widget
        widget.overrides_repeat = self.instance.overrides_repeat
        tz = timezone._get_timezone_name(self.instance.tz)
        if tz != timezone.get_current_timezone_name():
            self.exceptionTZ = tz
        else:
            self.exceptionTZ = None

class ExceptionDatePanel(object):
    def __init__(self, field_name, classname=""):
        self.field_name = field_name
        self.classname = classname

    def bind_to_model(self, model):
        members = {
            'model':      model,
            'field_name': self.field_name,
            'classname':  self.classname,
            'widget':     ExceptionDateInput,
        }
        return type(str('_ExceptionDatePanel'), (BaseExceptionDatePanel,), members)

# ------------------------------------------------------------------------------
