# private-home-tools
Private repository for development and backup of personal tools

## Commands used (Compiling and Signing Executables)
(Section used for both transparency and documenting useful commands)

- Compiling: `pyinstaller --onefile .\main.py -n pyprog.exe`
Compile `main.py` in `pyprog.exe` with no DLLs dependencies, all in the EXE file

- Signing: `signtool sign /fd SHA256 /f cert.pfx /p $Pass /tr http://timestamp.digicert.com /td SHA256 pyprog.exe`
Use `signtool` to `sign` `pyprog.exe` using `SHA256`, private key `cert.pfx`, PFX password `$Pass` (redacted), with timestamp provided by `timestap.digicert.com` and its digest algorithm `SHA256`

With PowerShell, it's easy to check if an EXE is signed with a certificate. Download `publicTrowerExec.cer` (check its SHA256 hash on publicTrowerExec.cer.hash) and run:
`Get-PfxCertificate .\pyprog.exe`
That Thumbprint must be the same as the one `Get-PfxCertificate .\publicTrowerExec.cer` shows.