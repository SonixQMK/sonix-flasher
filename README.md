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

Run with sudo to flash unless you have the correct udev rules set up.
