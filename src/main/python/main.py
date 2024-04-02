from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QProgressBar, QGroupBox, \
    QComboBox, QSizePolicy, QToolButton, QMessageBox, QFileDialog, QRadioButton

import sys
import hid
import struct
import configparser
import time
import threading
import traceback
import webbrowser
import os

# TODO: dry-run support to ensure flashing doesn't crash

RESPONSE_LEN = 64
MAX_FIRMWARE_SN32F260 = 30 * 1024  # 30K
MAX_FIRMWARE_SN32F240 = 64 * 1024  # 64K Also 240B
MAX_FIRMWARE = MAX_FIRMWARE_SN32F260
QMK_OFFSET_DEFAULT = 0x200


CMD_BASE = 0x55AA00
CMD_INIT = CMD_BASE + 1
CMD_PREPARE = CMD_BASE + 5
CMD_REBOOT = CMD_BASE + 7

EXPECTED_STATUS = 0xFAFAFAFA

DEVICE_DESC = {
    # keyboards in bootloader mode:
    (0x0c45, 0x7010): "SN32F268F (bootloader)",  # 0x200
    (0x0c45, 0x7040): "SN32F248B (bootloader)",  # 0x0
    (0x0c45, 0x7900): "SN32F248 (bootloader)",   # 0x0

    # keyboards in normal mode:
    (0x05ac, 0x024f): "Apple Keyboard / Keychron / Flashquark Horizon Z",
    (0x05ac, 0x0250): "Apple Keyboard / Keychron",
    (0x05ac, 0x0256): "Apple Keyboard / Ajazz K870T / RAKK Lam-Ang Pro / Miller GM807",
    (0x0c45, 0x652f): "Glorious GMMK / Tecware Phantom",
    (0x0c45, 0x5004): "Redragon",
    (0x0c45, 0x5104): "Redragon",
    (0x0c45, 0x766b): "Kemove",
    (0x0c45, 0x7698): "Womier",
    (0x0C45, 0x7903): "Ajazz",
    (0x0C45, 0x8006): "Sharkoon / Cloudnine",
    (0x0c45, 0x8008): "Cloudnine",
    (0x0c45, 0x8073): "Cloudnine",
    (0x0C45, 0x8508): "SPCGear",
    (0x0C45, 0x8513): "Sharkoon",
    (0x320f, 0x5013): "Akko",
    (0x320f, 0x5041): "Designed By GG",
    (0x3299, 0x4E58): "SPCGear",
    (0x3299, 0x4E5B): "SPCGear",
    (0x3434, 0xfe00): "Keychron K1 ANSI",
    (0x3434, 0xfe01): "Keychron K1 ISO",
    (0x3434, 0xfe02): "Keychron K2 ANSI",
    (0x3434, 0xfe03): "Keychron K2 ISO",
    (0x3434, 0xfe04): "Keychron K3 ANSI",
    (0x3434, 0xfe05): "Keychron K3 ISO",
    (0x3434, 0xfe06): "Keychron K4 ANSI",
    (0x3434, 0xfe07): "Keychron K4 ISO",
    (0x3434, 0xfe08): "Keychron K5 ANSI",
    (0x3434, 0xfe09): "Keychron K5 ISO",
    (0x3434, 0xfe0a): "Keychron K6 ANSI",
    (0x3434, 0xfe0b): "Keychron K6 ISO",
    (0x3434, 0xfe0c): "Keychron K7 ANSI",
    (0x3434, 0xfe0d): "Keychron K7 ISO",
    (0x3434, 0xfe0e): "Keychron K8 ANSI",
    (0x3434, 0xfe0f): "Keychron K8 ISO",
    (0x3434, 0xfe10): "Keychron K9 ANSI",
    (0x3434, 0xfe11): "Keychron K9 ISO",
    (0x3434, 0xfe12): "Keychron K10 ANSI",
    (0x3434, 0xfe13): "Keychron K10 ISO",
    (0x3434, 0xfe14): "Keychron K11 ANSI",
    (0x3434, 0xfe15): "Keychron K11 ISO",
    (0x3434, 0xfe16): "Keychron K12 ANSI",
    (0x3434, 0xfe17): "Keychron K12 ISO",
    (0x3434, 0xfe18): "Keychron K13 ANSI",
    (0x3434, 0xfe19): "Keychron K13 ISO",
    (0x3434, 0xfe1a): "Keychron K14 ANSI",
    (0x3434, 0xfe1b): "Keychron K14 ISO",
    (0x3434, 0xfe1c): "Keychron K15 ANSI",
    (0x3434, 0xfe1d): "Keychron K15 ISO",
    (0x3434, 0xfe1e): "Keychron K16 ANSI",
    (0x3434, 0xfe1f): "Keychron K16 ISO",
    (0x3434, 0xfe20): "Keychron C1 ANSI",
    (0x3434, 0xfe21): "Keychron C1 ISO",
    (0x3434, 0xfe22): "Keychron C2 ANSI",
    (0x3434, 0xfe23): "Keychron C2 ISO",
    (0x3434, 0xfe24): "Keychron C3 ANSI",
    (0x3434, 0xfe25): "Keychron C3 ISO",
    (0x3434, 0xfe26): "Keychron C4 ANSI",
    (0x3434, 0xfe27): "Keychron C4 ISO",
    (0x3434, 0xfe28): "Keychron C5 ANSI",
    (0x3434, 0xfe29): "Keychron C5 ISO",
    (0x3434, 0xfe2a): "Keychron C6 ANSI",
    (0x3434, 0xfe2b): "Keychron C6 ISO",
    (0x3434, 0xfe2c): "Keychron C7 ANSI",
    (0x3434, 0xfe2d): "Keychron C7 ISO",
    (0x3434, 0xfe2e): "Keychron C8 ANSI",
    (0x3434, 0xfe2f): "Keychron C8 ISO",
    (0x3434, 0xfe30): "Keychron C9 ANSI",
    (0x3434, 0xfe31): "Keychron C9 ISO",
    (0x3434, 0xfe32): "Keychron C10 ANSI",
    (0x3434, 0xfe33): "Keychron C10 ISO",
    (0x3434, 0xfe34): "Keychron C11 ANSI",
    (0x3434, 0xfe35): "Keychron C11 ISO",
    (0x3434, 0xfe36): "Keychron C12 ANSI",
    (0x3434, 0xfe37): "Keychron C12 ISO",
    (0x3434, 0xfe38): "Keychron C13 ANSI",
    (0x3434, 0xfe39): "Keychron C13 ISO",
    (0x3434, 0xfe3a): "Keychron C14 ANSI",
    (0x3434, 0xfe3b): "Keychron C14 ISO",
    (0x3434, 0xfe3c): "Keychron C15 ANSI",
    (0x3434, 0xfe3d): "Keychron C15 ISO",
    (0x3434, 0xfe3e): "Keychron C16 ANSI",
    (0x3434, 0xfe3f): "Keychron C16 ISO",
    (0x3938, 0x1205): "Onn KMF Mechanical Gaming Keyboard",
    (0x09da, 0x322c): "A4Tech Generic Keyboard",
    (0x046a, 0x00df): "Cherry MX 10.0N RGB",
}

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]

def hid_set_feature(dev, report):
    if len(report) > 64:
        raise RuntimeError("report must be less than 64 bytes")
    report += b"\x00" * (64 - len(report))

    # add 00 at start for hidapi report id
    dev.send_feature_report(b"\x00" + report)


def hid_get_feature(dev):
    # strip 00 at start for hidapi report id
    return dev.get_feature_report(0, RESPONSE_LEN + 1)[1:]


def console_progress(msg, progress):
    print("{}: {:.2f}%".format(msg, 100 * progress))


def console_complete():
    pass


def console_error(msg):
    print("Error: {}".format(msg))


def cmd_flash(dev, offset, firmware, progress_cb=console_progress, complete_cb=console_complete, error_cb=console_error, skip_size_check=False):
    while len(firmware) % 64 != 0:
        firmware += b"\x00"

    if(skip_size_check == False):
        if len(firmware) + offset > MAX_FIRMWARE:
            return error_cb("Firmware is too large to flash")

    # 1) Initialize
    progress_cb("Initializing device", 0)
    hid_set_feature(dev, struct.pack("<I", CMD_INIT))
    resp = bytes(hid_get_feature(dev))
    if len(resp) != RESPONSE_LEN:
        return error_cb("Failed to initialize: got response of length {}, expected {}".format(len(resp), RESPONSE_LEN))
    cmd, status = struct.unpack("<II", resp[0:8])
    if cmd != CMD_INIT:
        return error_cb("Failed to initialize: response cmd is 0x{:08X}, expected 0x{:08X}".format(cmd, CMD_INIT))
    progress_cb("Initializing device", 0)

    # 2) Prepare for flash
    progress_cb("Preparing for flash", 0)
    hid_set_feature(dev, struct.pack(
        "<III", CMD_PREPARE, offset, len(firmware) // 64))
    resp = bytes(hid_get_feature(dev))
    if len(resp) != RESPONSE_LEN:
        return error_cb("Failed to prepare: got response of length {}, expected {}".format(len(resp), RESPONSE_LEN))
    cmd, status = struct.unpack("<II", resp[0:8])
    if cmd != CMD_PREPARE:
        return error_cb("Failed to prepare: response cmd is 0x{:08X}, expected 0x{:08X}".format(cmd, CMD_PREPARE))
    if status != EXPECTED_STATUS:
        return error_cb("Failed to prepare: response status is 0x{:08X}, expected 0x{:08X}".format(status, EXPECTED_STATUS))
    progress_cb("Preparing for flash", 1)

    # 3) Flash
    progress_cb("Flashing", 0)
    for addr in range(0, len(firmware), 64):
        chunk = firmware[addr:addr+64]
        hid_set_feature(dev, chunk)

        progress_cb("Flashing", (addr + 64) / len(firmware))

    # 4) Reboot
    hid_set_feature(dev, struct.pack("<I", CMD_REBOOT))
    complete_cb()


def cmd_reboot_evision(dev, progress_cb=console_progress, complete_cb=console_complete, error_cb=console_error):
    progress_cb("Reboot to bootloader", 0)
    hid_set_feature(dev, struct.pack("<II", 0x5AA555AA, 0xCC3300FF))
    progress_cb("Reboot to bootloader", 0.5)
    time.sleep(5)
    complete_cb()

def cmd_reboot_hfd(dev, progress_cb=console_progress, complete_cb=console_complete, error_cb=console_error):
    progress_cb("Reboot to bootloader", 0)
    hid_set_feature(dev, struct.pack("<II", 0x5A8942AA, 0xCC6271FF))
    progress_cb("Reboot to bootloader", 0.5)
    time.sleep(5)
    complete_cb()

class MainWindow(QWidget):

    progress_signal = pyqtSignal(object)
    complete_signal = pyqtSignal(object)
    error_signal = pyqtSignal(object)


    def __init__(self):
        super().__init__()

        self.dev = None


        self.device_descs = DEVICE_DESC.copy()

        self.qmk_offset = QMK_OFFSET_DEFAULT

        self.progress_signal.connect(self._on_progress)
        self.complete_signal.connect(self._on_complete)
        self.error_signal.connect(self._on_error)

        lbl_warning = QLabel(
            "<font color='red'><b>Make sure jumploader is installed before you flash QMK</b></font>")
        lbl_warning.setWordWrap(True)

        layout_offset = QHBoxLayout()
        self.rbtn_qmk_offset_200 = QRadioButton("0x200")
        self.rbtn_qmk_offset_200.setChecked(True)
        self.rbtn_qmk_offset_200.toggled.connect(
            lambda: self.on_toggle_offset(self.rbtn_qmk_offset_200))
        self.rbtn_qmk_offset_0 = QRadioButton("0x00")
        self.rbtn_qmk_offset_0.toggled.connect(
            lambda: self.on_toggle_offset(self.rbtn_qmk_offset_0))
        layout_offset.addWidget(self.rbtn_qmk_offset_200)
        layout_offset.addWidget(self.rbtn_qmk_offset_0)
        group_qmk_offset = QGroupBox("qmk offset")
        group_qmk_offset.setLayout(layout_offset)

        btn_flash_qmk = QPushButton("Flash QMK...")
        btn_flash_qmk.clicked.connect(self.on_click_flash_qmk)

        lbl_help = QLabel(
            "After jumploader is installed, hold Backspace(Enter for GMMK keyboards) while plugging in the keyboard to start in bootloader mode.")
        lbl_help.setWordWrap(True)

        btn_reboot_bl_evision = QPushButton("Reboot to Bootloader [eVision]")
        btn_reboot_bl_evision.clicked.connect(self.on_click_reboot_evision)
        btn_reboot_bl_hfd = QPushButton("Reboot to Bootloader [HFD]")
        btn_reboot_bl_hfd.clicked.connect(self.on_click_reboot_hfd)
        btn_flash_jumploader = QPushButton("Flash Jumploader")
        btn_flash_jumploader.clicked.connect(self.on_click_flash_jumploader)
        btn_restore_stock = QPushButton("Revert to Stock Firmware")
        btn_restore_stock.clicked.connect(self.on_click_revert)
        btn_download_stock_fw = QPushButton("Download Stock Firmware")
        btn_download_stock_fw.clicked.connect(self.on_download_click)
        if get_platform() == "Linux":
            if os.geteuid() == 0:
                btn_download_stock_fw.setEnabled(False)


        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress_label = QLabel("Ready")

        layout_device_type = QHBoxLayout()
        self.rbtn_device_type_240 = QRadioButton("SN32F24x")
        self.rbtn_device_type_240.toggled.connect(
            lambda: self.on_toggle_device_type(self.rbtn_device_type_240))
        self.rbtn_device_type_260 = QRadioButton("SN32F26x")
        self.rbtn_device_type_260.setChecked(True)
        self.rbtn_device_type_260.toggled.connect(
            lambda: self.on_toggle_device_type(self.rbtn_device_type_260))
        layout_device_type.addWidget(self.rbtn_device_type_260)
        layout_device_type.addWidget(self.rbtn_device_type_240)

        self.combobox_devices = QComboBox()
        btn_refresh_devices = QToolButton()
        btn_refresh_devices.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn_refresh_devices.setText("Refresh")
        btn_refresh_devices.clicked.connect(self.on_click_refresh)

        devices_layout = QHBoxLayout()
        devices_layout.addWidget(self.combobox_devices)
        devices_layout.addWidget(btn_refresh_devices)

        device_group_layout = QVBoxLayout()
        device_group_layout.addLayout(layout_device_type)
        device_group_layout.addLayout(devices_layout)

        group_device = QGroupBox("Device")
        group_device.setLayout(device_group_layout)

        layout_qmk = QVBoxLayout()
        layout_qmk.setAlignment(Qt.AlignTop)
        layout_qmk.addWidget(lbl_warning)
        layout_qmk.addWidget(group_qmk_offset)
        layout_qmk.addWidget(btn_flash_qmk)
        layout_qmk.addWidget(lbl_help)

        layout_stock = QVBoxLayout()
        layout_stock.setAlignment(Qt.AlignTop)
        layout_stock.addWidget(btn_reboot_bl_evision)
        layout_stock.addWidget(btn_reboot_bl_hfd)
        layout_stock.addWidget(btn_flash_jumploader)
        layout_stock.addWidget(btn_restore_stock)
        layout_stock.addWidget(btn_download_stock_fw)

        layout_progress = QVBoxLayout()
        layout_progress.addWidget(self.progress_label)
        layout_progress.addWidget(self.progress)

        group_qmk = QGroupBox("QMK")
        group_qmk.setLayout(layout_qmk)

        group_stock = QGroupBox("Stock")
        group_stock.setLayout(layout_stock)

        group_progress = QGroupBox("")
        group_progress.setLayout(layout_progress)

        group_layout = QHBoxLayout()
        group_layout.addWidget(group_qmk)
        group_layout.addWidget(group_stock)

        layout = QVBoxLayout()
        layout.addWidget(group_device, stretch=0)
        layout.addLayout(group_layout, stretch=1)
        layout.addWidget(group_progress, stretch=0)
        self.setLayout(layout)

        self.lockable = [btn_flash_qmk, btn_reboot_bl_evision, btn_reboot_bl_hfd, btn_flash_jumploader, btn_restore_stock,
                         self.combobox_devices, btn_refresh_devices]

        self.on_click_refresh()
        
        if cli_mode:
            self.on_click_flash_qmk()

    def lock_user(self):
        for obj in self.lockable:
            obj.setEnabled(False)

    def unlock_user(self):
        self.close_dev()
        for obj in self.lockable:
            obj.setEnabled(True)

    def close_dev(self):
        if self.dev is not None:
            self.dev.close()
            self.dev = None

    def _on_progress(self, args):
        msg, progress = args
        progress = int(progress * 100)
        self.progress.setValue(progress)
        self.progress_label.setText(msg)

    def _on_complete(self, args):
        self.progress.setValue(100)
        self.progress_label.setText("Finished")
        self.on_click_refresh()
        self.unlock_user()
        if cli_mode:
            sys.exit(0)

    def _on_error(self, msg):
        self.progress_label.setText("Failed")
        QMessageBox.critical(window, "Error", msg)
        self.unlock_user()

    def on_progress(self, msg, progress):
        self.progress_signal.emit([msg, progress])

    def on_complete(self):
        self.complete_signal.emit(None)

    def on_error(self, msg):
        self.error_signal.emit(msg)

    def on_toggle_offset(self, rbtn):
        if rbtn.isChecked() == True:
            if rbtn.text() == "0x200":
                self.qmk_offset = 0x200
            elif rbtn.text() == "0x00":
                self.qmk_offset = 0x00

    def on_toggle_device_type(self, rbtn):
        global MAX_FIRMWARE
        if rbtn.isChecked() == True:
            if rbtn.text() == "SN32F24x":
                MAX_FIRMWARE = MAX_FIRMWARE_SN32F240
            elif rbtn.text() == "SN32F26x":
                MAX_FIRMWARE = MAX_FIRMWARE_SN32F260

    def on_click_refresh(self):
        self.devices = []
        self.combobox_devices.clear()

        for dev in hid.enumerate():
            vid, pid = dev["vendor_id"], dev["product_id"]
            if (vid, pid) in self.device_descs and dev["interface_number"] <= 0:
                self.combobox_devices.addItem("{} [{:04X}:{:04X}]  {} {} ".format(
                    self.device_descs[(vid, pid)], vid, pid, dev["manufacturer_string"], dev["product_string"]))
                self.devices.append(dev)

                if cli_mode and vid == cli_vid and pid == cli_pid:                    
                    self.cli_dev = dev['path']
                    
                if pid == 0x7040 or pid == 0x7900:  # Sonix 248 and 248B
                    self.qmk_offset = 0x00
                    self.rbtn_qmk_offset_0.setChecked(True)
                    self.rbtn_qmk_offset_200.setChecked(False)
                    self.rbtn_device_type_260.setChecked(False)
                    self.rbtn_device_type_240.setChecked(True)

                if pid == 0x7010:  # Sonix 260
                    self.qmk_offset = 0x200
                    self.rbtn_qmk_offset_200.setChecked(True)
                    self.rbtn_qmk_offset_0.setChecked(False)
                    self.rbtn_device_type_240.setChecked(False)
                    self.rbtn_device_type_260.setChecked(True)
        
        if cli_mode:
            self.qmk_offset = cli_offset

    def get_active_device(self):
        idx = self.combobox_devices.currentIndex()
        if idx == -1:
            self._on_error("No device selected")
            return None

        try:
            dev = hid.device()
            if cli_mode:
                print(self.cli_dev)
                dev.open_path(self.cli_dev)
            else:
                dev.open_path(self.devices[idx]["path"])
            return dev
        except OSError:
            self._on_error(
                "Failed to open the device. You might not have sufficient permissions.")
            return None

    def sanity_check_qmk_firmware(self, firmware, offset=0):
        # check the size so we don't trash bootloader
        # (ok, we wouldn't overwrite it anyway as it's checked again in cmd_flash)
        if len(firmware) + offset > MAX_FIRMWARE:
            self._on_error("Firmware is too large: 0x{:X} max allowed is 0x{:X}".format(
                len(firmware), MAX_FIRMWARE-offset))
            return False
        if len(firmware) < 0x100:
            self._on_error("Firmware is too small")
            return False
        firmware_valid = True
        # check stack pointer is valid and that first 3 vectors have bit0 set
        sp, *vecs = struct.unpack("<IIII", firmware[0:16])
        if sp < 0x20000000 or sp > 0x20000800 or vecs[0] & 1 != 1 or vecs[1] & 1 != 1 or vecs[2] & 1 != 1:
            self._on_error("Firmware appears to be corrupted")
            return False
        return True

    def check_jumperloader_firmware(self, jumper_loader):
        # check the size so we don't trash bootloader
        # (ok, we wouldn't overwrite it anyway as it's checked again in cmd_flash)
        if len(jumper_loader) > QMK_OFFSET_DEFAULT:
            self._on_error("Jumper loader is too large: 0x{:X} max allowed is 0x{:X}".format(
                len(jumper_loader), MAX_FIRMWARE-QMK_OFFSET_DEFAULT))
            return False
        return True

    def on_click_flash_qmk(self):
        self.dev = self.get_active_device()
        if not self.dev:
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        if cli_mode:
            filename = cli_filename
        else:
            filename = QFileDialog.getOpenFileName(
                None, "Select firmware to flash", "", "Firmware Files (*.bin)", options=options)[0]
        if not filename:
            self.close_dev()
            return

        with open(filename, "rb") as inf:
            firmware = inf.read()

        if not self.sanity_check_qmk_firmware(firmware, self.qmk_offset):
            self.close_dev()
            return

        self.lock_user()
        threading.Thread(target=lambda: cmd_flash(self.dev, self.qmk_offset,
                                                  firmware, self.on_progress, self.on_complete, self.on_error)).start()

    def on_click_reboot_evision(self):
        self.dev = self.get_active_device()
        if not self.dev:
            return

        self.lock_user()
        threading.Thread(target=lambda: cmd_reboot_evision(
            self.dev, self.on_progress, self.on_complete, self.on_error)).start()

    def on_click_reboot_hfd(self):
        self.dev = self.get_active_device()
        if not self.dev:
            return

        self.lock_user()
        threading.Thread(target=lambda: cmd_reboot_hfd(
            self.dev, self.on_progress, self.on_complete, self.on_error)).start()

    def on_click_revert(self):
        reply = QMessageBox.question(self, "Warning", "This is a potentially dangerous operation. It does not check if your firmware is valid. Are you sure you want to continue?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.dev = self.get_active_device()
        if not self.dev:
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename = QFileDialog.getOpenFileName(
            None, "Select stock firmware to flash", "", "Stock Firmware (*.bin)", options=options)[0]
        if not filename:
            self.close_dev()
            return

        with open(filename, "rb") as inf:
            firmware = inf.read()

        self.lock_user()
        threading.Thread(target=lambda: cmd_flash(
            self.dev, 0, firmware, self.on_progress, self.on_complete, self.on_error, True)).start()


    def on_click_flash_jumploader(self):
        reply = QMessageBox.question(self, "Warning", "This is a potentially dangerous operation, are you sure you want to continue?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.dev = self.get_active_device()
        if not self.dev:
            return

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename = QFileDialog.getOpenFileName(
            None, "Select jumploader to flash", "", "Jumploader Files (*.bin)", options=options)[0]
        if not filename:
            self.close_dev()
            return

        with open(filename, "rb") as inf:
            firmware = inf.read()

        if not self.check_jumperloader_firmware(firmware):
            self.close_dev()
            return

        if len(firmware) < QMK_OFFSET_DEFAULT:
            firmware += b"\x00" * (QMK_OFFSET_DEFAULT - len(firmware))

        self.lock_user()
        threading.Thread(target=lambda: cmd_flash(
            self.dev, 0, firmware, self.on_progress, self.on_complete, self.on_error)).start()

    def on_download_click(self):
    	webbrowser.open("https://github.com/SonixQMK/Mechanical-Keyboard-Database", new=1, autoraise=True)


def excepthook(exc_type, exc_value, exc_tb):
    exc = traceback.format_exception(exc_type, exc_value, exc_tb)
    QMessageBox.critical(window, "Fatal error", "".join(exc))
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) == 5:
        cli_mode = True
        cli_vid = int(sys.argv[1], 16)
        cli_pid = int(sys.argv[2], 16)
        cli_offset = int(sys.argv[3], 16)
        cli_filename = sys.argv[4]
    else:
        cli_mode = False

    appctxt = ApplicationContext()
    window = MainWindow()
    window.resize(600, 500)
    if get_platform() == "Linux":
        if os.geteuid() == 0:
            window.setWindowTitle("Sonix Keyboard Flasher (ROOT)")
        else:
            window.setWindowTitle("Sonix Keyboard Flasher")
    else:
        window.setWindowTitle("Sonix Keyboard Flasher")
        
    window.show()
    sys.excepthook = excepthook
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
