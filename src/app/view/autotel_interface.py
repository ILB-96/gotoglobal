# coding:utf-8

from services.fluent.qfluentwidgets.components.widgets.label import StrongBodyLabel, SubtitleLabel

from .gallery_interface import GalleryInterface
from ..common.config import cfg
from .table_frame import TableFrame

class AutotelInterface(GalleryInterface):
    """ View interface """

    def __init__(self, parent=None):
        super().__init__(
            parent=parent
        )
        self.setObjectName('AutotelInterface')
        self.long_rides_title = SubtitleLabel('Autotel Long Rides', self)
        self.batteries_title = SubtitleLabel('Autotel Batteries', self)
        long_rides_columns=[self.tr("Ride ID"), self.tr("Driver Name"), self.tr("Duration"), self.tr("Location"), self.tr("Comment")]
        batteries_columns=[self.tr("Ride ID"), self.tr("License Plate"), self.tr("Battery"), self.tr("Location"), self.tr("Comment")]
        self.long_rides_table = TableFrame(columns=long_rides_columns, titleWidget=self.long_rides_title, parent=self)
        self.batteries_table = TableFrame(columns=batteries_columns, titleWidget=self.batteries_title, parent=self)

        
        self.vBoxLayout.addWidget(self.long_rides_title)
        self.vBoxLayout.addWidget(self.long_rides_table)
        self.vBoxLayout.addWidget(self.batteries_title)
        self.vBoxLayout.addWidget(self.batteries_table)
        
    def _remove(self, widget):
        if widget is not None:
            self.vBoxLayout.removeWidget(widget)
            widget.setParent(None)  # Detach from the UI
            widget.deleteLater()
            
    def removeWidgets(self):
        """ Remove all widgets from the interface """
        if not cfg.get(cfg.long_rides):
            self._remove(self.long_rides_title)
            self._remove(self.long_rides_table)
        if not cfg.get(cfg.batteries):
            self._remove(self.batteries_title)
            self._remove(self.batteries_table)
