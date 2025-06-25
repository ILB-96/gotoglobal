# coding:utf-8

from services.fluent.qfluentwidgets import SubtitleLabel
from .table_frame import TableFrame

from .gallery_interface import GalleryInterface
from ..common.config import cfg


class GotoInterface(GalleryInterface):
    """ View interface """

    def __init__(self, parent=None):
        super().__init__(
            parent=parent
        )
        self.setObjectName('viewInterface')
        self.late_rides_title = SubtitleLabel('Goto Late Rides', self)
        late_rides_columns=[self.tr("Ride ID"), self.tr("End Time"), self.tr("Future Ride"), self.tr("Future Ride Time"), self.tr("Comment")]
        self.late_rides_table = TableFrame(columns=late_rides_columns, titleWidget=self.late_rides_title, parent=self)
        self.vBoxLayout.addWidget(self.late_rides_title)
        self.vBoxLayout.addWidget(self.late_rides_table)
        
    def _remove(self, widget):
        if widget is not None:
            self.vBoxLayout.removeWidget(widget)
            widget.setParent(None)  # Detach from the UI
            widget.deleteLater()
            
    def removeWidgets(self):
        """ Remove all widgets from the interface """
        if not cfg.get(cfg.late_rides):
            self._remove(self.late_rides_title)
            self._remove(self.late_rides_table)
