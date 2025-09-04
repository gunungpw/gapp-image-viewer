import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QScrollArea,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtGui import QPixmap, QImageReader, QPalette, QAction
from PySide6.QtCore import Qt, QSize


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gapp-image-viewer")
        self.scale_factor = 1.0
        self.original_pixmap = None  # Store the original pixmap

        # Create main widget and layout
        self.image_label = QLabel()
        self.image_label.setBackgroundRole(QPalette.ColorRole.Base)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.image_label.setScaledContents(False)  # Disable scaled contents

        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.ColorRole.Dark)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setVisible(False)
        self.setCentralWidget(self.scroll_area)

        # Create menu
        self.create_menus()

        # Set initial window size
        self.resize(800, 600)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("&View")

        zoom_in_action = QAction("Zoom &In (25%)", self)
        zoom_in_action.setShortcut("Ctrl+Shift++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom &Out (25%)", self)
        zoom_out_action.setShortcut("Ctrl+Shift+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        normal_size_action = QAction("&Normal Size", self)
        normal_size_action.setShortcut("Ctrl+S")
        normal_size_action.triggered.connect(self.normal_size)
        view_menu.addAction(normal_size_action)

        fit_to_window_action = QAction("&Fit to Window", self)
        fit_to_window_action.setShortcut("Ctrl+F")
        fit_to_window_action.setCheckable(True)
        fit_to_window_action.triggered.connect(self.fit_to_window)
        view_menu.addAction(fit_to_window_action)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_name:
            reader = QImageReader(file_name)
            reader.setAutoTransform(True)
            image = reader.read()

            if image.isNull():
                QMessageBox.information(
                    self, "Image Viewer", f"Cannot load {file_name}"
                )
                return

            self.original_pixmap = QPixmap.fromImage(image)
            self.image_label.setPixmap(self.original_pixmap)
            self.scroll_area.setVisible(True)
            self.scale_factor = 1.0
            self.update_image()
            self.scroll_area.setWidgetResizable(False)

    def zoom_in(self):
        self.scale_image(1.25)

    def zoom_out(self):
        self.scale_image(0.8)

    def normal_size(self):
        if self.original_pixmap:
            self.scale_factor = 1.0
            self.update_image()
            self.scroll_area.setWidgetResizable(False)

    def fit_to_window(self):
        fit_to_window = self.sender().isChecked()
        self.scroll_area.setWidgetResizable(fit_to_window)
        if not fit_to_window and self.original_pixmap:
            self.update_image()

    def scale_image(self, factor):
        if self.original_pixmap:
            self.scale_factor *= factor
            # Limit zoom range to prevent extreme scaling
            self.scale_factor = max(0.1, min(self.scale_factor, 10.0))
            self.update_image()

    def update_image(self):
        if self.original_pixmap:
            new_size = QSize(
                self.original_pixmap.size().width() * self.scale_factor,
                self.original_pixmap.size().height() * self.scale_factor,
            )
            scaled_pixmap = self.original_pixmap.scaled(
                new_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.adjustSize()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())
