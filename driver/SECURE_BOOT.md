# Secure Boot & Module Signing

`nitro_glyph` is an unsigned out-of-tree kernel module. If Secure Boot is
enabled, the kernel refuses to load unsigned modules — `insmod`/`modprobe`
will fail with `Key was rejected by service` (check `dmesg` to confirm).
`driver/install.sh` detects this automatically (via `mokutil --sb-state`)
and prints a warning before installing.

You have two options.

## Option 1: Disable Secure Boot (simplest)

Reboot into firmware setup (BIOS/UEFI) and turn Secure Boot off. No further
steps are needed — re-run `driver/install.sh` afterward.

## Option 2: Sign the module and enroll a MOK key

If DKMS is installed, most distros' `dkms` package (Fedora, Ubuntu, etc.)
already does this automatically on first build: it generates a local
signing key, signs the module, and prompts you to enroll it via MOK on
next boot. If that happens, skip to step 4.

Otherwise, do it manually:

1. Generate a signing key (one-time; keep `MOK.priv` outside version control):

   ```bash
   openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -outform DER \
       -out MOK.der -nodes -days 36500 -subj "/CN=nitro-glyph module signing key/"
   ```

2. Sign the built module:

   ```bash
   # Fedora
   sudo /usr/src/kernels/$(uname -r)/scripts/sign-file sha256 MOK.priv MOK.der nitro_glyph.ko

   # Debian/Ubuntu
   sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 MOK.priv MOK.der nitro_glyph.ko
   ```

3. Enroll the key with MOK:

   ```bash
   sudo mokutil --import MOK.der
   ```

   You'll be asked to set a temporary password — remember it, you need it
   in the next step.

4. Reboot. The blue "MOK Manager" screen appears before the OS loads —
   select **Enroll MOK**, enter the password from step 3, and confirm.

5. After the reboot completes, re-run `driver/install.sh`; the now-trusted
   module will load.
