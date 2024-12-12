from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QComboBox,
    QProgressBar,
    QHBoxLayout,
    QApplication,
    QFrame,
    QSizePolicy,
    QMenu,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QAction, QKeySequence
from checksum_calculator import ChecksumCalculator
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checksum Verifier - Secure File Verification")
        # self.setMinimumSize(900, 600)  # Slightly larger minimum size
        # Maximize window and disable resizing
        self.showMaximized()
        self.setFixedSize(self.size())
        self.calculator = ChecksumCalculator()
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #ffffff, stop:1 #f0f0f0);
            }
            QWidget {
                color: #333333;
            }
        """
        )
        # Add icon font
        self.icon_font = QFont()
        self.icon_font.setPointSize(16)
        self.current_file = None  # Add this line
        self.feedback_timer = QTimer()
        self.feedback_timer.timeout.connect(self.reset_feedback)
        self.feedback_timer.setSingleShot(True)

        # Set window icon
        self.setWindowIcon(QIcon("icon.png"))  # You'll need to provide an icon file

        # Add menu bar
        self.create_menu_bar()

        # Initialize shortcuts
        self.setup_shortcuts()

        self.setup_ui()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.browse_file)
        file_menu.addAction(open_action)

        clear_action = QAction("&Clear", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.clear_form)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_shortcuts(self):
        # Add copy shortcut
        self.copy_shortcut = QKeySequence(QKeySequence.StandardKey.Copy)
        self.verify_shortcut = QKeySequence("Ctrl+Return")  # For verify action

    def show_about(self):
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "About Checksum Verifier",
            """<h3>Checksum Verifier</h3>
            <p>A secure tool for calculating and verifying file checksums.</p>
            <p>Supported algorithms: MD5, SHA-1, SHA-256, SHA-512</p>
            <p><small>Version 1.0</small></p>""",
        )

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Add container frame
        container = QFrame()
        container.setStyleSheet(
            """
            QFrame {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """
        )
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(40, 40, 40, 40)

        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        # Drop area with unicode icon
        self.drop_label = QLabel(
            "📄\n\nDrop file here\nor click Browse to select"
        )  # Extra newline for spacing
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #333333;
                border-radius: 12px;
                padding: 40px;
                background: #ffffff;
                font-size: 16px;
                color: #333333;
                margin: 10px;
            }
            QLabel:hover {
                background: #f5f5f5;
                border-color: #000000;
            }
        """
        )
        self.drop_label.setMinimumHeight(150)  # Ensure enough vertical space

        # Add file info display
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet(
            """
            QLabel {
                padding: 15px;
                color: #666666;
                font-style: italic;
                font-size: 13px;
                border-radius: 5px;
                background: rgba(0, 0, 0, 0.03);
            }
        """
        )

        # Browse button with unicode icon
        self.browse_button = QPushButton("📂 Browse for file...")  # Folder icon
        self.browse_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #333333;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #cccccc;
                background-color: #f5f5f5;
            }
        """
        )
        self.browse_button.clicked.connect(self.browse_file)

        # Hash type selector
        self.hash_combo = QComboBox()
        self.hash_combo.addItems(["MD5", "SHA-1", "SHA-256", "SHA-512"])
        self.hash_combo.setStyleSheet(
            """
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #333333;
                border-radius: 6px;
                background: white;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:hover {
                border-color: #000000;
                background: #fafafa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #333333;
                margin-top: 2px;
            }
        """
        )
        self.hash_combo.currentTextChanged.connect(self.hash_changed)

        # Add verify input early in the setup
        self.verify_input = QLineEdit()
        self.verify_input.setPlaceholderText("Paste checksum to verify...")
        self.verify_input.setStyleSheet(
            """
            QLineEdit {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-family: monospace;
                font-size: 14px;
                background: white;
                color: #333333;
            }
            QLineEdit:focus {
                border-color: #333333;
                background: #ffffff;
            }
        """
        )
        self.verify_input.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        # Add verify button early in the setup
        self.verify_button = QPushButton("✓ Verify")
        self.verify_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #333333;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #cccccc;
                background-color: #f5f5f5;
            }
        """
        )
        self.verify_button.clicked.connect(self.verify_checksum)

        # Create horizontal layout for result and copy button
        result_container = QFrame()
        result_container.setStyleSheet(
            """
            QFrame {
                background: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
        """
        )
        result_layout = QHBoxLayout(result_container)
        result_layout.setContentsMargins(10, 10, 10, 10)
        result_layout.setSpacing(15)  # Add space between result and copy button

        # Result display (modify existing)
        self.result_label = QLabel("Checksum will appear here")
        self.result_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.result_label.setStyleSheet(
            """
            QLabel {
                padding: 15px;
                background: #fafafa;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-family: monospace;
                font-size: 15px;
                color: #333333;
                min-height: 20px;
                letter-spacing: 1px;
            }
        """
        )

        # Add copy button
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #333333;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #cccccc;
                background-color: #f5f5f5;
            }
        """
        )
        self.copy_button.clicked.connect(self.copy_result)
        self.copy_button.setEnabled(False)

        result_layout.addWidget(self.result_label)
        result_layout.addWidget(self.copy_button)

        # Add clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setStyleSheet(
            """
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #333333;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #cccccc;
                background-color: #f5f5f5;
            }
        """
        )
        self.clear_button.clicked.connect(self.clear_form)

        # Modify layout additions
        layout.addWidget(self.drop_label, stretch=2)
        layout.addWidget(self.file_info_label)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.hash_combo)
        layout.addWidget(result_container)  # Add the horizontal layout
        layout.addWidget(self.verify_input)

        # Create button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)  # Add space between buttons
        button_layout.addWidget(self.verify_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()  # Push buttons to the left
        layout.addLayout(button_layout)

        # Progress bar initialization
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                height: 25px;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 4px;
            }
        """
        )
        self.progress_bar.hide()

        layout.addWidget(self.progress_bar)

        # Add status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #666666;
                font-size: 13px;
                padding: 5px;
                border-radius: 3px;
                background: transparent;
            }
        """
        )
        layout.addWidget(self.status_label)

        # Add stretch to main layout to push content up
        layout.addStretch()

        # Setup drag and drop
        self.setAcceptDrops(True)

        # Add tooltips
        self.browse_button.setToolTip("Open file browser (Ctrl+O)")
        self.hash_combo.setToolTip("Select hash algorithm")
        self.verify_button.setToolTip("Verify checksum (Ctrl+Return)")
        self.copy_button.setToolTip("Copy to clipboard (Ctrl+C)")
        self.clear_button.setToolTip("Clear all fields (Ctrl+L)")
        self.verify_input.setToolTip("Enter checksum to verify")

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select file")
        if filename:
            self.calculate_checksum(filename)

    def calculate_checksum(self, filepath):
        self.progress_bar.setMaximum(0)  # Show indeterminate progress
        self.progress_bar.show()
        self.show_status("Calculating checksum...", "#007bff")
        QApplication.processEvents()  # Force UI update

        try:
            self.current_file = filepath
            hash_type = self.hash_combo.currentText()

            # Update file info
            file_size = os.path.getsize(filepath)
            file_name = os.path.basename(filepath)
            size_str = self.format_size(file_size)
            self.file_info_label.setText(f"File: {file_name} ({size_str})")

            result = self.calculator.calculate(filepath, hash_type)
            self.result_label.setText(result)
            self.copy_button.setEnabled(True)
            self.show_status(f"Checksum calculated using {hash_type}", "#28a745")
        except Exception as e:
            self.show_status(f"Error: {str(e)}", "#dc3545")
        finally:
            self.progress_bar.hide()
            QApplication.processEvents()  # Ensure UI is updated

    def format_size(self, size):
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0

    def verify_checksum(self):
        input_hash = self.verify_input.text().strip().lower()
        current_hash = self.result_label.text().strip().lower()

        if input_hash == current_hash:
            self.result_label.setStyleSheet(
                """
                QLabel {
                    padding: 15px;
                    background: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 14px;
                    color: #155724;
                }
            """
            )
            self.show_status("Checksum verified successfully! ✓", "#28a745")
        else:
            self.result_label.setStyleSheet(
                """
                QLabel {
                    padding: 15px;
                    background: #f8d7da;
                    border: 2px solid #dc3545;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 14px;
                    color: #721c24;
                }
            """
            )
            self.show_status("Checksum verification failed! ✗", "#dc3545")

    def copy_result(self):
        if self.result_label.text() != "Checksum will appear here":
            clipboard = QApplication.clipboard()
            clipboard.setText(self.result_label.text())

            # Visual feedback with transparent green
            self.copy_button.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(40, 167, 69, 0.2);
                    color: #000;
                    border: 2px solid #28a745;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 100px;
                }
            """
            )
            self.copy_button.setText("📋 Copied!")
            self.show_status("Checksum copied to clipboard!", "#28a745")

            QTimer.singleShot(1000, self.reset_copy_button)

    def reset_copy_button(self):
        self.copy_button.setStyleSheet(self.default_button_style())
        self.copy_button.setText("📋 Copy")

    def clear_form(self):
        # Visual feedback animation
        self.result_label.setStyleSheet(
            """
            QLabel {
                padding: 15px;
                background: #fff3cd;
                border: 2px solid #ffeeba;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
                color: #856404;
            }
        """
        )
        QTimer.singleShot(300, self._complete_clear)
        self.show_status("Form cleared", "#856404")

    def _complete_clear(self):
        self.result_label.setText("Checksum will appear here")
        self.verify_input.clear()
        self.file_info_label.setText("No file selected")
        self.current_file = None
        self.copy_button.setEnabled(False)
        self.result_label.setStyleSheet(self.default_label_style())

    def default_button_style(self):
        return """
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #333333;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #333333;
                color: white;
                border-color: #333333;
            }
            QPushButton:pressed {
                background-color: #000000;
                color: white;
            }
            QPushButton:disabled {
                border-color: #cccccc;
                color: #cccccc;
                background-color: #f5f5f5;
            }
        """

    def default_label_style(self):
        return """
            QLabel {
                padding: 15px;
                background: white;
                border: 2px solid #333333;
                border-radius: 5px;
                font-family: monospace;
                font-size: 14px;
                color: #333333;
            }
        """

    def hash_changed(self):
        if self.current_file:
            self.calculate_checksum(self.current_file)
            self.show_status("Hash algorithm changed", "#333333")

    def show_status(self, message, color="#333333"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                padding: 8px 12px;
                border-radius: 4px;
                background: rgba(0, 0, 0, 0.05);
                font-weight: bold;
            }}
        """
        )
        self.feedback_timer.start(3000)  # Show status for 3 seconds

    def reset_feedback(self):
        self.status_label.setText("")
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #666666;
                font-size: 13px;
                padding: 5px;
                border-radius: 3px;
                background: transparent;
            }
        """
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self.drop_label.setStyleSheet(
                """
                QLabel {
                    border: 3px dashed #4CAF50;
                    border-radius: 12px;
                    padding: 40px;
                    background: #E8F5E9;
                    font-size: 16px;
                    color: #2E7D32;
                }
            """
            )
            self.show_status("Release to calculate checksum", "#4CAF50")
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.drop_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #333333;
                border-radius: 12px;
                padding: 40px;
                background: #ffffff;
                font-size: 16px;
                color: #333333;
            }
        """
        )
        self.status_label.clear()

    def dropEvent(self, event: QDropEvent):
        files = event.mimeData().urls()
        if files:
            filepath = files[0].toLocalFile()
            self.calculate_checksum(filepath)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_result()
        elif (
            event.key() == Qt.Key.Key_Return
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self.verify_checksum()
        super().keyPressEvent(event)
