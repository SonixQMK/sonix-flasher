# Sonix Flasher

## Usage

### Entering bootloader

You must boot into bootloader to flash the firmware，you have some choices to do it

- for stock firmware，click “Reboot to Bootloader” if your keyboard listed in the device list
- Pulled down the BOOT pin
- If you have a jumploader ，It’s strongly recommended to flash the jumploader on SN32F260 since the 260 series can become brick if the bootloader is overrided. [See](https://github.com/SonixQMK/sonix-keyboard-bootloader#entering-the-bootloader)

### Flash Firmware

- Set qmk_offset to 0x200 only if you have a jumploader flashed in the keyboard

## Compile

```
python3 -m venv venv
. venv/bin/activate
pip install wheel
pip install -r requirements.txt
fbs run
# or "fbs freeze" to create the package
```

Alternatively, if you're running NixOS or have Nix installed, you can run

```
nix shell
fbs run
```


To run it for immediate use, just run `run.sh` and it'll set itself up and run.

### UDEV

Run with sudo to flash unless you have the correct udev rules set up.

To setup the udev rule, run this command (tested for Berseker).

```bash
sudo bash -c 'cat << EOF > /etc/udev/rules.d/52-flash-keyboard.rules
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="7040", GROUP="users", MODE="0666"
EOF'
sudo systemctl restart udev
```

In order to check your bootloader's vendor & product IDs, run the following command, then immediately put your keyboard in bootloader mode, and wait for the diff.

```
lsusb > /tmp/pre; sleep 30; lsusb > /tmp/post; diff -u /tmp/pre /tmp/post
```

You should get something like this, look at the line starting with +.

```
[...]
-Bus 003 Device 016: ID 320f:5042 GG Berserker
+Bus 003 Device 017: ID 0c45:7040 Microdia
[...]
```
