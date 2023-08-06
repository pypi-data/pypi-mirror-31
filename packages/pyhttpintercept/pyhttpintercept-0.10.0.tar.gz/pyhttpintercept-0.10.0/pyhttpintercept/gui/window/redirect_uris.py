# encoding: utf-8

import logging_helper
from uiutil import ChildWindow
from uiutil.tk_names import NSEW
from ..frame.redirect_uris import RedirectURIConfigFrame

logging = logging_helper.setup_logging()


class RedirectURIConfigWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        super(RedirectURIConfigWindow, self).__init__(*args,
                                                      **kwargs)

    def _draw_widgets(self):
        self.title(u"Redirect URI Configuration")

        self.config = RedirectURIConfigFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)
